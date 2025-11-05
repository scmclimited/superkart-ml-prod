from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import logging
from datetime import datetime
import io
import json

from app.schema import ProductStoreInput, PredictionResponse, BatchPredictionResponse
from app.transform import DataTransformer
from app.validators import InputValidator
from app.config import settings
import requests

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SuperKart Input Transform Service",
    description="Validates and transforms input data for the inference API",
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

# Initialize transformer and validator
transformer = DataTransformer()
validator = InputValidator()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SuperKart Input Transform Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/transform/single", response_model=PredictionResponse)
async def transform_and_predict_single(input_data: ProductStoreInput):
    """
    Validate, transform single input and get prediction
    """
    try:
        # Validate input
        validator.validate_single(input_data.dict())
        
        # Transform to DataFrame
        df = transformer.json_to_dataframe([input_data.dict()])
        
        # Prepare request for inference API
        inference_data = {
            "Product_Type": df.iloc[0]["Product_Type"],
            "Store_Type": df.iloc[0]["Store_Type"],
            "Store_Location_City_Type": df.iloc[0]["Store_Location_City_Type"],
            "Store_Size": df.iloc[0]["Store_Size"],
            "Product_Sugar_Content": df.iloc[0]["Product_Sugar_Content"],
            "Product_Weight": float(df.iloc[0]["Product_Weight"]),
            "Product_MRP": float(df.iloc[0]["Product_MRP"]),
            "Product_Allocated_Area": float(df.iloc[0]["Product_Allocated_Area"]),
            "Store_Establishment_Year": int(df.iloc[0]["Store_Establishment_Year"])
        }
        
        # Call inference API
        response = requests.post(
            f"{settings.INFERENCE_API_URL}/predict",
            json=inference_data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Inference API request failed")
        
        result = response.json()
        
        return PredictionResponse(
            predicted_revenue=result["predicted_revenue"],
            timestamp=result["timestamp"],
            input_data=input_data.dict()
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        logger.error(f"Inference API error: {str(e)}")
        raise HTTPException(status_code=503, detail="Inference API unavailable")
    except Exception as e:
        logger.error(f"Transform error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transform failed: {str(e)}")


@app.post("/transform/batch", response_model=BatchPredictionResponse)
async def transform_and_predict_batch(file: UploadFile = File(...)):
    """
    Validate and transform batch CSV input and get predictions
    """
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        logger.info(f"Received batch file with {len(df)} records")
        
        # Validate batch
        validator.validate_batch(df)
        
        # Transform data
        transformed_df = transformer.transform_dataframe(df)
        
        # Prepare batch request for inference API
        batch_data = []
        for _, row in transformed_df.iterrows():
            batch_data.append({
                "Product_Type": row["Product_Type"],
                "Store_Type": row["Store_Type"],
                "Store_Location_City_Type": row["Store_Location_City_Type"],
                "Store_Size": row["Store_Size"],
                "Product_Sugar_Content": row["Product_Sugar_Content"],
                "Product_Weight": float(row["Product_Weight"]),
                "Product_MRP": float(row["Product_MRP"]),
                "Product_Allocated_Area": float(row["Product_Allocated_Area"]),
                "Store_Establishment_Year": int(row["Store_Establishment_Year"])
            })
        
        # Call inference API
        response = requests.post(
            f"{settings.INFERENCE_API_URL}/predict/batch",
            json={"data": batch_data},
            timeout=60
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Batch inference API request failed")
        
        result = response.json()
        
        return BatchPredictionResponse(
            predictions=[pred["predicted_revenue"] for pred in result["predictions"]],
            total_records=result["total_records"],
            timestamp=result["timestamp"]
        )
    
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Empty CSV file")
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        logger.error(f"Inference API error: {str(e)}")
        raise HTTPException(status_code=503, detail="Inference API unavailable")
    except Exception as e:
        logger.error(f"Batch transform error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch transform failed: {str(e)}")


@app.get("/schema")
async def get_schema():
    """Get expected input schema"""
    return {
        "required_fields": [
            "Product_Type",
            "Store_Type",
            "Store_Location_City_Type",
            "Store_Size",
            "Product_Sugar_Content",
            "Product_Weight",
            "Product_MRP",
            "Product_Allocated_Area",
            "Store_Establishment_Year"
        ],
        "field_types": {
            "Product_Type": "string (categorical)",
            "Store_Type": "string (categorical)",
            "Store_Location_City_Type": "string (categorical)",
            "Store_Size": "string (categorical)",
            "Product_Sugar_Content": "string (categorical)",
            "Product_Weight": "float",
            "Product_MRP": "float",
            "Product_Allocated_Area": "float",
            "Store_Establishment_Year": "integer"
        },
        "valid_values": validator.get_valid_values()
    }