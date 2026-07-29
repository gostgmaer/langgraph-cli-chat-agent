from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any, Literal

from langchain.messages import HumanMessage
from langchain_core.messages import BaseMessage
from langgraph.graph import END
from langgraph.types import Command

from core.database.repositories.session_repository import SessionRepository
from core.llm.manager import LLMManager

from core.memory.session import Session, SessionManager
from shared.logger import logger
from core.graph.graph import GraphBuilder

# Friendly, human-readable label shown in the CLI whenever the graph enters
# one of these nodes -- lets the user see what the system is doing step by
# step, not just the final streamed answer.
STEP_LABELS: dict[str, str] = {
    "router": "🧭 Routing your message",
    "chatbot": "🤖 Thinking",
    "tools": "🛠️ Running tools",
    "research_team": "🧪 Starting research team",
    "supervisor": "🧠 Supervisor deciding next step",
    "planner_agent": "📝 Planning research sub-questions",
    "plan_review": "⏸️ Awaiting your plan review",
    "dispatch_search": "📤 Dispatching parallel searches",
    "search_agent": "🔍 Searching",
    "writer_agent": "✍️ Writing answer",
    "reviewer_agent": "🔎 Reviewing for accuracy",
}


@dataclass
class StreamChunk:
    """A single piece of a streamed graph run: a step announcement (a node
    started running), an assistant token to render, or the token-usage
    summary for the completed turn."""

    type: Literal["step", "token", "usage"]
    content: str


def _extract_usage(event: dict) -> dict | None:
    """Pull token usage off the AIMessage a chat-model call finished with,
    if the provider populated it (not all do, e.g. some Ollama models)."""
    output = event.get("data", {}).get("output")
    usage = getattr(output, "usage_metadata", None)
    if usage is None and isinstance(output, dict):
        usage = output.get("usage_metadata")
    return usage or None


def _format_usage(usage_totals: dict[str, int]) -> str:
    return (
        f"📊 Tokens — in: {usage_totals['input_tokens']:,} · "
        f"out: {usage_totals['output_tokens']:,} · "
        f"total: {usage_totals['total_tokens']:,}"
    )


