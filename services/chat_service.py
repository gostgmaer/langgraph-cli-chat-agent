# ============================================================
# services/chat_service.py — Chat Service
# ============================================================
# TODO: Coordinate between session, memory, agent, and LLM
# TODO: Accept user message and session_id
# TODO: Retrieve session + history, run agent, persist response
# TODO: Return final assistant message to caller
# ============================================================

from langchain_core.messages import BaseMessage

from core.llm.manager import LLMManager, llm
from shared.logger import logger
from core.llm.formatter import LLMResponseFormatter


class ChatService:

    def __init__(self, llm_manager: LLMManager) -> BaseMessage:
        self._llm = llm_manager

    def chat(self, user_message: str) -> BaseMessage:
        if not user_message.strip():
            raise ValueError("Message cannot be empty.")
        logger.info("Processing user message.")
        response = self._llm.invoke(input=user_message)
        logger.info("User message processed.")
        return response

    def get_response(self, user_message: str) -> str:
        """Get formatted text response."""
        response = self.chat(user_message)

        return LLMResponseFormatter.to_text(response)


chat_service = ChatService(llm)
