# ============================================================
# core/llm/manager.py — LLM Manager
# ============================================================
# TODO: Factory to return correct LLM based on provider setting
# TODO: Support OpenAI, Anthropic, Google Gemini backends
# TODO: Apply temperature, max_tokens from settings
# TODO: Enable/disable streaming per request
# TODO: Expose `get_llm(provider, model, **kwargs)` function
# ============================================================

from typing import Any
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from config.enums import LLMProvider
from config.settings import settings
from shared.logger import logger
from collections.abc import Iterator, AsyncIterator


class LLMManager:
    def __init__(self):
        self._provider = settings.llm_provider
        self._model_name = settings.llm_model

        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens
        self._model = self._create_model()

    def _create_model(self) -> BaseChatModel:
        """Create and return the configured chat model."""

        common_kwargs = {
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        logger.info(
            "Initializing %s provider...",
            self._provider.value,
        )

        try:

            match self._provider:
                case LLMProvider.GOOGLE:
                    return ChatGoogleGenerativeAI(
                        api_key=settings.google_api_key,
                        model=self._model_name,
                        **common_kwargs,
                    )
                case LLMProvider.OPENAI:
                    return ChatOpenAI(
                        api_key=settings.openai_api_key,
                        model=self._model_name,
                        **common_kwargs,
                    )
                case LLMProvider.ANTHROPIC:
                    return ChatAnthropic(
                        api_key=settings.anthropic_api_key,
                        model=self._model_name,
                        **common_kwargs,
                    )
                case LLMProvider.GROQ:
                    return ChatGroq(
                        api_key=settings.groq_api_key,
                        model=self._model_name,
                        **common_kwargs,
                    )
                case _:
                    raise ValueError(
                        f"Unsupported LLM provider: {self._provider.value}"
                    )

        except Exception:
            logger.exception("Failed to initialize provider.")
            raise

    def invoke(self, input: LanguageModelInput, **kwargs: Any) -> BaseMessage:
        logger.debug("Invoking LLM")
        return self._model.invoke(input, **kwargs)

    async def ainvoke(self, input: LanguageModelInput, **kwargs: Any) -> BaseMessage:
        logger.debug("Async invoking LLM")
        return await self._model.ainvoke(input, **kwargs)

    def stream(self, input: LanguageModelInput, **kwargs: Any) -> Iterator[BaseMessage]:
        logger.debug("Streaming response")
        return self._model.stream(input, **kwargs)

    async def astream(
        self, input: LanguageModelInput, **kwargs: Any
    ) -> AsyncIterator[BaseMessage]:
        async for chunk in self._model.astream(input, **kwargs):
            yield chunk

    @property
    def model(self) -> BaseChatModel:
        return self._model

    def get_model_info(self) -> dict[str, str]:
        return {
            "provider": self._provider.value,
            "model": self._model_name,
        }

llm = LLMManager()