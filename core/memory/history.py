# ============================================================
# core/memory/history.py — Conversation History Manager
# ============================================================
# TODO: Load message history for a given session_id
# TODO: Save new messages to persistent store
# TODO: Trim history to max allowed message count
# TODO: Convert history to LangChain message format
# ============================================================


from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class HistoryManager:
    """Manages conversation history for all sessions."""

    def __init__(self):
        self._history: dict[str, list[BaseMessage]] = {}

    def add_user_message(
        self,
        session_id: str,
        message: str,
    ) -> None:
        """Add a user message to a session."""

        self._history.setdefault(session_id, []).append(HumanMessage(content=message))

    def add_ai_message(self, session_id: str, message: str) -> None:
        """Add an AI message to a session."""
        self._history.setdefault(session_id, []).append(AIMessage(content=message))

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        """Retrieve all messages for a session."""
        return self._history.get(session_id, [])

    def clear_history(self, session_id: str) -> None:
        """Clear the message history for a session."""
        if session_id in self._history:
            del self._history[session_id]

    def delete_history(self, session_id: str) -> None:
        """Delete the history for a session."""
        if session_id in self._history:
            del self._history[session_id]

    def trim_history(self, session_id: str, max_messages: int) -> None:
        """Trim the message history for a session to a maximum number of messages."""
        if session_id in self._history:
            self._history[session_id] = self._history[session_id][-max_messages:]


history_manager = HistoryManager()
