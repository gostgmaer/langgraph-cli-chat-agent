from sqlalchemy.ext.asyncio import AsyncSession

from core.database.repositories.session_repository import SessionRepository
from core.graph.checkpointer import Checkpointer
from core.llm.manager import llm
from core.memory.session import SessionManager
from services.chat_service import ChatService


async def create_chat_service(
    db_session: AsyncSession,
    checkpoint_manager: Checkpointer,
) -> ChatService:
    session_repository = SessionRepository(db_session)
    session_manager = SessionManager(session_repository)

    return ChatService(
        llm=llm,
        session_manager=session_manager,
        checkpointer=checkpoint_manager.checkpointer,
        checkpoint_manager=checkpoint_manager,
    )