from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule
from rich.status import Status
from rich.live import Live
from rich.table import Table
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
    # Graph Step Visibility
    # ------------------------------------------------------------------

    def print_step(
        self,
        label: str,
    ) -> None:
        """Show a single graph node's execution as a lightweight status
        line, so the user can follow what the system is doing step by
        step (routing, planning, searching, reviewing, etc.)."""
        self.console.print(f"[dim cyan]  → {label}[/dim cyan]")

    def print_usage(
        self,
        summary: str,
    ) -> None:
        """Show token-usage totals for a completed turn."""
        self.console.print(f"[dim yellow]{summary}[/dim yellow]")

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    def print_session(
        self,
        session_id: str,
    ):
        self.console.print(f"[dim cyan]Session ID: {session_id}[/dim cyan]")

    # ------------------------------------------------------------------
    # Research Plan Review (Human-in-the-Loop)
    # ------------------------------------------------------------------

    def print_plan(
        self,
        sub_questions: list[str],
    ) -> None:
        self.console.print("\n[bold magenta]📋 Research Plan:[/bold magenta]")
        for i, q in enumerate(sub_questions, start=1):
            self.console.print(f"  [cyan]{i}.[/cyan] {q}")

    # ------------------------------------------------------------------
    # Slash Commands
    # ------------------------------------------------------------------

    def print_command_menu(
        self,
        commands: list[tuple[str, str, str]],
    ) -> None:
        """Render the available slash commands as a numbered table.

        `commands` is a list of (name, usage, description) tuples.
        """
        table = Table(title="Available Commands", show_lines=False)
        table.add_column("#", style="dim", justify="right")
        table.add_column("Command", style="bold cyan")
        table.add_column("Description")

        for i, (_, usage, description) in enumerate(commands, start=1):
            table.add_row(str(i), usage, description)

        self.console.print(table)

    def print_history(
        self,
        messages: list,
    ) -> None:
        """Render the conversation history for the current session."""
        if not messages:
            self.print_system_message("No conversation history yet for this session.")
            return

        self.console.print("\n[bold magenta]📜 Conversation History:[/bold magenta]")
        for msg in messages:
            role = type(msg).__name__
            text = self._stringify_content(getattr(msg, "content", ""))
            if not text.strip():
                continue

            if role == "HumanMessage":
                self.console.print("\n[bold green]👤 You:[/bold green]")
                self.console.print(text)
            elif role == "AIMessage":
                self.console.print("\n[bold blue]🤖 Assistant:[/bold blue]")
                self.console.print(Markdown(text))
            elif role == "SystemMessage":
                continue
            else:
                self.console.print(f"\n[dim]{role}:[/dim] {text}")

    @staticmethod
    def _stringify_content(content) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    parts.append(block)
            return "".join(parts)
        return str(content) if content else ""

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