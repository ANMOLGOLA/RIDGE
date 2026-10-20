from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "RIDGE - Regional Intelligence & Geospatial Efficiency"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # TinyFish Web Intelligence
    TINYFISH_API_KEY: Optional[str] = None
    TINYFISH_MODE: str = "fixture"  # "live" | "fixture"
    ENABLE_TINYFISH_AGENT: bool = False
    
    # LLM Configuration
    LLM_PROVIDER: str = "none"  # "anthropic" | "none"
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ridge.db')).replace('\\', '/')}"
    REDIS_URL: Optional[str] = None
    
    # Periodic Ingestion & Risk Refresh
    INGEST_INTERVAL_MIN: int = 15
    RISK_REFRESH_MIN: int = 30
    
    # Vision & Alerts
    ENABLE_VISION: bool = False
    ENABLE_TWILIO: bool = False
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
