from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://govt_services_user:secure_password_here@postgres:5432/govt_services"
    REDIS_URL: str = "redis://redis:6379"
    GEMINI_API_KEY: str = "your_key_here"
    SECRET_KEY: str = "dev_secret_key"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
