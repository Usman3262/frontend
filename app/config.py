"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings from .env file."""
    
    # Application
    app_name: str = "LifeEcho"
    app_version: str = "0.1.0"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    allowed_hosts: list = ["localhost", "127.0.0.1"]
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/lifeecho"
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 3600
    
    # Meilisearch
    meilisearch_url: str = "http://localhost:7700"  # Railway: https://meilisearch-xxxx.railway.app
    meilisearch_api_key: str = ""  # Railroad key: isny8r04wl1tg1fl15kvgdxngdmkngmf
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    
    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    # Limits
    max_story_length: int = 2000
    min_story_length: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
