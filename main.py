import asyncio
import os

from config.settings import settings
from core.bootstrap import create_chat_service, render_startup_diagrams
from core.database.db import AsyncSessionLocal, init_database
from core.graph.checkpointer import Checkpointer

from interfaces.cli.cli import CLI
from interfaces.cli.renderer import CLIRenderer
from shared.logger import logger


def _configure_tracing() -> None:
    """LangChain/LangSmith tracing activates by reading os.environ directly
    -- so tracing never actually turns on regardless of config."""
    if not settings.langchain_tracing:
        return
    if not settings.langchain_api_key:
        logger.warning(
            "LANGCHAIN_TRACING_V2 is enabled but LANGCHAIN_API_KEY is missing -- "
            "tracing will not be activated."
        )
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    logger.info("LangSmith tracing enabled for project '%s'.", settings.langchain_project)


async def main() -> None:
    _configure_tracing()

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

            renderer = CLIRenderer()
            for name, error in render_startup_diagrams(chat_service):
                if error:
                    renderer.print_error(f"Could not render {name}: {error}")
                else:
                    renderer.print_system_message(f"✅ Saved diagram to '{name}'")

            cli = CLI(
                chat_service=chat_service,
                renderer=renderer,
            )

            await cli.run()

        finally:
            await checkpoint_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
