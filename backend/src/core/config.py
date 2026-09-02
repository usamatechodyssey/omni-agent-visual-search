import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniAgent Core"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # ------------------- SUPER ADMIN STRICT LOGIN 🔒 -------------------
    # Sirf yeh email login kar payega. Doosre emails ke liye access block.
    SUPER_ADMIN_EMAIL: str = os.getenv("SUPER_ADMIN_EMAIL", "usamabhattipk027@gmail.com")
    # Yeh password hash .env mein daalein (Uper wale command se generate karein)
    SUPER_ADMIN_PASSWORD_HASH: str = os.getenv("SUPER_ADMIN_PASSWORD_HASH", "")

    # ------------------- DATABASES (Generic) -------------------
    _DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./omni_agent.db")

    @property
    def DATABASE_URL(self) -> str:
        url = self._DATABASE_URL
        if url and "?" in url:
            url = url.split("?")[0]
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    VECTOR_DB_PROVIDER: str = os.getenv("VECTOR_DB_PROVIDER", "")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: str | None = os.getenv("QDRANT_API_KEY") or None
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "omni_agent_collection")

    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", "27017"))
    MONGO_USER: str = os.getenv("MONGO_USER", "")
    MONGO_PASS: str = os.getenv("MONGO_PASS", "")

    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "")
    EMBEDDING_API_KEY: str | None = os.getenv("EMBEDDING_API_KEY") or None
    EMBEDDING_BASE_URL: str | None = os.getenv("EMBEDDING_BASE_URL") or None

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "")
    LLM_BASE_URL: str | None = os.getenv("LLM_BASE_URL") or None
    LLM_API_KEY: str | None = os.getenv("LLM_API_KEY") or None

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY") or None
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY") or None
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY") or None
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY") or None
    MISTRAL_API_KEY: str | None = os.getenv("MISTRAL_API_KEY") or None
    CEREBRAS_API_KEY: str | None = os.getenv("CEREBRAS_API_KEY") or None

    CUSTOM_LLM_BASE_URL: str | None = os.getenv("CUSTOM_LLM_BASE_URL") or None
    CUSTOM_LLM_API_KEY: str | None = os.getenv("CUSTOM_LLM_API_KEY") or None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()