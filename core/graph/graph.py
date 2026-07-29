from typing import Annotated, Any, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.base import BaseCheckpointSaver

from core.graph.nodes import create_chatbot_node
from core.graph.research.graph import ResearchGraphBuilder
from core.llm.manager import LLMManager
from core.tools.news import get_news
from core.tools.search import get_google_search
from core.tools.weather import get_weather
from core.tools.preferences import save_preference
from core.graph.state import update_preferences


def _replace_list(left: list, right: list) -> list:
    """Replace reducer — new value fully replaces old (not append)."""
    return right if right is not None else left


class State(TypedDict, total=False):
    """Unified state schema combining Chat and Multi-Agent Research."""
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    question: str
    sub_questions: Annotated[list[str], _replace_list]
    search_results: Annotated[list[str], _replace_list]
    revision_count: int
    draft: str
    final_answer: str
    user_preferences: Annotated[dict[str, Any], update_preferences]


def router_node(state: State) -> dict:
    """Classifies user input into standard chatbot vs research team."""
    if not state.get("messages"):
        return {"intent": "chat"}
    
    last_msg = state["messages"][-1]
    content = getattr(last_msg, "content", "")
    
    if isinstance(content, list):
        # Extract text from list of blocks (e.g. Gemini / Anthropic block structure)
        text_parts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in content]
        text_content = "".join(text_parts).strip()
    else:
        text_content = str(content).strip()

    if text_content.startswith("/research "):
        raw_topic = text_content[len("/research "):].strip()
        topic = _resolve_research_topic(raw_topic, state)
        return {
            "intent": "research",
            "question": topic,
            # Hard-reset ALL research fields to prevent stale checkpoint state
            "sub_questions": [],
            "search_results": [],
            "draft": "",
            "revision_count": 0,
            "final_answer": "",
        }
    return {"intent": "chat"}


_CONTINUE_PREFIXES = ("continue", "follow up", "follow-up")


def _matches_continue_prefix(lowered_topic: str, prefix: str) -> bool:
    """True only if `prefix` is a whole leading word/phrase, not just a
    string prefix -- otherwise "continued fractions" would match "continue"."""
    if not lowered_topic.startswith(prefix):
        return False
    rest = lowered_topic[len(prefix):]
    return rest == "" or not rest[0].isalnum()


def _resolve_research_topic(raw_topic: str, state: State) -> str:
    """'/research continue [focus]' builds on the previous research in this
    thread instead of treating "continue" as a literal new topic -- reads
    the prior question/final_answer from state (still the previous run's
    values here, since this node's own update hasn't been applied yet)."""
    lowered = raw_topic.lower()
    matched_prefix = next(
        (p for p in _CONTINUE_PREFIXES if _matches_continue_prefix(lowered, p)), None
    )
    if matched_prefix is None:
        return raw_topic

    prev_question = state.get("question", "")
    prev_answer = state.get("final_answer", "")
    if not prev_answer:
        # Nothing to continue from yet -- fall back to the literal topic.
        return raw_topic

    extra_focus = raw_topic[len(matched_prefix):].strip(" :,-")
    follow_up_instruction = (
        f"Focus the follow-up research specifically on: {extra_focus}"
        if extra_focus
        else "Identify gaps, open questions, or under-explored angles in the "
        "previous findings and research those further."
    )
    return (
        f"Continue and deepen the previous research on: {prev_question}\n\n"
        f"Previous findings:\n{prev_answer}\n\n"
        f"{follow_up_instruction}"
    )


def route_decision(state: State) -> Literal["chatbot", "research_team"]:
    if state.get("intent") == "research":
        return "research_team"
    return "chatbot"


class GraphBuilder:
    """Builds a single master graph combining Router, Chatbot, Tools, and Research Subgraph."""

    def __init__(self, llm: LLMManager, checkpointer: BaseCheckpointSaver = None):
        self._llm = llm
        self._checkpointer = checkpointer

    def build(self):
        # 1. Subgraph: Research Team (reuses the same LLMManager instance --
        # no separate provider connection for the research agents)
        research_team_subgraph = ResearchGraphBuilder(llm=self._llm).build()

        # 2. Parent Graph
        builder = StateGraph(State)

        # 3. Add Nodes
        tools = [get_weather, get_google_search, get_news, save_preference]
        builder.add_node("router", router_node)
        builder.add_node("chatbot", create_chatbot_node(self._llm, tools))
        builder.add_node("tools", ToolNode(tools))
        builder.add_node("research_team", research_team_subgraph)

        # 4. Add Edges & Conditional Routing
        builder.add_edge(START, "router")
        builder.add_conditional_edges("router", route_decision)

        # Single-Agent Chat Branch
        builder.add_conditional_edges("chatbot", tools_condition)
        builder.add_edge("tools", "chatbot")

        # Multi-Agent Research Subgraph Branch
        builder.add_edge("research_team", END)

        if self._checkpointer:
            return builder.compile(checkpointer=self._checkpointer)
        return builder.compile()
