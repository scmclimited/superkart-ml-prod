"""
SuperKart Sales Forecasting Frontend

Streamlit-based user interface for predicting product-level revenue
in stores using historical and categorical inputs.
"""

__version__ = "1.0.0"
__author__ = "SuperKart ML Team"

from app.config import settings, get_settings

__all__ = [
    "settings",
    "get_settings"
]