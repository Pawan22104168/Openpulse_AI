# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Superset
    SUPERSET_BASE_URL: str = Field(..., env="SUPERSET_BASE_URL")
    SUPERSET_API_KEY: str = Field(..., env="SUPERSET_API_KEY")

    # PostgreSQL
    POSTGRES_HOST: Optional[str] = Field(default=None, env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: Optional[str] = Field(default=None, env="POSTGRES_DB")
    POSTGRES_USER: Optional[str] = Field(default=None, env="POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = Field(default=None, env="POSTGRES_PASSWORD")

    # Vector Store
    VECTOR_STORE_PATH: str = Field(default="./data/vector_db", env="VECTOR_STORE_PATH")

    # Redis Cache
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")

    # LLM Settings
    LLM_MODEL_NAME: str = Field(default="mistral-7b-instruct", env="LLM_MODEL_NAME")
    LLM_MAX_TOKENS: int = Field(default=1024, env="LLM_MAX_TOKENS")

    # App Settings
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        # Load .env from the project root regardless of current working directory
        env_file = str(Path(__file__).resolve().parents[1] / ".env")
        env_file_encoding = "utf-8"


settings = Settings()
