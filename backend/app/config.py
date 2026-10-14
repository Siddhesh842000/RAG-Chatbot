import os
from pathlib import Path

from dotenv import load_dotenv

# backend/ folder (two levels above this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Read the .env file
load_dotenv(BASE_DIR / ".env")


class Settings:
    """All app settings in one place."""

    APP_NAME: str = "RAG Chatbot"
    VERSION: str = "0.1.0"

    # Groq (LLM)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    LLM_TEMPERATURE: float = 0.1  # low = factual and stable
    LLM_MAX_TOKENS: int = 1500  # the model's thinking tokens count here too
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_REASONING_EFFORT: str = "low"  # low / medium / high

    # CORS: which websites may call this backend
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384  # all-MiniLM-L6-v2 makes vectors of 384 numbers
    EMBEDDING_BATCH_SIZE: int = 32

    # RAG settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 5

    # A chunk is shown as a source only if its score is at least this fraction
    # of the best chunk's score. (The LLM still reads all TOP_K chunks.)
    SOURCE_SCORE_RATIO: float = 0.6

    # Upload limits (protect the small free server)
    MAX_FILE_SIZE_MB: int = 10
    MAX_PAGES: int = 100

    # How many visitors' documents we keep in memory at the same time
    MAX_SESSIONS: int = 5


settings = Settings()
