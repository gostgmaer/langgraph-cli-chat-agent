from xml.parsers.expat import model

from core.database.models.session import SessionModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


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
        self._session.add(model)

        await self._session.commit()

        await self._session.refresh(model)

        return model

    async def get_by_id(self, session_id: str) -> SessionModel | None:
        statement = select(SessionModel).where(SessionModel.id == session_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def list_all(self)->list[SessionModel]:
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
