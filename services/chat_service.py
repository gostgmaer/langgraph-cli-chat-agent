# ============================================================
# services/chat_service.py — Chat Service
# ============================================================
# TODO: Coordinate between session, memory, agent, and LLM
# TODO: Accept user message and session_id
# TODO: Retrieve session + history, run agent, persist response
# TODO: Return final assistant message to caller
# ============================================================

from langchain_core.messages import BaseMessage

from core.llm.formatter import LLMResponseFormatter
from core.llm.manager import LLMManager, llm
from core.memory.history import HistoryManager
from core.memory.session import SessionManager
from shared.logger import logger


class ChatService:
    """Coordinates the complete chat workflow."""

    def __init__(
        self,
        llm,
        session_manager,
        history_manager,
    ) -> None:
        self._llm = llm
        self._session_manager = session_manager
        self._history_manager = history_manager

    async def chat(self, user_message: str) -> BaseMessage:
        """Process a user message and return the assistant response."""

        # 1. Validate input
        if not user_message.strip():
            raise ValueError("Message cannot be empty.")

        # 2. Get or create current session
        session = self._session_manager.get_current_session()

        if session is None:
            session = self._session_manager.create_session()

        logger.info("Using session %s", session.id)

        # 3. Save user message
        self._history_manager.add_user_message(
            session.id,
            user_message,
        )

        # 4. Load conversation history
        messages = self._history_manager.get_messages(session.id)

        logger.info(
            "Sending %d messages to LLM.",
            len(messages),
        )

        # Debug (remove later)
        # for message in messages:
        #     print(type(message).__name__, ":", message.content)

        # 5. Invoke LLM
        logger.info("Processing user message...")
        response = await self._llm.ainvoke(messages)

        # 6. Save assistant response
        self._history_manager.add_ai_message(
            session.id,
            response.content,
        )

        self._history_manager.trim_history(
            session.id,
            max_messages=20,
        )

        logger.info("Assistant response saved.")

        # 7. Return response
        return response

    def get_response(self, user_message: str) -> str:
        """Return formatted assistant text."""

        response = self.chat(user_message)
        return LLMResponseFormatter.to_text(response)


chat_service = ChatService(
    llm=llm,
    session_manager=SessionManager(),
    history_manager=HistoryManager(),
)
