import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def validate_numerical_range(value: float, min_val: float, max_val: float, field_name: str) -> bool:
    """
    Validate numerical value is within acceptable range
    
    Args:
        value: Value to validate
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value
        field_name: Name of the field for error messages
        
    Returns:
        True if valid
        
    Raises:
        ValueError if out of range
    """
    if not min_val <= value <= max_val:
        raise ValueError(f"{field_name} must be between {min_val} and {max_val}, got {value}")
    return True


def format_prediction_response(predictions: np.ndarray, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Format predictions into standardized response
    
    Args:
        predictions: Array of predictions
        metadata: Optional metadata to include
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "predictions": predictions.tolist(),
        "count": len(predictions)
    }
    
    if metadata:
        response.update(metadata)
    
    return response


def calculate_statistics(predictions: np.ndarray) -> Dict[str, float]:
    """
    Calculate statistics for batch predictions
    
    Args:
        predictions: Array of predictions
        
    Returns:
        Dictionary with statistics
    """
    return {
        "mean": float(np.mean(predictions)),
        "median": float(np.median(predictions)),
        "std": float(np.std(predictions)),
        "min": float(np.min(predictions)),
        "max": float(np.max(predictions)),
        "total": float(np.sum(predictions))
    }