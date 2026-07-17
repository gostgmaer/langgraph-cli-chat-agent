from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule
from rich.status import Status
from rich.live import Live
from rich import print

from config.settings import settings


class CLIRenderer:
    """Rich terminal renderer (Classic CLI Style)."""

    def __init__(self) -> None:
        self.console = Console()
        self._stream_buffer = ""
        self._live = None

    # ------------------------------------------------------------------
    # Banner
    # ------------------------------------------------------------------

    def print_banner(self) -> None:
        self.console.print()
        # Proper, clean heading without heavy boxes
        self.console.print(f"[bold cyan]{settings.app_name}[/bold cyan]", justify="center")
        self.console.print(
            f"[dim]Version {settings.app_version} • {settings.llm_provider.value.upper()} • {settings.llm_model}[/dim]",
            justify="center"
        )
        self.console.print(Rule(style="cyan"))

    # ------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------

    def print_user_message(
        self,
        message: str,
    ) -> None:
        self.console.print("\n[bold green]👤 You:[/bold green]")
        self.console.print(message)

    # ------------------------------------------------------------------
    # Assistant
    # ------------------------------------------------------------------

    def print_assistant_message(
        self,
        message: str,
    ) -> None:
        self.console.print("\n[bold blue]🤖 Assistant:[/bold blue]")
        self.console.print(Markdown(message))

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    def start_assistant_message(self):
        self.console.print("\n[bold blue]🤖 Assistant:[/bold blue]")
        self._stream_buffer = ""
        
        # Stream markdown directly without wrapping it in a Panel
        self._live = Live(
            Markdown(self._stream_buffer),
            console=self.console,
            refresh_per_second=30,
        )
        self._live.start()

    def stream_token(
        self,
        token: str,
    ):
        self._stream_buffer += token
        self._live.update(Markdown(self._stream_buffer))

    def finish_assistant_message(self):
        if self._live:
            self._live.stop()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(
        self,
        message: str,
    ) -> Status:
        return self.console.status(
            f"[bold magenta]{message}[/bold magenta]",
            spinner="dots",
        )

    # ------------------------------------------------------------------
    # Tool Calls
    # ------------------------------------------------------------------

    def print_tool(
        self,
        tool: str,
        args: str,
    ):
        self.console.print(f"\n[bold yellow]🔧 Tool Call: {tool}[/bold yellow]")
        self.console.print(f"[dim]{args}[/dim]")

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    def print_session(
        self,
        session_id: str,
    ):
        self.console.print(f"[dim cyan]Session ID: {session_id}[/dim cyan]")

    # ------------------------------------------------------------------
    # System
    # ------------------------------------------------------------------

    def print_system_message(
        self,
        message: str,
    ):
        self.console.print(f"\n[bold yellow]⚙️ System:[/bold yellow] {message}")

    # ------------------------------------------------------------------
    # Error
    # ------------------------------------------------------------------

    def print_error(
        self,
        message: str,
    ):
        self.console.print(f"\n[bold red]❌ Error:[/bold red] {message}")

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def separator(self):
        self.console.print(Rule(style="dim"))

    def clear(self):
        self.console.clear()