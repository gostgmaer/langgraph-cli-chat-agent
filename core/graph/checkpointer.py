from contextlib import AbstractAsyncContextManager

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


class Checkpointer:
    """Manages the lifecycle of the LangGraph SQLite checkpointer."""

    def __init__(self, database_url: str):
        self._database_url = database_url

        self._context: (
            AbstractAsyncContextManager[AsyncSqliteSaver] | None
        ) = None

        self._checkpointer: AsyncSqliteSaver | None = None

    async def initialize(self) -> None:
        """Initialize the checkpointer."""

        if self._checkpointer is not None:
            return

        self._context = AsyncSqliteSaver.from_conn_string(
            self._database_url
        )

        self._checkpointer = await self._context.__aenter__()

        await self._checkpointer.setup()

    async def close(self) -> None:
        """Close the SQLite connection."""

        if self._context is not None:
            await self._context.__aexit__(None, None, None)

    @property
    def checkpointer(self) -> AsyncSqliteSaver:
        if self._checkpointer is None:
            raise RuntimeError(
                "Checkpointer has not been initialized."
            )

        return self._checkpointer