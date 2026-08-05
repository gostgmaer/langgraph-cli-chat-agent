from langchain_core.messages import AIMessage, SystemMessage, trim_messages
from langchain_core.tools import BaseTool
from shared.logger import logger
from core.graph.state import GraphState
from core.llm.manager import LLMManager
from utils.retries import async_retry

# Cap how much prior conversation gets resent to the LLM each turn. The
# checkpointer persists the full thread indefinitely (including across CLI
# restarts, since sessions are reused until /new is run), so without this
# every turn's input tokens grow with the *entire* lifetime of the thread.
HISTORY_MESSAGE_LIMIT = 20  # ~10 human/assistant turns


def _flatten_content(content) -> str:
    """Normalise list-of-blocks (Gemini / Anthropic) to a plain string."""
    if isinstance(content, list):
        return "".join(
            b.get("text", "") if isinstance(b, dict) else str(b) for b in content
        )
    return str(content)


def _build_history(messages, preferences: dict) -> list:
    """Build the message list for the LLM, with a system prompt prepended
    and research-agent messages stripped out."""
    sys_msg = SystemMessage(
        content=(
            "You are a helpful, knowledgeable assistant in a CLI chat app.\n\n"
            "RULES:\n"
            "1. For greetings, small talk, or questions you can answer from your "
            "own knowledge — reply DIRECTLY. Do NOT call any tool.\n"
            "2. Only call a tool when the user's request genuinely requires "
            "live/external data:\n"
            "   - get_weather      → current weather for a city\n"
            "   - web_search       → search the web via DuckDuckGo\n"
            "   - get_google_search → Google search\n"
            "   - get_news         → recent news on a topic\n"
            "   - save_preference  → remember something the user tells you about "
            "themselves (name, language, diet, etc.)\n"
            "3. Call at most ONE tool per turn. Never call the same tool twice.\n"
            "4. For deep research questions suggest the '/research <topic>' command.\n\n"
            f"Remembered user preferences: {preferences}."
        )
    )

    filtered = []
    for m in messages:
        name = m.get("name") if isinstance(m, dict) else getattr(m, "name", None)
        if name == "writer_agent":
            continue
        if hasattr(m, "content") and isinstance(m.content, list):
            filtered.append(type(m)(content=_flatten_content(m.content)))
        elif isinstance(m, dict) and isinstance(m.get("content"), list):
            filtered.append({**m, "content": _flatten_content(m["content"])})
        else:
            filtered.append(m)

    # token_counter=len makes max_tokens act as a message-count budget
    # instead of an actual token budget -- simple and cheap.
    trimmed = trim_messages(
        filtered,
        max_tokens=HISTORY_MESSAGE_LIMIT,
        token_counter=len,
        strategy="last",
        start_on="human",
    )
    return [sys_msg] + trimmed


def create_chatbot_node(llm: LLMManager, tools: list[BaseTool]):
    """First-pass chatbot node: may call tools.
    Routes to 'tools' if the LLM emits tool_calls, otherwise to END."""
    tool_enabled_llm = llm.bind_tools(tools)
    plain_llm = llm.model  # no tools bound — used for conversational replies

    async def chatbot_node(state: GraphState):
        messages = state["messages"]
        preferences = state.get("user_preferences", {})

        # ── Fast intent check ─────────────────────────────────────────────────
        # Classify the last user message with a tiny prompt — no tool schemas,
        # no history. Saves ~1,500-2,000 tokens for every conversational turn.
        last_user_text = ""
        for m in reversed(messages):
            if getattr(m, "type", None) == "human" or (
                isinstance(m, dict) and m.get("type") == "human"
            ):
                raw = m.content if not isinstance(m, dict) else m.get("content", "")
                last_user_text = _flatten_content(raw) if isinstance(raw, list) else str(raw)
                break

        needs_tools = True  # default safe
        if last_user_text:
            from langchain_core.messages import HumanMessage
            classifier_msg = HumanMessage(
                content=(
                    "Classify the following message. Reply with exactly one word:\n"
                    "- TOOLS if it requires live external data (weather, web search, "
                    "news, or saving a preference)\n"
                    "- CHAT if it can be answered directly from knowledge "
                    "(greetings, general questions, explanations, etc.)\n\n"
                    f"Message: {last_user_text}"
                )
            )
            try:
                verdict = await plain_llm.ainvoke(
                    [classifier_msg],
                    config={"run_name": "intent_classifier"},
                )
                verdict_text = _flatten_content(verdict.content).strip().upper()
                needs_tools = verdict_text.startswith("TOOLS")
                logger.debug("Intent classifier: %r → needs_tools=%s", verdict_text, needs_tools)
            except Exception:
                logger.warning("Intent classifier failed — defaulting to tool-enabled path.")

        history = _build_history(messages, preferences)

        if needs_tools:
            response = await async_retry(tool_enabled_llm.ainvoke, history)
        else:
            response = await async_retry(plain_llm.ainvoke, history)

        logger.debug("Chatbot | content: %s", response.content)
        logger.debug("Chatbot | tool_calls: %s", getattr(response, "tool_calls", []))

        state_update: dict = {"messages": [response]}

        # Eagerly persist save_preference calls so state is updated
        # even before the finalise node runs.
        for tc in (getattr(response, "tool_calls", None) or []):
            if tc["name"] == "save_preference":
                key = tc["args"].get("key", "")
                val = tc["args"].get("value", "")
                if key:
                    state_update.setdefault("user_preferences", {})[key] = val

        return state_update

    return chatbot_node


def create_finalise_node(llm: LLMManager):
    """Second-pass node: plain LLM with NO tools bound.
    Runs after ToolNode so the model is forced to produce a final text
    answer — it physically cannot emit another tool_call, breaking the loop."""

    async def finalise_node(state: GraphState):
        messages = state["messages"]
        preferences = state.get("user_preferences", {})
        history = _build_history(messages, preferences)

        # Plain LLM — no tools → guaranteed text response, no looping
        response = await async_retry(llm.ainvoke, history)
        logger.debug("Finalise | content: %s", response.content)
        return {"messages": [AIMessage(content=_flatten_content(response.content))]}

    return finalise_node


def create_refiner_node(llm: LLMManager):
    async def refiner_node(state: GraphState):
        messages = state["messages"]

        system_prompt = SystemMessage(
            content=(
                "You are an expert assistant and editor. Based on the conversation "
                "history and any tool results, provide a clear, accurate, and highly "
                "polished final answer. Do not repeat words endlessly. "
                "Stop when your thought is complete."
            )
        )

        response = await async_retry(llm.ainvoke, [system_prompt] + messages)
        logger.debug("Refined content: %s", response.content)
        return {"messages": [AIMessage(content=response.content, name="refiner")]}

    return refiner_node
