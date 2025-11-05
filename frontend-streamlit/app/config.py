from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Transform Service Configuration
    TRANSFORM_SERVICE_URL: str = "http://input-transform-service:8001"
    
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