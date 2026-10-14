from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
from urllib.parse import urlsplit

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

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, origins: List[str]) -> List[str]:
        normalized = []
        for origin in origins:
            origin = origin.strip()
            parsed = urlsplit(origin)
            if (
                not origin
                or "*" in origin
                or parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("CORS_ORIGINS must contain explicit HTTP(S) origins; wildcard origins are not allowed")
            normalized.append(origin.rstrip("/"))
        return list(dict.fromkeys(normalized))
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
