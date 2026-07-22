# ============================================================
# core/memory/session.py — Session Management
# ============================================================
# TODO: Create a new session with unique session_id
# TODO: Load an existing session by ID
# TODO: List all active sessions
# TODO: Delete / archive a session
# TODO: Track session metadata (created_at, last_active, model)
# ============================================================


from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4
from core.database.models.session import SessionModel
from core.database.repositories.session_repository import SessionRepository
from shared.logger import logger


@dataclass
class Session:
    """Represents a chat session."""

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class SessionManager:
    def __init__(
        self,
        repository: SessionRepository,
    ):

        self._current_session_id: str | None = None
        self._repository = repository

    async def get_or_create(self) -> Session:
        if self._current_session_id:
            return await self.get_session(self._current_session_id)
            
        model = await self._repository.get_active_session()

        if model:
            self._current_session_id = model.id
            return self._to_domain(model)

        return await self.create_session()

    async def create_session(self, title: str = "New Chat") -> Session:
        session_id = str(uuid4())
        self._current_session_id = session_id

        now = datetime.now(UTC)
        session = Session(
            id=session_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        saved_model = await self._repository.save(self._to_model(session))

        return self._to_domain(saved_model)
        # self._sessions[session_id] = session
        logger.debug("Created session %s", session.id)
        return session

    async def get_session(self, session_id: str) -> Session:
        model = await self._repository.get_by_id(session_id)

        if model is None:
            raise ValueError("Session not found")

        session = self._to_domain(model)

        logger.debug("Retrieved session %s", session.id)

        return session

    async def get_current_session(self) -> Session | None:
        if self._current_session_id is None:
            return None
        return await self.get_session(self._current_session_id)

    async def list_sessions(self) -> list[Session]:
        models = await self._repository.list_all()

        return [self._to_domain(model) for model in models]

    async def switch_session(self, session_id: str) -> None:
        await self.get_session(session_id)

        self._current_session_id = session_id

        logger.debug("Switched session %s", session_id)

    async def delete_session(self, session_id: str) -> None:
        model = await self._repository.get_by_id(session_id)

        if model is None:
            raise ValueError("Session not found")

        await self._repository.delete(model)

        if self._current_session_id == session_id:
            self._current_session_id = None

        logger.debug("Deleted session %s", session_id)

    def _to_model(
        self,
        session: Session,
    ) -> SessionModel:
        return SessionModel(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    def _to_domain(
        self,
        model: SessionModel,
    ) -> Session:
        return Session(
            id=model.id,
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
