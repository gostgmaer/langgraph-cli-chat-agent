from core.database.db import AsyncSessionLocal
from core.database.repositories.session_repository import SessionRepository
from core.llm.manager import llm
from core.memory.history import HistoryManager
from core.memory.session import SessionManager
from services.chat_service import ChatService


async def create_chat_service() -> ChatService:
    session = AsyncSessionLocal()
    session_repository = SessionRepository(session)
    session_manager = SessionManager(session_repository)
    history_manager = HistoryManager()
    return ChatService(
        llm=llm,
        session_manager=session_manager,
        history_manager=history_manager,
    )
