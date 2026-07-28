from sqlalchemy.ext.asyncio import AsyncSession

from core.database.repositories.session_repository import SessionRepository
from core.graph.checkpointer import Checkpointer
from core.graph.research.graph import ResearchGraphBuilder
from core.llm.manager import LLMManager
from config.enums import LLMProvider
from core.llm.models import SupportedModel
from core.memory.session import SessionManager
from services.chat_service import ChatService


async def create_chat_service(
    db_session: AsyncSession,
    checkpoint_manager: Checkpointer,
) -> ChatService:
    session_repository = SessionRepository(db_session)
    session_manager = SessionManager(session_repository)

    primary_llm = LLMManager()

    return ChatService(
        llm=primary_llm,
        session_manager=session_manager,
        checkpointer=checkpoint_manager.checkpointer,
        checkpoint_manager=checkpoint_manager,
    )


async def create_research_graph(checkpoint_manager: Checkpointer):
    return ResearchGraphBuilder(checkpointer=checkpoint_manager.checkpointer).build()
