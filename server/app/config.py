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
    
    # Set explicitly in the environment; no built-in administrator credential.
    ADMIN_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
