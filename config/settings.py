# ============================================================
# config/settings.py — Application Settings & Configuration
# ============================================================
# TODO: Load environment variables using pydantic-settings or python-dotenv
# TODO: Define a Settings class with all app-wide configuration
# TODO: Expose a singleton settings instance for import
# ============================================================


"""
Application configuration.

Loads environment variables from `.env` using Pydantic Settings
and exposes a singleton `settings` object.

This module is the ONLY place where environment variables
should be accessed. Do not use `os.getenv()` anywhere else
in the project.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.enums import (
    AppEnvironment,
    CLITheme,
    EmbeddingProvider,
    LLMProvider,
    LogFormat,
    LogLevel,
    RetrievalStrategy,
    SearchProvider,
    VectorStore,
)

# ============================================================================
# Application
# ============================================================================


class AppSettings(BaseModel):
    """Application configuration."""

    name: str = Field(alias="APP_NAME")
    version: str = Field(alias="APP_VERSION")
    environment: AppEnvironment = Field(alias="APP_ENV")
    debug: bool = Field(alias="DEBUG")


# ============================================================================
# LLM
# ============================================================================


class LLMSettings(BaseModel):
    """Large Language Model configuration."""

    provider: LLMProvider = Field(alias="LLM_PROVIDER")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")

    model: str = Field(alias="LLM_MODEL")

    temperature: float = Field(alias="LLM_TEMPERATURE")

    max_tokens: int = Field(alias="LLM_MAX_TOKENS")

    streaming: bool = Field(alias="LLM_STREAMING")

    top_p: float = Field(alias="TOP_P")

    top_k: int = Field(alias="TOP_K")

    @model_validator(mode="after")
    def validate_temperature(self):
        if not 0 <= self.temperature <= 2:
            raise ValueError("LLM_TEMPERATURE must be between 0 and 2")
        return self


# ============================================================================
# Embeddings
# ============================================================================


class EmbeddingSettings(BaseModel):
    """Embedding model configuration."""

    provider: EmbeddingProvider = Field(alias="EMBEDDING_PROVIDER")
    model: str = Field(alias="EMBEDDING_MODEL")


# ============================================================================
# Memory
# ============================================================================


class MemorySettings(BaseModel):
    """Conversation memory configuration."""

    max_history_messages: int = Field(alias="MAX_HISTORY_MESSAGES")

    summary_trigger_messages: int = Field(alias="SUMMARY_TRIGGER_MESSAGES")

    summary_keep_last_messages: int = Field(alias="SUMMARY_KEEP_LAST_MESSAGES")

    max_context_tokens: int = Field(alias="MAX_CONTEXT_TOKENS")

    auto_generate_session_title: bool = Field(alias="AUTO_GENERATE_SESSION_TITLE")

    @model_validator(mode="after")
    def validate_summary(self):
        if self.summary_keep_last_messages >= self.summary_trigger_messages:
            raise ValueError(
                "SUMMARY_KEEP_LAST_MESSAGES "
                "must be smaller than SUMMARY_TRIGGER_MESSAGES"
            )

        return self


# ============================================================================
# Database
# ============================================================================


class DatabaseSettings(BaseModel):
    """Database configuration."""

    database_url: str = Field(alias="DATABASE_URL")

    checkpoint_db_path: Path = Field(alias="CHECKPOINT_DB_PATH")

    session_db_path: Path = Field(alias="SESSION_DB_PATH")

    summary_db_path: Path = Field(alias="SUMMARY_DB_PATH")


# ============================================================================
# Vector Store
# ============================================================================


class VectorStoreSettings(BaseModel):
    """Vector database configuration."""

    backend: VectorStore = Field(alias="VECTOR_STORE")

    chroma_persist_dir: Path = Field(alias="CHROMA_PERSIST_DIR")

    faiss_index_path: Path = Field(alias="FAISS_INDEX_PATH")

    qdrant_url: str = Field(alias="QDRANT_URL")

    qdrant_api_key: str | None = Field(
        default=None,
        alias="QDRANT_API_KEY",
    )

    postgres_host: str = Field(alias="POSTGRES_HOST")

    postgres_port: int = Field(alias="POSTGRES_PORT")

    postgres_db: str = Field(alias="POSTGRES_DB")

    postgres_user: str = Field(alias="POSTGRES_USER")

    postgres_password: str = Field(alias="POSTGRES_PASSWORD")


# ============================================================================
# RAG
# ============================================================================


class RAGSettings(BaseModel):
    """Retrieval-Augmented Generation configuration."""

    enabled: bool = Field(alias="ENABLE_RAG")

    upload_dir: Path = Field(alias="UPLOAD_DIR")

    chunk_size: int = Field(alias="CHUNK_SIZE")

    chunk_overlap: int = Field(alias="CHUNK_OVERLAP")

    retrieval_top_k: int = Field(alias="RETRIEVAL_TOP_K")

    retrieval_strategy: RetrievalStrategy = Field(alias="RETRIEVAL_STRATEGY")


# ============================================================================
# Tools
# ============================================================================


class ToolSettings(BaseModel):
    """Tool configuration."""

    enable_search: bool = Field(alias="ENABLE_SEARCH_TOOL")

    enable_weather: bool = Field(alias="ENABLE_WEATHER_TOOL")

    enable_news: bool = Field(alias="ENABLE_NEWS_TOOL")

    enable_calculator: bool = Field(alias="ENABLE_CALCULATOR_TOOL")

    search_provider: SearchProvider = Field(alias="SEARCH_PROVIDER")

    serper_api_key: str | None = Field(default=None, alias="SERPER_API_KEY")

    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    openweather_api_key: str | None = Field(
        default=None,
        alias="OPENWEATHER_API_KEY",
    )

    openweather_base_url: str = Field(alias="OPENWEATHER_BASE_URL")

    newsapi_api_key: str | None = Field(
        default=None,
        alias="NEWSAPI_API_KEY",
    )

    newsapi_base_url: str = Field(alias="NEWSAPI_BASE_URL")


# ============================================================================
# HTTP
# ============================================================================


class HTTPSettings(BaseModel):
    """HTTP client configuration."""

    timeout: int = Field(alias="HTTP_TIMEOUT")

    max_retries: int = Field(alias="MAX_RETRIES")

    retry_delay: int = Field(alias="RETRY_DELAY")

    user_agent: str = Field(alias="USER_AGENT")


# ============================================================================
# CLI
# ============================================================================


class CLISettings(BaseModel):
    """CLI configuration."""

    theme: CLITheme = Field(alias="CLI_THEME")

    streaming: bool = Field(alias="CLI_STREAMING")

    show_tool_calls: bool = Field(alias="CLI_SHOW_TOOL_CALLS")

    show_thinking: bool = Field(alias="CLI_SHOW_THINKING")


# ============================================================================
# Logging
# ============================================================================


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: LogLevel = Field(alias="LOG_LEVEL")

    format: LogFormat = Field(alias="LOG_FORMAT")

    file: Path = Field(alias="LOG_FILE")


# ============================================================================
# LangSmith
# ============================================================================


class LangSmithSettings(BaseModel):
    """LangSmith tracing configuration."""

    tracing: bool = Field(alias="LANGCHAIN_TRACING_V2")

    endpoint: str = Field(alias="LANGCHAIN_ENDPOINT")

    api_key: str | None = Field(
        default=None,
        alias="LANGCHAIN_API_KEY",
    )

    project: str = Field(alias="LANGCHAIN_PROJECT")


# ============================================================================
# Root Settings
# ============================================================================


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app: AppSettings
    llm: LLMSettings
    embedding: EmbeddingSettings
    memory: MemorySettings
    database: DatabaseSettings
    vector_store: VectorStoreSettings
    rag: RAGSettings
    tools: ToolSettings
    http: HTTPSettings
    cli: CLISettings
    logging: LoggingSettings
    langsmith: LangSmithSettings

    @computed_field
    @property
    def project_root(self) -> Path:
        """Return project root directory."""
        return Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
