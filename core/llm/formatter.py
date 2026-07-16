from typing import Any

from langchain_core.messages import BaseMessage


class LLMResponseFormatter:
    """Formats LLM responses into plain text."""

    @staticmethod
    def to_text(message: BaseMessage) -> str:
        """
        Convert any provider response into plain text.
        """

        content = message.content

        # OpenAI
        if isinstance(content, str):
            return content

        # Gemini
        if isinstance(content, list):
            parts: list[str] = []

            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        parts.append(text)

            return "\n".join(parts)

        return str(content)