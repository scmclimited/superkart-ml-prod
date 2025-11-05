from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Transform Service Configuration
    # Can be overridden via TRANSFORM_API_URL environment variable from docker-compose
    # Note: Pydantic BaseSettings will automatically read TRANSFORM_API_URL from environment
    TRANSFORM_SERVICE_URL: str = "http://input-transform-service:8030"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Map TRANSFORM_API_URL (from docker-compose) to TRANSFORM_SERVICE_URL
        import os
        transform_url = os.getenv("TRANSFORM_API_URL")
        if transform_url:
            self.TRANSFORM_SERVICE_URL = transform_url
    
    # UI Configuration
    APP_TITLE: str = "SuperKart Sales Forecasting"
    APP_ICON: str = "🛒"
    APP_LAYOUT: str = "wide"
    
    # Feature Flags
    ENABLE_BATCH_PREDICTION: bool = True
    ENABLE_DOWNLOAD: bool = True
    DEBUG_MODE: bool = False
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 50
    MAX_BATCH_ROWS: int = 10000
    ALLOWED_FILE_EXTENSIONS: list = [".csv"]
    
    # API Configuration
    API_TIMEOUT: int = 120
    
    # Display Configuration
    RECORDS_PER_PAGE: int = 100
    SHOW_PREDICTION_DETAILS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings instance
    
    Returns:
        Settings instance
    """
    return settings