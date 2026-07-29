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

                if user_message.lower() == "/graph":
                    try:
                        png_bytes = self._chat_service._graph.get_graph(
                            xray=True
                        ).draw_mermaid_png()
                        with open("graph.png", "wb") as f:
                            f.write(png_bytes)
                        self._renderer.print_system_message(
                            "✅ Saved Master Graph diagram to 'graph.png'"
                        )
                    except Exception as e:
                        self._renderer.print_error(f"Could not render graph PNG: {e}")
                    continue

                is_research = user_message.strip().startswith("/research")
                status_text = (
                    "Researching... (This may take a minute)"
                    if is_research
                    else "Thinking..."
                )

                first_token = True
                status = self._renderer.status(status_text)
                status.start()

                try:
                    async for token in self._chat_service.stream_chat(user_message):
                        if first_token:
                            status.stop()
                            self._renderer.start_assistant_message()
                            first_token = False
                        self._renderer.stream_token(token)
                finally:
                    if first_token:
                        status.stop()
                        self._renderer.start_assistant_message()

                self._renderer.finish_assistant_message()

                # Human-in-the-loop: the research planner pauses for plan
                # approval before dispatching parallel searches. Keep
                # resuming (which may itself pause again, e.g. after a
                # rejection produces a final answer with no further pause)
                # until the graph is no longer paused.
                pending = await self._chat_service.get_pending_interrupt()
                while pending:
                    resume_value = await self._review_plan(pending)

                    status = self._renderer.status(
                        "Researching... (This may take a minute)"
                    )
                    status.start()
                    first_token = True
                    try:
                        async for token in self._chat_service.resume_chat(resume_value):
                            if first_token:
                                status.stop()
                                self._renderer.start_assistant_message()
                                first_token = False
                            self._renderer.stream_token(token)
                    finally:
                        if first_token:
                            status.stop()
                            self._renderer.start_assistant_message()
                    self._renderer.finish_assistant_message()

                    pending = await self._chat_service.get_pending_interrupt()

                self._renderer.separator()

            except KeyboardInterrupt:
                self._renderer.print_system_message("\nGoodbye 👋")
                break
            except Exception as error:
                self._renderer.print_error(str(error))

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
