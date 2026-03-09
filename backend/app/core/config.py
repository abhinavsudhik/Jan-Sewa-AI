from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import json

class Settings(BaseSettings):
    # Database - optional for basic functionality
    DATABASE_URL: Optional[str] = None
    
    # Redis - optional
    REDIS_URL: Optional[str] = None
    
    # API Keys - required for AI features
    GEMINI_API_KEY: str = "your_key_here"
    
    # Security
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Vercel deployment URL (configurable via environment variable)
    VERCEL_URL: Optional[str] = None
    
    # Additional CORS origins (optional, comma-separated)
    ADDITIONAL_CORS_ORIGINS: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_cors_origins(self) -> List[str]:
        """Get the complete list of allowed CORS origins"""
        origins = [
            "http://localhost:3000",
            "http://localhost:3001",
        ]
        
        # Add Vercel URL if set
        if self.VERCEL_URL:
            origins.append(self.VERCEL_URL)
        
        # Add additional origins from env var if set
        if self.ADDITIONAL_CORS_ORIGINS:
            # Treat as comma-separated string
            additional = [o.strip() for o in self.ADDITIONAL_CORS_ORIGINS.split(",") if o.strip()]
            origins.extend(additional)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_origins = []
        for origin in origins:
            if origin not in seen:
                seen.add(origin)
                unique_origins.append(origin)
        
        return unique_origins

settings = Settings()
