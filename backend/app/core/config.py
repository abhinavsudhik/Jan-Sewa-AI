from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://govt_services_user:secure_password_here@postgres:5432/govt_services"
    REDIS_URL: str = "redis://redis:6379"
    GEMINI_API_KEY: str = "your_key_here"
    SECRET_KEY: str = "dev_secret_key"
    ENVIRONMENT: str = "development"
    
    # Vercel deployment URL (configurable via environment variable)
    VERCEL_URL: str = "https://jansewaai-beige.vercel.app"
    
    # Allow Vercel and local development
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_cors_origins(self) -> List[str]:
        """Get the complete list of allowed CORS origins including Vercel URL"""
        origins = self.CORS_ORIGINS.copy()
        if self.VERCEL_URL:
            origins.append(self.VERCEL_URL)
        return origins

settings = Settings()
