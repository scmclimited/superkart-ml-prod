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
    # Ranges based on training data EDA (describe() output)
    # Product_Weight: min=4.0, max=22.0
    Product_Weight: float = Field(..., ge=4.0, le=22.0, description="Product weight in kg")
    # Product_MRP: min=31.0, max=266.0
    Product_MRP: float = Field(..., ge=31.0, le=266.0, description="Maximum Retail Price")
    # Product_Allocated_Area: min=0.004, max=0.298
    Product_Allocated_Area: float = Field(..., ge=0.004, le=0.298, description="Display area allocation")
    # Store_Establishment_Year: min=1987, max=2009
    Store_Establishment_Year: int = Field(..., ge=1987, le=2009, description="Year store was established")
    
    @validator('Product_Weight')
    def validate_weight(cls, v):
        if v < 4.0 or v > 22.0:
            raise ValueError('Product_Weight must be between 4.0 and 22.0 kg (based on training data range)')
        return v
    
    @validator('Product_MRP')
    def validate_mrp(cls, v):
        if v < 31.0 or v > 266.0:
            raise ValueError('Product_MRP must be between 31.0 and 266.0 (based on training data range)')
        return v
    
    @validator('Product_Allocated_Area')
    def validate_area(cls, v):
        if v < 0.004 or v > 0.298:
            raise ValueError('Product_Allocated_Area must be between 0.004 and 0.298 (based on training data range)')
        return v
    
    @validator('Store_Establishment_Year')
    def validate_year(cls, v):
        if v < 1987 or v > 2009:
            raise ValueError('Store_Establishment_Year must be between 1987 and 2009 (based on training data range)')
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