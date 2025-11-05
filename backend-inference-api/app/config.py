from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    Supports both Windows and Linux paths for localhost testing
    
    For Windows localhost testing:
    - Set MODEL_PATH environment variable to point to your model file
    - Or create a .env file in the backend-inference-api directory with MODEL_PATH
    - Default path is for Docker: /app/models/superkart_model.joblib
    """
    
    # Model settings
    # Can be overridden via MODEL_PATH environment variable (docker-compose.yml sets this)
    MODEL_PATH: str = "/app/models/superkart_model.joblib"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure MODEL_PATH is read from environment if set
        import os
        if os.getenv("MODEL_PATH"):
            self.MODEL_PATH = os.getenv("MODEL_PATH")
    
    # API settings
    INFERENCE_API_HOST: str = "0.0.0.0"
    INFERENCE_API_PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()