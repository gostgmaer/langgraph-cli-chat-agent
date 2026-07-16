# ============================================================
# services/chat_service.py — Chat Service
# ============================================================
# TODO: Coordinate between session, memory, agent, and LLM
# TODO: Accept user message and session_id
# TODO: Retrieve session + history, run agent, persist response
# TODO: Return final assistant message to caller
# ============================================================

from langchain_core.messages import BaseMessage

from core.llm.manager import LLMManager,llm
from shared.logger import logger


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



chat_service = ChatService(llm)