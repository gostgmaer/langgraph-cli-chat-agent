
from core.database.models.session import SessionModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database.models.session import SessionModel


class SessionRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def save(
        self,
        session: SessionModel,
    ) -> SessionModel:
        self._session.add(session)

        await self._session.commit()

        await self._session.refresh(session)

        return session

    async def get_by_id(self, session_id: str) -> SessionModel | None:
        statement = select(SessionModel).where(SessionModel.id == session_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[SessionModel]:
        statement = select(SessionModel)
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def update(self, session: SessionModel) -> SessionModel:
        await self._session.commit()
        await self._session.refresh(session)
        return session

    async def delete(self, session: SessionModel) -> None:
        await self._session.delete(session)
        await self._session.commit()

    async def get_active_session(self) -> SessionModel | None:
        stmt = (
            select(SessionModel)
            .where(SessionModel.is_active == True)
            .order_by(SessionModel.updated_at.desc())
            .limit(1)
        )

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()
