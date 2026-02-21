import os
from typing import List, Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Velos API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["dev", "staging", "prod"] = "dev"
    LOG_LEVEL: str = "INFO"

    # API Security Config
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000"]
    
    # Auth (JWT)
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # Database
    # Use SQLite by default for development, PostgreSQL for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./velos.db"

    # LLM Providers (Failover chain: Groq -> Gemini -> Ollama)
    GROQ_API_KEY: str
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    GEMINI_API_KEY: Optional[str] = None
    
    # Storage
    STORAGE_BACKEND: Literal["local", "supabase", "r2"] = "local"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Blockchain
    ETHEREUM_PRIVATE_KEY: str
    ZYND_API_KEY: str = "mock-zynd-key-for-now"
    
    # Optional Services (Graceful degradation)
    REDIS_URL: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None
    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
