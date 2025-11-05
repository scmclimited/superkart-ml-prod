import joblib
import logging
import os
from pathlib import Path
from typing import Optional, Any

from app.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Handles loading of pretrained machine learning models
    Designed for inference-only operations (no training)
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ModelLoader
        
        Args:
            model_path: Optional path to model file. If not provided, uses settings.MODEL_PATH
        """
        self.model_path = model_path or settings.MODEL_PATH
        self.model: Optional[Any] = None
        self._is_loaded = False
    
    def load_model(self) -> None:
        """
        Load pretrained model from file
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            ValueError: If model file cannot be loaded
        """
        try:
            # Convert to Path object for cross-platform compatibility
            model_path = Path(self.model_path)
            
            # Check if file exists
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Model file not found at: {self.model_path}. "
                    f"Please ensure the model file exists at the specified path."
                )
            
            # Load model using joblib
            logger.info(f"Loading model from: {self.model_path}")
            self.model = joblib.load(model_path)
            self._is_loaded = True
            logger.info(f"Model loaded successfully. Model type: {type(self.model).__name__}")
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise ValueError(f"Failed to load model from {self.model_path}: {str(e)}")
    
    def get_model(self) -> Any:
        """
        Get the loaded model
        
        Returns:
            Loaded model object
            
        Raises:
            ValueError: If model is not loaded
        """
        if not self._is_loaded or self.model is None:
            raise ValueError(
                "Model not loaded. Call load_model() first or ensure model loading succeeded."
            )
        return self.model
    
    def is_loaded(self) -> bool:
        """
        Check if model is loaded
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self._is_loaded and self.model is not None
    
    def reload_model(self) -> None:
        """
        Reload model from file (useful for model updates)
        """
        logger.info("Reloading model...")
        self.model = None
        self._is_loaded = False
        self.load_model()

