from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Q&A App"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-for-jwt-keep-it-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/aiqna"
    
    # AI Services
    GEMINI_API_KEY: Optional[str] = None
    WHISPER_MODEL: str = "base"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
