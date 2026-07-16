import asyncio

from config.settings import settings
from core.bootstrap import create_chat_service
from core.database.db import AsyncSessionLocal, init_database
from core.graph.checkpointer import Checkpointer

from interfaces.cli.cli import CLI
from interfaces.cli.renderer import renderer


async def main() -> None:
    await init_database()

    async with AsyncSessionLocal() as db_session:

        checkpoint_manager = Checkpointer(
            settings.sqlite_checkpoint_db
        )

        await checkpoint_manager.initialize()

        try:
            chat_service = await create_chat_service(
                db_session=db_session,
                checkpoint_manager=checkpoint_manager,
            )

            cli = CLI(
                chat_service=chat_service,
                renderer=renderer,
            )

            await cli.run()

        finally:
            await checkpoint_manager.close()


if __name__ == "__main__":
    asyncio.run(main())