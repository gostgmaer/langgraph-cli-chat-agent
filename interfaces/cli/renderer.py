from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.status import Status
from rich.live import Live
from rich.align import Align
from rich.box import ROUNDED
from rich import print

from config.settings import settings


class CLIRenderer:
    """Rich terminal renderer."""

    def __init__(self) -> None:
        self.console = Console()
        self._stream_buffer = ""

    # ------------------------------------------------------------------
    # Banner
    # ------------------------------------------------------------------

    def print_banner(self) -> None:

        title = Text(
            settings.app_name,
            style="bold cyan",
            justify="center",
        )

        subtitle = Text(
            f"Version {settings.app_version} • {settings.llm_provider.value.upper()} • {settings.llm_model}",
            style="dim",
            justify="center",
        )

        self.console.print()

        self.console.print(
            Panel.fit(
                Align.center(Text.assemble(title, "\n", subtitle)),
                border_style="cyan",
                box=ROUNDED,
                padding=(1, 6),
            )
        )

        self.console.print(Rule("[bold cyan]Interactive Chat Session[/bold cyan]"))

    # ------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------

    def print_user_message(
        self,
        message: str,
    ) -> None:

        self.console.print()

        self.console.print(
            Panel(
                Markdown(message),
                title="👤 You",
                title_align="left",
                border_style="green",
                expand=True,
            )
        )

    # ------------------------------------------------------------------
    # Assistant
    # ------------------------------------------------------------------

    def print_assistant_message(
        self,
        message: str,
    ) -> None:

        self.console.print()

        self.console.print(
            Panel(
                Markdown(message),
                title="🤖 Assistant",
                title_align="left",
                border_style="blue",
                expand=True,
            )
        )

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    def start_assistant_message(self):

        self._stream_buffer = ""

        self._live = Live(
            Panel(
                "",
                title="🤖 Assistant",
                border_style="blue",
                expand=True,
            ),
            console=self.console,
            refresh_per_second=30,
        )

        self._live.start()

    def stream_token(
        self,
        token: str,
    ):

        self._stream_buffer += token

        self._live.update(
            Panel(
                Markdown(self._stream_buffer),
                title="🤖 Assistant",
                border_style="blue",
                expand=True,
            )
        )

    def finish_assistant_message(self):

        self._live.stop()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(
        self,
        message: str,
    ) -> Status:

        return self.console.status(
            message,
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

        self.console.print(
            Panel(
                args,
                title=f"🔧 {tool}",
                border_style="yellow",
                expand=True,
            )
        )

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    def print_session(
        self,
        session_id: str,
    ):

        self.console.print(
            Panel.fit(
                f"[cyan]{session_id}[/cyan]",
                title="Session",
                border_style="cyan",
            )
        )

    # ------------------------------------------------------------------
    # System
    # ------------------------------------------------------------------

    def print_system_message(
        self,
        message: str,
    ):

        self.console.print(
            Panel.fit(
                message,
                title="System",
                border_style="yellow",
            )
        )

    # ------------------------------------------------------------------
    # Error
    # ------------------------------------------------------------------

    def print_error(
        self,
        message: str,
    ):

        self.console.print(
            Panel(
                message,
                title="❌ Error",
                border_style="red",
                expand=True,
            )
        )

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def separator(self):

        self.console.print(Rule())

    def clear(self):

        self.console.clear()
