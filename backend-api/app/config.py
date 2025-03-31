# app/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Attendance API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    
    # API keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # AI model settings
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "gemini")  # Options: claude, openai, gemini
    
    # CORS settings
    CORS_ORIGINS: List[str] = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
    
    # Database retry settings
    DB_RETRY_ATTEMPTS: int = int(os.getenv("DB_RETRY_ATTEMPTS", "3"))
    DB_RETRY_MIN_SECONDS: int = int(os.getenv("DB_RETRY_MIN_SECONDS", "4"))
    DB_RETRY_MAX_SECONDS: int = int(os.getenv("DB_RETRY_MAX_SECONDS", "10"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()