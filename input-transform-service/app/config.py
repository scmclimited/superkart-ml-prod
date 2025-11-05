from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Service Configuration
    TRANSFORM_SERVICE_HOST: str = "0.0.0.0"
    TRANSFORM_SERVICE_PORT: int = 8001
    
    # Inference API Configuration
    # Can be overridden via BACKEND_API_URL environment variable from docker-compose
    INFERENCE_API_URL: str = "http://backend-inference-api:8000"
    INFERENCE_API_TIMEOUT: int = 60
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check if BACKEND_API_URL is set (from docker-compose) and use it
        if os.getenv("BACKEND_API_URL"):
            self.INFERENCE_API_URL = os.getenv("BACKEND_API_URL")
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 50
    MAX_BATCH_ROWS: int = 1000
    ALLOWED_FILE_TYPES: list = [".csv"]
    
    # Validation Configuration
    STRICT_VALIDATION: bool = True
    AUTO_NORMALIZE_SUGAR_CONTENT: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # API Configuration
    API_TITLE: str = "SuperKart Input Transform Service"
    API_DESCRIPTION: str = "Validates and transforms input data for the inference API"
    API_VERSION: str = "1.0.0"
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
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


def validate_settings():
    """
    Validate critical settings on startup
    
    Raises:
        ValueError if critical settings are invalid
    """
    if not settings.INFERENCE_API_URL:
        raise ValueError("INFERENCE_API_URL must be set")
    
    if settings.MAX_FILE_SIZE_MB <= 0:
        raise ValueError("MAX_FILE_SIZE_MB must be positive")
    
    if settings.MAX_BATCH_ROWS <= 0:
        raise ValueError("MAX_BATCH_ROWS must be positive")
    
    if settings.INFERENCE_API_TIMEOUT <= 0:
        raise ValueError("INFERENCE_API_TIMEOUT must be positive")
    
    return True