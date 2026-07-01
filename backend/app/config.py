"""
Application Configuration Settings
Using Pydantic Settings for environment variable management
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "FinBuddy"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SQL_ECHO: bool = False
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/finbuddy"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    @property
    def async_database_url(self) -> str:
        """Convert standard PostgreSQL URL to asyncpg format."""
        url = self.DATABASE_URL
        # Convert postgresql:// to postgresql+asyncpg://
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Handle Neon SSL parameters - asyncpg uses ssl=require instead of sslmode
        url = url.replace("sslmode=require", "ssl=require")
        url = url.replace("&channel_binding=require", "")
        return url
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # OpenAI (legacy fallback)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5.1"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 4096
    
    # Google Gemini / Google AI Studio (primary for Kaggle ADK course)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_MODEL_PRO: str = "gemini-2.5-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_OUTPUT_TOKENS: int = 4096
    GEMINI_TOP_P: float = 0.95
    GEMINI_TOP_K: int = 40
    
    # Agent Framework Selection
    AGENT_FRAMEWORK: str = "adk"  # "adk" (Google) or "langchain" (legacy)
    
    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION_NAME: str = "finbuddy_knowledge"
    
    # JWT
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    PII_REDACTION_ENABLED: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    AUDIT_LOGGING_ENABLED: bool = True
    ENCRYPTION_KEY: str = ""
    
    # Market Data APIs
    ALPHA_VANTAGE_API_KEY: str = ""
    YAHOO_FINANCE_ENABLED: bool = True
    
    # Bank Integration
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"
    
    # News APIs
    NEWS_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    
    # OCR
    OCR_PROVIDER: str = "openai"
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ("../.env", ".env")  # Check parent dir first, then current
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars not in the model
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "CORS_ORIGINS":
                return json.loads(raw_val)
            return raw_val


settings = Settings()
