from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import logging
from datetime import datetime

from app.model_loader import ModelLoader
from app.predict import Predictor
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SuperKart Sales Forecasting API",
    description="Backend inference API for predicting product-level revenue",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model and predictor
model_loader = ModelLoader()
predictor = Predictor(model_loader)


class PredictionInput(BaseModel):
    Product_Type: str
    Store_Type: str
    Store_Location_City_Type: str
    Store_Size: str
    Product_Sugar_Content: str
    Product_Weight: float
    Product_MRP: float
    Product_Allocated_Area: float
    Store_Establishment_Year: int


class PredictionOutput(BaseModel):
    predicted_revenue: float
    confidence_interval: Optional[dict] = None
    timestamp: str


class BatchPredictionInput(BaseModel):
    data: List[PredictionInput]


class BatchPredictionOutput(BaseModel):
    predictions: List[PredictionOutput]
    total_records: int
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    try:
        model_loader.load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SuperKart Sales Forecasting API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = "loaded" if model_loader.model is not None else "not_loaded"
    return {
        "status": "healthy",
        "model_status": model_status,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict", response_model=PredictionOutput)
async def predict_single(input_data: PredictionInput):
    """
    Predict revenue for a single product-store combination
    """
    try:
        # Convert to DataFrame (using model_dump() for Pydantic v2)
        df = pd.DataFrame([input_data.model_dump()])
        
        # Make prediction
        prediction = predictor.predict(df)
        
        return PredictionOutput(
            predicted_revenue=float(prediction[0]),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionOutput)
async def predict_batch(input_data: BatchPredictionInput):
    """
    Predict revenue for multiple product-store combinations
    """
    try:
        # Convert to DataFrame (using model_dump() for Pydantic v2)
        data_dicts = [item.model_dump() for item in input_data.data]
        df = pd.DataFrame(data_dicts)
        
        # Make predictions
        predictions = predictor.predict(df)
        
        # Format output
        prediction_outputs = [
            PredictionOutput(
                predicted_revenue=float(pred),
                timestamp=datetime.now().isoformat()
            )
            for pred in predictions
        ]
        
        return BatchPredictionOutput(
            predictions=prediction_outputs,
            total_records=len(predictions),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/model/info")
async def model_info():
    """Get model information"""
    if model_loader.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": type(model_loader.model).__name__,
        "model_loaded": True,
        "expected_features": [
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
    }