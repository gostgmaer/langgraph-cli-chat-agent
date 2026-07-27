# ============================================================
# interfaces/cli/cli.py — Main CLI Application
# ============================================================
# TODO: Define the main CLI app (e.g., Typer or Click app)
# TODO: Register all CLI commands
# TODO: Handle startup / shutdown lifecycle
# ============================================================


from interfaces.cli.renderer import CLIRenderer
from services.chat_service import ChatService


class CLI:
    def __init__(
        self,
        chat_service: ChatService,
        renderer: CLIRenderer,
    ):
        self._chat_service = chat_service
        self._renderer = renderer
        self.console = renderer.console

    async def run(self) -> None:
        """Start the CLI application."""
        self._renderer.print_banner()
        self._renderer.print_system_message(
            "Tip: Type messages for Chat, '/research <topic>' for Multi-Agent Research, or '/graph' to render graph.png"
        )
        while True:
            try:
                self.console.print("\n[bold green]👤 You:[/bold green] ", end="")
                user_message = str(input().strip())
                if not user_message:
                    continue
                if user_message.lower() in ("exit", "quit", "close"):
                    self._renderer.print_system_message("Goodbye!")
                    break

                # Slash Command: Generate Master Graph PNG
                if user_message.lower() == "/graph":
                    try:
                        png_bytes = (
                            self._chat_service._graph.get_graph(xray=True).draw_mermaid_png()
                        )
                        with open("graph.png", "wb") as f:
                            f.write(png_bytes)
                        self._renderer.print_system_message(
                            "✅ Saved Master Graph diagram to 'graph.png'"
                        )
                    except Exception as e:
                        self._renderer.print_error(f"Could not render graph PNG: {e}")
                    continue

                # Execute all messages through the master graph
                self._renderer.start_assistant_message()
                async for token in self._chat_service.stream_chat(user_message):
                    self._renderer.stream_token(token)

                self._renderer.finish_assistant_message()
                self._renderer.separator()

            except KeyboardInterrupt:
                self._renderer.print_system_message("\nGoodbye 👋")
                break
            except Exception as error:
                self._renderer.print_error(str(error))
