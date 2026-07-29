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


async def create_research_graph(llm: LLMManager, checkpoint_manager: Checkpointer):
    return ResearchGraphBuilder(llm=llm, checkpointer=checkpoint_manager.checkpointer).build()


def render_startup_diagrams(chat_service: ChatService) -> list[tuple[str, Exception | None]]:
    """Render the master graph and Research Team subgraph diagrams to PNG
    files at startup, so they're always available without a manual command.
    Failures (e.g. no network access to the mermaid.ink render API) are
    collected rather than raised, so a render failure doesn't block CLI
    startup."""
    results: list[tuple[str, Exception | None]] = []

    try:
        png_bytes = chat_service._graph.get_graph(xray=True).draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_bytes)
        results.append(("graph.png", None))
    except Exception as e:
        results.append(("graph.png", e))

    try:
        # Reuse the ChatService's already-connected LLMManager -- building a
        # fresh one here would open a second, redundant provider connection.
        research_graph = ResearchGraphBuilder(llm=chat_service._llm).build()
        png_bytes = research_graph.get_graph(xray=True).draw_mermaid_png()
        with open("research_graph.png", "wb") as f:
            f.write(png_bytes)
        results.append(("research_graph.png", None))
    except Exception as e:
        results.append(("research_graph.png", e))

    return results
