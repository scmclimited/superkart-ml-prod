import pandas as pd
import numpy as np
import logging
from typing import List

from app.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class Predictor:
    """
    Handles prediction logic using the loaded model
    """
    
    def __init__(self, model_loader: ModelLoader):
        self.model_loader = model_loader
        self.expected_columns = [
            "Product_Type",
            "Store_Type",
            "Store_Location_City_Type",
            "Store_Size",
            "Product_Sugar_Content",
            "Product_Weight",
            "Product_MRP",
            "Product_Allocated_Area",
            "Store_Establishment_Year"
        ]
    
    def validate_input(self, df: pd.DataFrame) -> bool:
        """
        Validate input DataFrame has required columns
        
        Args:
            df: Input DataFrame
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        missing_cols = set(self.expected_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return True
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on input data
        
        Args:
            df: Input DataFrame with required features
            
        Returns:
            Array of predictions
        """
        try:
            # Validate input
            self.validate_input(df)
            
            # Get model
            model = self.model_loader.get_model()
            
            # Ensure columns are in correct order
            df = df[self.expected_columns]
            
            # Make predictions
            predictions = model.predict(df)
            
            logger.info(f"Generated {len(predictions)} predictions")
            
            return predictions
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    