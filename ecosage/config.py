"""Configuration management for EcoSage.

Supports multiple LLM providers:
- gemini: Google Gemini (free, needs Gmail only)
- groq: Groq Cloud (free, needs email signup)
- ollama: Local Ollama (free, no account needed at all)
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables and .env file."""
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Provider: "gemini", "groq", or "ollama"
    LLM_PROVIDER: str = "gemini"

    # API Keys (only needed for cloud providers)
    GOOGLE_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    # Model names per provider
    LLM_MODEL: str = "gemini-3.5-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"

    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    # Groq settings
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ChromaDB
    CHROMA_PATH: str = "./chroma_db"
    CHROMA_COLLECTION: str = "ecosage_knowledge"

    # Retrieval
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.65
    HIGH_CONFIDENCE_THRESHOLD: float = 0.80

    LOG_LEVEL: str = "INFO"

    def get_active_model(self) -> str:
        """Return the model name for the active provider."""
        if self.LLM_PROVIDER == "groq":
            return self.GROQ_MODEL
        elif self.LLM_PROVIDER == "ollama":
            return self.OLLAMA_MODEL
        return self.LLM_MODEL

    def validate_provider(self) -> None:
        """Validate that required keys are set for the chosen provider."""
        if self.LLM_PROVIDER == "gemini" and not self.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is required for Gemini provider. "
                "Get a free key at https://aistudio.google.com (no card needed, just Gmail)"
            )
        if self.LLM_PROVIDER == "groq" and not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is required for Groq provider. "
                "Get a free key at https://console.groq.com (no card needed)"
            )


@lru_cache
def get_settings() -> Settings:
    """Return application settings, cached."""
    settings = Settings()
    settings.validate_provider()
    return settings
