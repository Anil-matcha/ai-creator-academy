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

    # Per-process sliding-window limit for REST and MCP requests, keyed by socket peer IP.
    API_RATE_LIMIT_REQUESTS: int = 120
    API_RATE_LIMIT_WINDOW_SECONDS: int = 60
    API_RATE_LIMIT_MAX_CLIENTS: int = 8192

    # Uvicorn returns 503 when the number of concurrent connections/tasks reaches this cap.
    HTTP_MAX_CONCURRENCY: int = 200
    HTTP_KEEPALIVE_TIMEOUT_SECONDS: int = 5
    HTTP_MAX_REQUEST_BYTES: int = 10 * 1024 * 1024

    @field_validator("API_RATE_LIMIT_REQUESTS", "API_RATE_LIMIT_WINDOW_SECONDS", "API_RATE_LIMIT_MAX_CLIENTS")
    @classmethod
    def validate_rate_limits(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("API rate limit settings must be greater than zero")
        return value

    @field_validator("HTTP_MAX_CONCURRENCY", "HTTP_KEEPALIVE_TIMEOUT_SECONDS", "HTTP_MAX_REQUEST_BYTES")
    @classmethod
    def validate_http_limits(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("HTTP server limits must be greater than zero")
        return value

    @field_validator("PORT")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not 1 <= value <= 65535:
            raise ValueError("PORT must be between 1 and 65535")
        return value

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
