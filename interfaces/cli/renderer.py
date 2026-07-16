# ============================================================
# interfaces/cli/renderer.py — Terminal Rendering
# ============================================================
# TODO: Render assistant messages with Rich formatting
# TODO: Render user messages
# TODO: Render tool call panels / spinners
# TODO: Render error messages
# TODO: Render session info / metadata panels
# TODO: Render markdown inside chat bubbles
# ============================================================


from rich.text import Text
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from config.settings import settings

class CLIRenderer:
    """Handles all terminal rendering."""
    def __init__(self):
        self.console = Console()

    def print_banner(self)->None:
         
         """Display application banner."""
         title = Text(f"{settings.app_name} v{settings.app_version}",justify="center",style="bold blue")
         self.console.print(
            Panel(
                title,
                subtitle=f"{settings.llm_provider.value} • {settings.llm_model}",
                expand=False,
            )
        )

    def print_user_message(self,message: str)->None:
        """Display a user message."""
        self.console.print(f"[bold green]User:[/bold green] {message}")

    def print_assistant_message(self,message: str)->None:
        """Display an assistant message."""
        self.console.print(f"[bold blue]Assistant:[/bold blue] {message}")
        self.console.print(Markdown(message))
        self.console.print()

    def print_system_message(self,message: str)->None:
        """Display a system message."""
        self.console.print(f"[bold yellow]System:[/bold yellow] {message}")
        

    def print_error(self,message: str)->None:
        """Display an error message."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")

    def print_separator(self) -> None:
        """Print separator."""

        self.console.rule()

    def clear(self) -> None:
        """Clear terminal."""

        self.console.clear()


renderer = CLIRenderer()