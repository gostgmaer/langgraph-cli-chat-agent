# ============================================================
# app.py — CLI Entry Point
# ============================================================
# TODO: Initialize the CLI application
# TODO: Parse arguments / commands
# TODO: Bootstrap config, logger, and services
# TODO: Launch the chat loop or dispatch subcommands
# ============================================================


import asyncio

from core.bootstrap import create_chat_service
from core.database.db import init_database
from interfaces.cli.cli import CLI
from interfaces.cli.renderer import renderer


async def main() -> None:
    await init_database()
    chat_service = await create_chat_service()

    cli = CLI(
        chat_service=chat_service,
        renderer=renderer,
    )

    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())