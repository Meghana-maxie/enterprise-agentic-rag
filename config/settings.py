"""System settings and environment configuration."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable fallback."""

    # Project Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    # LLM Settings
    LLM_PROVIDER: str = "ollama" 
    OLLAMA_MODEL: str = "llama3.2:3b"
    ANTHROPIC_API_KEY: str = "mock-key"
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 2048

    # Qdrant Vector Store
    QDRANT_STORAGE_PATH: str = str(BASE_DIR / "data" / "qdrant_db")
    QDRANT_COLLECTION_NAME: str = "enterprise_knowledge_base"
    QDRANT_URL: Optional[str] = None
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384

    # BM25 Storage
    BM25_INDEX_PATH: str = str(BASE_DIR / "data" / "bm25_index.pkl")

    # Local Reranker
    RERANKER_MODEL: str = "ms-marco-MiniLM-L-12-v2"

    # Retrieval & Routing Parameters
    TOP_K_RETRIEVAL: int = 12
    TOP_K_RERANK: int = 4
    RRF_K: int = 60  # Reciprocal Rank Fusion constant
    FAITHFULNESS_THRESHOLD: float = 0.85
    MAX_CRITIC_RETRIES: int = 1

    # Ingestion Parameters
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 80

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure required directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
Path(settings.QDRANT_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
