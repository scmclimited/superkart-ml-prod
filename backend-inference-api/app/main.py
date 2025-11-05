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

# Configure logging - ensure it goes to stdout/stderr for Docker
# Convert LOG_LEVEL string to uppercase to get the correct logging constant
# (entrypoint.sh converts it to lowercase, but we need uppercase for logging constants)
log_level_str = settings.LOG_LEVEL.upper()
# Map string to logging constant
log_level_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
log_level = log_level_map.get(log_level_str, logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Ensure logs go to stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 50)
logger.info("Starting SuperKart Backend Inference API")
logger.info(f"Log Level: {settings.LOG_LEVEL}")
logger.info(f"Model Path: {settings.MODEL_PATH}")
logger.info("=" * 50)

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
        logger.info(f"Starting model load from: {model_loader.model_path}")
        model_loader.load_model()
        logger.info("Model loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        logger.error("Application will start but will not be able to make predictions")
        # Don't raise - allow app to start even if model fails
        # Health check will report model_status as "not_loaded"
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        logger.error("Application will start but will not be able to make predictions")
        # Don't raise - allow app to start even if model fails
        # Health check will report model_status as "not_loaded"


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
    try:
        model_status = "loaded" if model_loader.is_loaded() else "not_loaded"
        # Always return healthy status - app is running even if model isn't loaded
        # Dependencies can check model_status if needed
        return {
            "status": "healthy",
            "model_status": model_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        # Still return healthy to avoid container restarts
        # The service is running, just model might not be loaded
        return {
            "status": "healthy",
            "model_status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
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