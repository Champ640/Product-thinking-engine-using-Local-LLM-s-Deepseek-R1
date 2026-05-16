"""
Configuration loader for PRODUCT THINKER.
Reads all settings from .env file in project root.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Typed settings loaded from environment variables."""

    # LLM
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    ollama_thinking_temp: float = float(os.getenv("OLLAMA_THINKING_TEMP", "0.6"))
    ollama_normal_temp: float = float(os.getenv("OLLAMA_NORMAL_TEMP", "0.7"))

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Web Search
    search_max_results: int = int(os.getenv("SEARCH_MAX_RESULTS", "5"))

    # OpenRouter
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-next-80b-a3b-instruct:free")


settings = Settings()
