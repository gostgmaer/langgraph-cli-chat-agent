from interfaces.cli.renderer import CLIRenderer
from services.chat_service import ChatService

# (name, usage, description) shown by '/' and '/list'
COMMANDS = [
    ("history", "/history", "Show the conversation history for this session"),
    ("list", "/list", "Show this list of available commands"),
    ("research", "/research <topic>", "Run multi-agent research on a topic"),
    ("clear", "/clear", "Clear the screen and start a new session"),
]


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
            "Tip: Type '/' to see available commands, or just type a message to chat."
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

                if user_message.strip() == "/":
                    user_message = await self._prompt_menu_choice()
                    if user_message is None:
                        continue

                cmd = user_message.strip().lower()

                if cmd == "/list":
                    self._renderer.print_command_menu(COMMANDS)
                    continue

                if cmd == "/history":
                    await self._show_history()
                    continue

                if cmd == "/clear":
                    await self._clear_session()
                    continue

                if cmd == "/research":
                    topic = await self._prompt_topic()
                    if not topic:
                        self._renderer.print_system_message(
                            "Research cancelled — no topic given."
                        )
                        continue
                    user_message = f"/research {topic}"

                is_research = user_message.strip().startswith("/research")
                status_text = (
                    "Researching... (This may take a minute)"
                    if is_research
                    else "Thinking..."
                )
                await self._consume_stream(
                    self._chat_service.stream_chat(user_message), status_text
                )

                # Human-in-the-loop: the research planner pauses for plan
                # approval before dispatching parallel searches. Keep
                # resuming (which may itself pause again, e.g. after a
                # rejection produces a final answer with no further pause)
                # until the graph is no longer paused.
                pending = await self._chat_service.get_pending_interrupt()
                while pending:
                    resume_value = await self._review_plan(pending)
                    await self._consume_stream(
                        self._chat_service.resume_chat(resume_value),
                        "Researching... (This may take a minute)",
                    )
                    pending = await self._chat_service.get_pending_interrupt()

                self._renderer.separator()

            except KeyboardInterrupt:
                self._renderer.print_system_message("\nGoodbye 👋")
                break
            except Exception as error:
                self._renderer.print_error(str(error))

    async def _consume_stream(self, chunk_iter, status_text: str) -> None:
        """Render a stream of StreamChunk events: step announcements are
        printed as status lines, tokens are rendered as a live assistant
        message. A spinner covers the gap before the first event arrives."""
        status = self._renderer.status(status_text)
        status.start()
        status_running = True
        live_open = False
        try:
            async for chunk in chunk_iter:
                if status_running:
                    status.stop()
                    status_running = False

                if chunk.type == "step":
                    if live_open:
                        self._renderer.finish_assistant_message()
                        live_open = False
                    self._renderer.print_step(chunk.content)
                    continue

                if chunk.type == "usage":
                    if live_open:
                        self._renderer.finish_assistant_message()
                        live_open = False
                    self._renderer.print_usage(chunk.content)
                    continue

                if not live_open:
                    self._renderer.start_assistant_message()
                    live_open = True
                self._renderer.stream_token(chunk.content)
        finally:
            if status_running:
                status.stop()
            if live_open:
                self._renderer.finish_assistant_message()

    async def _review_plan(self, payload: dict) -> dict:
        """Show the planner's proposed sub-questions and ask the user to
        approve, reject, or modify them before parallel search runs."""
        sub_questions = payload.get("sub_questions") or []
        self._renderer.print_plan(sub_questions)

        while True:
            self.console.print(
                "\n[bold yellow]Approve this plan?[/bold yellow] "
                "[dim]([green]y[/green]es / [red]n[/red]o / [cyan]m[/cyan]odify)[/dim] ",
                end="",
            )
            choice = str(input().strip().lower())

            if choice in ("y", "yes", ""):
                return {"action": "approve"}

            if choice in ("n", "no"):
                return {"action": "reject"}

            if choice in ("m", "modify"):
                self.console.print(
                    "[dim]Enter revised sub-questions, one per line. Blank line to finish:[/dim]"
                )
                revised = []
                while True:
                    line = str(input().strip())
                    if not line:
                        break
                    revised.append(line)
                if revised:
                    return {"action": "modify", "sub_questions": revised}
                self._renderer.print_system_message(
                    "No sub-questions entered — keeping the original plan."
                )
                return {"action": "approve"}

            self._renderer.print_system_message("Please answer y, n, or m.")

    async def _prompt_menu_choice(self) -> str | None:
        """Show the slash-command menu and let the user pick an entry by
        number or name. Returns the fully-formed command string to execute
        (e.g. '/history', '/research <topic>'), or None if cancelled."""
        self._renderer.print_command_menu(COMMANDS)
        self.console.print(
            "\n[bold yellow]Select a command[/bold yellow] "
            "[dim](number or name, blank to cancel):[/dim] ",
            end="",
        )
        choice = str(input().strip().lower())
        if not choice:
            return None

        name = None
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(COMMANDS):
                name = COMMANDS[index][0]
        else:
            candidate = choice.lstrip("/")
            if candidate in (c[0] for c in COMMANDS):
                name = candidate

        if name is None:
            self._renderer.print_system_message(f"Unknown command: {choice}")
            return None

        if name == "research":
            topic = await self._prompt_topic()
            if not topic:
                self._renderer.print_system_message(
                    "Research cancelled — no topic given."
                )
                return None
            return f"/research {topic}"

        return f"/{name}"

    async def _prompt_topic(self) -> str:
        """Ask the user for a research topic."""
        self.console.print(
            "[bold yellow]Research topic:[/bold yellow] ", end=""
        )
        return str(input().strip())

    async def _show_history(self) -> None:
        """Display the message history for the current session."""
        messages = await self._chat_service.get_history()
        self._renderer.print_history(messages)

    async def _clear_session(self) -> None:
        """Clear the screen and start a brand-new session."""
        self._renderer.clear()
        session = await self._chat_service.new_session()
        self._renderer.print_banner()
        self._renderer.print_session(session.id)
        self._renderer.print_system_message(
            "Started a new session. Previous conversation context has been cleared."
        )

