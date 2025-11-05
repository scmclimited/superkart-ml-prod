# SuperKart ML Production System

A production-ready ML inference pipeline for revenue forecasting, featuring a Dockerized architecture with REST APIs and a Streamlit frontend. This system provides both single-row and batch prediction capabilities for product-level revenue predictions.

## Architecture Overview

This project consists of three microservices:

1. **backend-inference-api**: FastAPI service for ML model inference (single & batch predictions)
2. **input-transform-service**: FastAPI service for data validation and transformation
3. **frontend-streamlit**: Streamlit web interface for user interactions

---

## For Non-Technical Users

### Using the Hosted Frontend on Hugging Face

If you're not a developer, you can use the hosted version of this application on Hugging Face Spaces without any setup.

#### Step 1: Access the Application
- Navigate to the Hugging Face Space URL (https://huggingface.co/spaces/omoral02/RevenuePredictionFrontend)
- The web interface will open in your browser

#### Step 2: Single Row Prediction
1. Enter product and store information in the form fields:
   - **Product Type**: Select from dropdown (e.g., "Snack Foods", "Fruits and Vegetables", "Beverages")
   - **Store Type**: Select store type (e.g., "Supermarket Type1", "Grocery Store")
   - **Store Location City Type**: Select city tier (e.g., "Tier 1", "Tier 2", "Tier 3")
   - **Store Size**: Select size (e.g., "Small", "Medium", "Large")
   - **Product Sugar Content**: Select sugar level (e.g., "Regular", "Low")
   - **Product Weight**: Enter weight in kg (0-50)
   - **Product MRP**: Enter Maximum Retail Price (0-1000)
   - **Product Allocated Area**: Enter display area allocation (0-1.0)
   - **Store Establishment Year**: Enter year (1950-2025)

2. Click **"Predict Revenue"** button
3. View the predicted revenue result

#### Step 3: Batch Prediction
1. Prepare a CSV file with the required columns (see sample file below)
2. Click **"Upload CSV File"** button
3. Select your CSV file
4. Wait for processing
5. Download the results with predictions

#### Sample CSV Format

For batch predictions, create a CSV file with these exact column names:

```csv
Product_Type,Store_Type,Store_Location_City_Type,Store_Size,Product_Sugar_Content,Product_Weight,Product_MRP,Product_Allocated_Area,Store_Establishment_Year
Snack Foods,Supermarket Type1,Tier 1,Medium,Regular,150.0,249.0,0.4,2010
Fruits and Vegetables,Supermarket Type2,Tier 1,Large,Regular,250.0,199.0,0.6,2008
```

A sample file (`batch_sample.csv`) is available in the `sample_data` directory of this project for reference.

#### Understanding the Results

- **Single Prediction**: Returns a predicted revenue value for the input combination
- **Batch Prediction**: Returns a CSV file with predictions for each row in your input file

#### Viewing the Model Documentation

- Open the HTML file `Full_Code_SuperKart_Model.html` in the project root directory
- This contains the complete Jupyter notebook analysis and model documentation
- Open it in any web browser to view the model development process

---

## For Technical Users / Developers

### Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (version 20.10 or later)
  - Download from: https://www.docker.com/products/docker-desktop
  - Ensure Docker Desktop is running before proceeding

- **Docker Compose** (usually included with Docker Desktop)
  - Verify with: `docker-compose --version`

- **Git** (optional, for cloning the repository)

- **Model File**: Place your pretrained model file (`superkart_model.joblib`) in:
  ```
  backend-inference-api/models/superkart_model.joblib
  ```

### Local Development Setup

#### Step 1: Clone/Navigate to Project Directory

```bash
cd superkart-ml-prod
```

#### Step 2: Verify Model File Exists

Ensure your model file is present:
```bash
ls backend-inference-api/models/superkart_model.joblib
```

#### Step 3: Start All Services

Build and start all services using docker-compose:

```bash
docker-compose up --build
```

This will:
- Build Docker images for all three services
- Start services in dependency order (backend → transform → frontend)
- Display logs from all services

**To run in detached mode (background):**
```bash
docker-compose up -d --build
```

#### Step 4: Verify Services Are Running

Check service status:
```bash
docker-compose ps
```

All services should show `Up` status. Wait approximately 40-60 seconds for all services to become healthy.

### Service URLs

Once services are running, access them at:

- **Backend Inference API**: http://localhost:8000
  - Health Check: http://localhost:8000/health
  - API Documentation: http://localhost:8000/docs
  - Interactive API: http://localhost:8000/redoc

- **Input Transform Service**: http://localhost:8030
  - Health Check: http://localhost:8030/health
  - API Documentation: http://localhost:8030/docs

- **Frontend Streamlit**: http://localhost:8501
  - Web Interface: http://localhost:8501

### Testing the API

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Single Prediction Example

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Product_Type": "Snack Foods",
    "Store_Type": "Supermarket Type1",
    "Store_Location_City_Type": "Tier 1",
    "Store_Size": "Medium",
    "Product_Sugar_Content": "Regular",
    "Product_Weight": 150.0,
    "Product_MRP": 249.0,
    "Product_Allocated_Area": 0.4,
    "Store_Establishment_Year": 2010
  }'
