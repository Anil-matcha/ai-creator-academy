from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Open Agent Email"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/v1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./open_agent_email.db"
    
    # Server & Domains
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    SHARED_DOMAIN: str = "agents.local"
    DEFAULT_SENSITIVITY: str = "medium"  # low, medium, high
    
    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Admin master key for demo/local setup
    ADMIN_API_KEY: str = "oak_live_demo_key_998877"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
