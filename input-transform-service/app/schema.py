from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any


class ProductStoreInput(BaseModel):
    """
    Input schema for single product-store prediction
    """
    Product_Type: str = Field(..., description="Type of product")
    Store_Type: str = Field(..., description="Type of store")
    Store_Location_City_Type: str = Field(..., description="City tier classification")
    Store_Size: str = Field(..., description="Size of the store")
    Product_Sugar_Content: str = Field(..., description="Sugar content level")
    Product_Weight: float = Field(..., ge=0.0, le=50.0, description="Product weight in kg")
    Product_MRP: float = Field(..., ge=0.0, le=1000.0, description="Maximum Retail Price")
    Product_Allocated_Area: float = Field(..., ge=0.0, le=1.0, description="Display area allocation")
    Store_Establishment_Year: int = Field(..., ge=1950, le=2025, description="Year store was established")
    
    @validator('Product_Weight')
    def validate_weight(cls, v):
        if v < 0 or v > 50:
            raise ValueError('Product_Weight must be between 0 and 50')
        return v
    
    @validator('Product_MRP')
    def validate_mrp(cls, v):
        if v < 0 or v > 1000:
            raise ValueError('Product_MRP must be between 0 and 1000')
        return v
    
    @validator('Product_Allocated_Area')
    def validate_area(cls, v):
        if v < 0 or v > 1.0:
            raise ValueError('Product_Allocated_Area must be between 0 and 1.0')
        return v
    
    @validator('Store_Establishment_Year')
    def validate_year(cls, v):
        if v < 1950 or v > 2025:
            raise ValueError('Store_Establishment_Year must be between 1950 and 2025')
        return v


class PredictionResponse(BaseModel):
    """
    Response schema for single prediction
    """
    predicted_revenue: float
    timestamp: str
    input_data: Optional[Dict[str, Any]] = None


class BatchPredictionResponse(BaseModel):
    """
    Response schema for batch predictions
    """
    predictions: List[float]
    total_records: int
    timestamp: str
    statistics: Optional[Dict[str, float]] = None