```

#### Batch Prediction Example

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "Product_Type": "Snack Foods",
        "Store_Type": "Supermarket Type1",
        "Store_Location_City_Type": "Tier 1",
        "Store_Size": "Medium",
        "Product_Sugar_Content": "Regular",
        "Product_Weight": 150.0,
        "Product_MRP": 249.0,
        "Product_Allocated_Area": 0.4,
        "Store_Establishment_Year": 2010
      },
      {
        "Product_Type": "Fruits and Vegetables",
        "Store_Type": "Supermarket Type2",
        "Store_Location_City_Type": "Tier 1",
        "Store_Size": "Large",
        "Product_Sugar_Content": "Regular",
        "Product_Weight": 250.0,
        "Product_MRP": 199.0,
        "Product_Allocated_Area": 0.6,
        "Store_Establishment_Year": 2008
      }
    ]
  }'
```

#### Using the Transform Service (with File Upload)

```bash
curl -X POST http://localhost:8030/transform/batch \
  -F "file=@sample_data/batch_sample.csv"
```

### Common Docker Commands

#### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend-inference-api
docker-compose logs -f input-transform-service
docker-compose logs -f frontend-streamlit
```

#### Stop Services

```bash
docker-compose down
```

#### Stop and Remove Volumes

```bash
docker-compose down -v
```

#### Rebuild Specific Service

```bash
docker-compose up --build backend-inference-api
```

#### Restart Services

```bash
docker-compose restart
```

### Troubleshooting

#### Port Already in Use

If you get port binding errors:
```bash
# Check what's using the port (Linux/Mac)
lsof -i :8000
lsof -i :8030
lsof -i :8501

# On Windows, use:
netstat -ano | findstr :8000
netstat -ano | findstr :8030
netstat -ano | findstr :8501

# Kill the process or change ports in docker-compose.yml
```

#### Model File Not Found

Ensure the model file exists:
```bash
ls -la backend-inference-api/models/superkart_model.joblib
```

If missing, place your trained model file in that location.

#### Health Check Failures

Services may take 40-60 seconds to become healthy. Check logs:
```bash
docker-compose logs backend-inference-api
```

#### Permission Issues (Linux/Mac)

If you encounter permission errors:
```bash
sudo docker-compose up --build
```

#### Viewing Container Logs Directly

```bash
docker logs superkart-backend-inference
docker logs superkart-transform-service
docker logs superkart-frontend
```

### Development Workflow

1. **Make code changes** to any service
2. **Rebuild the specific service**:
   ```bash
   docker-compose up --build <service-name>
   ```
3. **Or rebuild all services**:
   ```bash
   docker-compose up --build
   ```

### Project Structure

```
superkart-ml-prod/
├── backend-inference-api/     # ML inference service
│   ├── app/                    # Application code
│   ├── models/                 # Model files directory
│   ├── Dockerfile
│   └── requirements.txt
├── input-transform-service/   # Data transformation service
│   ├── app/                    # Application code
│   ├── Dockerfile
│   └── requirements.txt
├── frontend-streamlit/        # Streamlit web interface
│   ├── app/                    # Application code
│   ├── Dockerfile
│   └── requirements.txt
├── sample_data/               # Sample CSV files
│   └── batch_sample.csv
├── docker-compose.yml          # Service orchestration
├── Full_Code_SuperKart_Model_Omar_Morales (1).html  # Model documentation
└── README.md                   # This file
```

### API Endpoints Reference

#### Backend Inference API (Port 8000)

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /model/info` - Model information
- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch prediction

#### Input Transform Service (Port 8030)

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /schema` - Input schema definition
- `POST /transform/single` - Transform and predict single row
- `POST /transform/batch` - Transform and predict batch (CSV upload)

### Environment Variables

Key environment variables can be set in `docker-compose.yml`:

- `MODEL_PATH`: Path to model file (default: `/app/models/superkart_model.joblib`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `WORKERS`: Number of worker processes (default: `4` for backend, `2` for transform)

### Performance Considerations

- Backend API is configured with 4 workers for concurrent requests
- Transform service uses 2 workers
- Resource limits are set in docker-compose.yml
- For production, adjust resources based on infrastructure

---

## Support

For issues or questions:
1. Check the logs using `docker-compose logs`
2. Verify all prerequisites are installed
3. Ensure model file is in the correct location
4. Review the HTML documentation file for model details

---

## License

See LICENSE file for details.
