# ============================================================
# interfaces/cli/cli.py — Main CLI Application
# ============================================================
# TODO: Define the main CLI app (e.g., Typer or Click app)
# TODO: Register all CLI commands
# TODO: Handle startup / shutdown lifecycle
# ============================================================



from copy import error

from interfaces.cli.renderer import CLIRenderer
from services.chat_service import ChatService


class CLI:
     def __init__(
        self,
        chat_service: ChatService,
        renderer: CLIRenderer,
    ):
          self._chat_service =chat_service
          self._renderer=renderer
    

     def run(self)->None:
          "Start the CLI application."
          self._renderer.print_banner()
          while True:
              try:
                user_message =str(input("You: ").strip())
                if not user_message:
                    continue
                if user_message.lower() in ('exit','quit','close'):
                    self._renderer.print_system_message("Goodbye!")
                    break
                self._renderer.print_user_message(user_message)
                response = self._chat_service.chat(user_message)
                self._renderer.print_assistant_message(response.content)
                # self._renderer.print_assistant_message(response)
              except KeyboardInterrupt:
                self._renderer.print_system_message("\nGoodbye 👋")
                break

              except Exception as error:
                self._renderer.print_error(str(error))



