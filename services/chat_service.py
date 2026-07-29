from collections.abc import AsyncGenerator
from typing import Any

from langchain.messages import HumanMessage
from langchain_core.messages import BaseMessage
from langgraph.types import Command

from core.database.repositories.session_repository import SessionRepository
from core.llm.manager import LLMManager

from core.memory.session import Session, SessionManager
from shared.logger import logger
from core.graph.graph import GraphBuilder


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
    ) -> AsyncGenerator[str, None]:

        if not user_message.strip():
            raise ValueError("Message cannot be empty.")

        config = await self._resolve_config()
        input_ = {"messages": [HumanMessage(content=user_message)]}
        async for token in self._stream_graph(input_, config):
            yield token

    async def resume_chat(
        self,
        resume_value: Any,
    ) -> AsyncGenerator[str, None]:
        """Resume a graph run paused at an interrupt() -- e.g. after the
        user approves/rejects/modifies a research plan -- and stream the
        continuation the same way stream_chat does."""
        config = await self._resolve_config()
        async for token in self._stream_graph(Command(resume=resume_value), config):
            yield token

    async def _stream_graph(
        self,
        input_: Any,
        config: dict,
    ) -> AsyncGenerator[str, None]:
        has_streamed = False
        async for event in self._graph.astream_events(
            input_,
            config=config,
            version="v2",
            subgraphs=True,  # Capture events from nested research_team subgraph
        ):
            if event["event"] == "on_chat_model_stream":
                node_name = event.get("metadata", {}).get("langgraph_node", "")
                if node_name not in ["chatbot", "writer_agent"]:
                    continue
                chunk = event["data"]["chunk"]
                if isinstance(chunk.content, str) and chunk.content:
                    has_streamed = True
                    yield chunk.content
                elif isinstance(chunk.content, list):
                    for block in chunk.content:
                        if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
                            has_streamed = True
                            yield block.get("text", "")

        if has_streamed:
            return

        current_state = await self._graph.aget_state(config)

        # The graph paused at an interrupt() (e.g. plan review) -- nothing
        # to stream yet. The caller checks get_pending_interrupt() instead.
        if current_state and any(t.interrupts for t in current_state.tasks):
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
                yield word + " "
                await asyncio.sleep(0.01)
        elif state_values.get("messages"):
            last_msg_content = getattr(state_values["messages"][-1], "content", "")
            if isinstance(last_msg_content, list):
                text = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in last_msg_content)
            else:
                text = str(last_msg_content)
            for word in text.split(" "):
                yield word + " "
                await asyncio.sleep(0.01)

    async def get_response(self, message: str) -> str:
        parts = []
        async for token in self.stream_chat(message):
            parts.append(token)
        return "".join(parts)