class ChatService:
    """Coordinates the complete chat workflow using the GraphBuilder."""

    def __init__(
        self,
        llm: LLMManager,
        session_manager: SessionManager,
        checkpointer,
        checkpoint_manager,
    ) -> None:

        self._llm = llm
        self._session_manager = session_manager
        self._checkpoint_manager = checkpoint_manager
        self._checkpointer = checkpointer
        self._graph = GraphBuilder(llm, checkpointer=checkpointer).build()

    async def chat(self, user_message: str) -> BaseMessage:
        """Process a user message and return the assistant response."""
        if not user_message.strip():
            raise ValueError("Message cannot be empty.")

        session = await self._session_manager.get_or_create()
        logger.debug("Using session %s", session.id)

        messages = [HumanMessage(content=user_message)]

        state = await self._graph.ainvoke(
            {"messages": messages},
            config={"configurable": {"thread_id": str(session.id)}},
        )
        for msg in state["messages"]:
            logger.debug(
                "%s -> %s",
                type(msg).__name__,
                getattr(msg, "content", ""),
            )
        return state["messages"][-1]

    async def _resolve_config(self) -> dict:
        session = await self._session_manager.get_or_create()
        return {"configurable": {"thread_id": str(session.id)}}

    async def get_history(self) -> list[BaseMessage]:
        """Return the message history for the current session's thread."""
        config = await self._resolve_config()
        state = await self._graph.aget_state(config)
        if not state:
            return []
        return state.values.get("messages", [])

    async def new_session(self) -> Session:
        """Start a fresh session, giving the graph a new thread_id so the
        assistant no longer sees prior conversation turns."""
        return await self._session_manager.create_session()

    async def get_pending_interrupt(self) -> dict | None:
        """Return the payload of an interrupt() the graph is currently
        paused at for this session's thread (e.g. a research plan awaiting
        approval), or None if the graph isn't paused."""
        config = await self._resolve_config()
        state = await self._graph.aget_state(config)
        if not state:
            return None
        for task in state.tasks:
            if task.interrupts:
                return task.interrupts[0].value
        return None

    async def stream_chat(
        self,
        user_message: str,
    ) -> AsyncGenerator[StreamChunk, None]:

        if not user_message.strip():
            raise ValueError("Message cannot be empty.")

        config = await self._resolve_config()
        input_ = {"messages": [HumanMessage(content=user_message)]}
        async for chunk in self._stream_graph(input_, config):
            yield chunk

    async def resume_chat(
        self,
        resume_value: Any,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Resume a graph run paused at an interrupt() -- e.g. after the
        user approves/rejects/modifies a research plan -- and stream the
        continuation the same way stream_chat does."""
        config = await self._resolve_config()
        async for chunk in self._stream_graph(Command(resume=resume_value), config):
            yield chunk

    async def _stream_graph(
        self,
        input_: Any,
        config: dict,
    ) -> AsyncGenerator[StreamChunk, None]:
        has_streamed = False
        announced_run_ids: set[str] = set()
        announced_end_ids: set[str] = set()
        usage_totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

        async for event in self._graph.astream_events(
            input_,
            config=config,
            version="v2",
            subgraphs=True,  # Capture events from nested research_team subgraph
        ):
            node_name = event.get("metadata", {}).get("langgraph_node", "")

            # A node just started -- announce it so the user can see what
            # the system is doing, not just the final streamed answer.
            if (
                event["event"] == "on_chain_start"
                and node_name in STEP_LABELS
                and event.get("name") == node_name
                and event.get("run_id") not in announced_run_ids
            ):
                announced_run_ids.add(event.get("run_id"))
                label = STEP_LABELS[node_name]
                if node_name == "search_agent":
                    question = (event.get("data", {}).get("input") or {}).get("question")
                    if question:
                        label = f"{label}: {question}"
                yield StreamChunk(type="step", content=label)

            # Disambiguate what "writing"/"reviewing" actually produced --
            # otherwise a reviewed, finalized answer looks identical to an
            # in-progress draft, since both just stream from writer_agent.
            if (
                event["event"] == "on_chain_end"
                and event.get("name") == node_name
                and event.get("run_id") not in announced_end_ids
            ):
                output = event.get("data", {}).get("output")
                goto = getattr(output, "goto", None)
                update = getattr(output, "update", None) or {}
                if node_name == "reviewer_agent" and goto == "writer_agent":
                    announced_end_ids.add(event.get("run_id"))
                    yield StreamChunk(
                        type="step", content="🔁 Sending draft back for revision"
                    )
                elif node_name == "supervisor" and goto == END and isinstance(update, dict) and update.get("final_answer"):
                    announced_end_ids.add(event.get("run_id"))
                    yield StreamChunk(type="step", content="✅ Final answer ready")

            if event["event"] == "on_chat_model_end":
                usage = _extract_usage(event)
                if usage:
                    usage_totals["input_tokens"] += usage.get("input_tokens") or 0
                    usage_totals["output_tokens"] += usage.get("output_tokens") or 0
                    usage_totals["total_tokens"] += usage.get("total_tokens") or 0

            if event["event"] == "on_chat_model_stream":
                if node_name not in ["chatbot", "writer_agent"]:
                    continue
                chunk = event["data"]["chunk"]
                if isinstance(chunk.content, str) and chunk.content:
                    has_streamed = True
                    yield StreamChunk(type="token", content=chunk.content)
                elif isinstance(chunk.content, list):
                    for block in chunk.content:
                        if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
                            has_streamed = True
                            yield StreamChunk(type="token", content=block.get("text", ""))

        def _usage_chunk() -> StreamChunk | None:
            if not any(usage_totals.values()):
                return None
            return StreamChunk(type="usage", content=_format_usage(usage_totals))

        if has_streamed:
            usage_chunk = _usage_chunk()
            if usage_chunk:
                yield usage_chunk
            return

        current_state = await self._graph.aget_state(config)

        # The graph paused at an interrupt() (e.g. plan review) -- nothing
        # to stream yet. The caller checks get_pending_interrupt() instead.
        if current_state and any(t.interrupts for t in current_state.tasks):
            usage_chunk = _usage_chunk()
            if usage_chunk:
                yield usage_chunk
            return

        # Fallback: research subgraph completed but writer used ainvoke (no stream events)
        import asyncio
        state_values = current_state.values if current_state else {}
        final_ans = state_values.get("final_answer")
        if final_ans:
            if isinstance(final_ans, list):
                text = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in final_ans)
            else:
                text = str(final_ans)
            # Word-by-word fake streaming so output feels progressive
            for word in text.split(" "):
                yield StreamChunk(type="token", content=word + " ")
                await asyncio.sleep(0.01)
        elif state_values.get("messages"):
            last_msg_content = getattr(state_values["messages"][-1], "content", "")
            if isinstance(last_msg_content, list):
                text = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in last_msg_content)
            else:
                text = str(last_msg_content)
            for word in text.split(" "):
                yield StreamChunk(type="token", content=word + " ")
                await asyncio.sleep(0.01)

        usage_chunk = _usage_chunk()
        if usage_chunk:
            yield usage_chunk

    async def get_response(self, message: str) -> str:
        parts = []
        async for chunk in self.stream_chat(message):
            if chunk.type == "token":
                parts.append(chunk.content)
        return "".join(parts)
