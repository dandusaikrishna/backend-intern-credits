"""
Configuration module for LawVriksh Credit Management API
"""
import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    db_user: str = "postgres"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "lawvriksh_credits"
    
    # Application settings
    app_name: str = "LawVriksh Credit Management API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS settings
    cors_origins: list = ["*"]
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
