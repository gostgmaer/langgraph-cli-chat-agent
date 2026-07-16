# ============================================================
# app.py — CLI Entry Point
# ============================================================
# TODO: Initialize the CLI application
# TODO: Parse arguments / commands
# TODO: Bootstrap config, logger, and services
# TODO: Launch the chat loop or dispatch subcommands
# ============================================================


from interfaces.cli.cli import CLI
from interfaces.cli.renderer import renderer
from services.chat_service import chat_service


def main() -> None:
    cli = CLI(chat_service, renderer)
    cli.run()


if __name__ == "__main__":
    main()