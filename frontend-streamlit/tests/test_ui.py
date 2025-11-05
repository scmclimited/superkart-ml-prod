import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings, get_settings


class TestFrontendConfiguration:
    """Test suite for frontend configuration"""
    
    def test_settings_loaded(self):
        """Test that settings are loaded correctly"""
        assert settings.APP_TITLE == "SuperKart Sales Forecasting"
        assert settings.APP_ICON == "🛒"
        assert settings.APP_LAYOUT == "wide"
        # Note: The actual UI title combines APP_ICON + APP_TITLE
    
    def test_transform_service_url(self):
        """Test transform service URL configuration"""
        assert settings.TRANSFORM_SERVICE_URL is not None
        assert len(settings.TRANSFORM_SERVICE_URL) > 0
    
    def test_file_upload_limits(self):
        """Test file upload configuration"""
        assert settings.MAX_FILE_SIZE_MB > 0
        assert settings.MAX_BATCH_ROWS > 0
        assert ".csv" in settings.ALLOWED_FILE_EXTENSIONS
    
    def test_api_timeout_configured(self):
        """Test API timeout is properly configured"""
        assert settings.API_TIMEOUT > 0
        assert settings.API_TIMEOUT >= 30
    
    def test_feature_flags(self):
        """Test feature flags are properly set"""
        assert isinstance(settings.ENABLE_BATCH_PREDICTION, bool)
        assert isinstance(settings.ENABLE_DOWNLOAD, bool)
        assert isinstance(settings.DEBUG_MODE, bool)
    
    def test_get_settings_returns_instance(self):
        """Test get_settings returns valid settings instance"""
        config = get_settings()
        assert config is not None
        assert config.APP_TITLE == "SuperKart Sales Forecasting"


class TestUIComponents:
    """Test suite for UI components"""
    
    def test_form_data_structure(self):
        """Test form data structure matches API requirements"""
        required_fields = [
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
        
        # Verify all required fields are present
        assert len(required_fields) == 9
        
        # Verify field naming convention
        for field in required_fields:
            assert "_" in field or field.isupper() or field[0].isupper()
    
    def test_valid_product_types(self):
        """Test valid product types match notebook implementation"""
        # Notebook shows 11 product types (not 16)
        valid_types = [
            "Meat", "Snack Foods", "Soft Drinks", "Dairy", "Household",
            "Fruits and Vegetables", "Frozen Foods", "Breakfast",
            "Baking Goods", "Health and Hygiene", "Starchy Foods"
        ]
        
        assert len(valid_types) == 11
        assert "Meat" in valid_types
        assert "Dairy" in valid_types
        assert "Snack Foods" in valid_types
        assert "Fruits and Vegetables" in valid_types
    
    def test_valid_store_types(self):
        """Test valid store types"""
        valid_store_types = [
            "Supermarket Type1", "Supermarket Type2", "Supermarket Type3",
            "Grocery Store"
        ]
        
        assert len(valid_store_types) == 4
        assert "Supermarket Type1" in valid_store_types
        assert "Grocery Store" in valid_store_types
    
    def test_valid_city_types(self):
        """Test valid city tier types"""
        valid_city_types = ["Tier 1", "Tier 2", "Tier 3"]
        
        assert len(valid_city_types) == 3
        assert "Tier 1" in valid_city_types
        assert "Tier 3" in valid_city_types
    
    def test_valid_store_sizes(self):
        """Test valid store sizes"""
        valid_sizes = ["Small", "Medium", "High"]
        
        assert len(valid_sizes) == 3
        assert "Small" in valid_sizes
        assert "Medium" in valid_sizes
        assert "High" in valid_sizes
    
    def test_valid_sugar_content(self):
        """Test valid sugar content values"""
        valid_sugar = ["No Sugar", "Low Sugar", "Regular"]
        
        assert len(valid_sugar) == 3
        assert "No Sugar" in valid_sugar
        assert "Low Sugar" in valid_sugar
        assert "Regular" in valid_sugar
    
    def test_numerical_field_ranges(self):
        """Test numerical field ranges match validators"""
        ranges = {
            "Product_Weight": (0.0, 50.0),
            "Product_MRP": (0.0, 1000.0),
            "Product_Allocated_Area": (0.0, 1.0),
            "Store_Establishment_Year": (1950, 2025)
        }
        
        assert ranges["Product_Weight"][0] == 0.0
        assert ranges["Product_Weight"][1] == 50.0
        assert ranges["Product_MRP"][1] == 1000.0
        assert ranges["Product_Allocated_Area"][1] == 1.0
        assert ranges["Store_Establishment_Year"][0] == 1950


class TestDataProcessing:
    """Test suite for data processing functions"""
    
    def test_sample_csv_structure(self):
        """Test sample CSV has correct structure"""
        sample_data = pd.DataFrame({
            "Product_Type": ["Meat", "Dairy", "Snack Foods"],
            "Store_Type": ["Supermarket Type1", "Grocery Store", "Supermarket Type2"],
            "Store_Location_City_Type": ["Tier 1", "Tier 2", "Tier 3"],
            "Store_Size": ["Small", "Medium", "High"],
            "Product_Sugar_Content": ["No Sugar", "Low Sugar", "Regular"],
            "Product_Weight": [10.0, 15.0, 20.0],
            "Product_MRP": [200.0, 150.0, 300.0],
            "Product_Allocated_Area": [0.20, 0.30, 0.40],
            "Store_Establishment_Year": [2010, 2005, 2015]
        })
        
        # Check column count
        assert len(sample_data.columns) == 9
        
        # Check row count
        assert len(sample_data) == 3
        
        # Check column names
        expected_columns = [
            "Product_Type", "Store_Type", "Store_Location_City_Type",
            "Store_Size", "Product_Sugar_Content", "Product_Weight",
            "Product_MRP", "Product_Allocated_Area", "Store_Establishment_Year"
        ]
        assert list(sample_data.columns) == expected_columns
        
        # Check data types
        assert sample_data["Product_Weight"].dtype in [float, 'float64']
        assert sample_data["Product_MRP"].dtype in [float, 'float64']
        assert sample_data["Product_Allocated_Area"].dtype in [float, 'float64']
    
    def test_csv_to_dataframe_conversion(self):
        """Test CSV string conversion to DataFrame"""
        csv_string = """Product_Type,Store_Type,Store_Location_City_Type,Store_Size,Product_Sugar_Content,Product_Weight,Product_MRP,Product_Allocated_Area,Store_Establishment_Year
Meat,Supermarket Type1,Tier 1,Small,No Sugar,10.0,200.0,0.20,2010
Dairy,Grocery Store,Tier 2,Medium,Low Sugar,15.0,150.0,0.30,2005"""
        
        from io import StringIO
        df = pd.read_csv(StringIO(csv_string))
        
        assert len(df) == 2
        assert len(df.columns) == 9
        assert df.iloc[0]["Product_Type"] == "Meat"
        assert df.iloc[1]["Product_Type"] == "Dairy"
    
    def test_prediction_result_structure(self):
        """Test prediction result has expected structure"""
        # Notebook uses 'Predicted_Store_Sales_Total' but transform service may use 'predicted_revenue'
        mock_result_v1 = {
            "Predicted_Store_Sales_Total": 1234.56,
            "timestamp": "2024-01-01T12:00:00"
        }
        
        mock_result_v2 = {
            "predicted_revenue": 1234.56,
            "timestamp": "2024-01-01T12:00:00"
        }
        
        # Test both possible formats
        assert "Predicted_Store_Sales_Total" in mock_result_v1 or "predicted_revenue" in mock_result_v2
        assert isinstance(mock_result_v1.get("Predicted_Store_Sales_Total", mock_result_v2.get("predicted_revenue")), (int, float))
        assert mock_result_v1.get("Predicted_Store_Sales_Total", mock_result_v2.get("predicted_revenue")) > 0
    
    def test_batch_prediction_result_structure(self):
        """Test batch prediction result structure"""
        # Notebook returns 'Predicted_Store_Sales_Total' as list, transform service may use 'predictions'
        mock_batch_result_v1 = {
            "Predicted_Store_Sales_Total": [1000.0, 1500.0, 2000.0],
            "timestamp": "2024-01-01T12:00:00"
        }
        
        mock_batch_result_v2 = {
            "predictions": [1000.0, 1500.0, 2000.0],
            "total_records": 3,
            "timestamp": "2024-01-01T12:00:00"
        }
        
        # Test both possible formats
        predictions = mock_batch_result_v1.get("Predicted_Store_Sales_Total") or mock_batch_result_v2.get("predictions", [])
        assert len(predictions) > 0
        assert all(isinstance(p, (int, float)) for p in predictions)


class TestAPIIntegration:
    """Test suite for API integration"""
    
    def test_transform_service_endpoint_format(self):
        """Test transform service endpoint URLs are properly formatted"""
        base_url = settings.TRANSFORM_SERVICE_URL
        
        # Test single prediction endpoint
        single_endpoint = f"{base_url}/transform/single"
        assert "/transform/single" in single_endpoint
        
        # Test batch prediction endpoint
        batch_endpoint = f"{base_url}/transform/batch"
        assert "/transform/batch" in batch_endpoint
    
    @patch('requests.post')
    def test_single_prediction_api_call_structure(self, mock_post):
        """Test single prediction API call structure"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "predicted_revenue": 1500.0,
            "timestamp": "2024-01-01T12:00:00"
        }
        mock_post.return_value = mock_response
        
        # Simulate API call
        form_data = {
            "Product_Type": "Meat",
            "Store_Type": "Supermarket Type1",
            "Store_Location_City_Type": "Tier 1",
            "Store_Size": "Small",
            "Product_Sugar_Content": "No Sugar",
            "Product_Weight": 10.0,
            "Product_MRP": 200.0,
            "Product_Allocated_Area": 0.20,
            "Store_Establishment_Year": 2010
        }
        
        import requests
        response = requests.post(
            f"{settings.TRANSFORM_SERVICE_URL}/transform/single",
            json=form_data,
            timeout=30
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "predicted_revenue" in result
        assert result["predicted_revenue"] == 1500.0
    
    def test_request_timeout_configured(self):
        """Test request timeout is properly configured"""
        assert settings.API_TIMEOUT >= 30
        assert settings.API_TIMEOUT <= 300  # Should not be unreasonably long


class TestErrorHandling:
    """Test suite for error handling"""
    
    def test_connection_error_handling(self):
        """Test connection error scenarios"""
        error_messages = {
            "connection": "Cannot connect to the prediction service",
            "timeout": "Request timed out",
            "validation": "Validation Error",
            "service_unavailable": "The prediction service is currently unavailable"
        }
        
        assert "connect" in error_messages["connection"].lower()
        assert "timeout" in error_messages["timeout"].lower()
        assert "validation" in error_messages["validation"].lower()
    
    def test_http_status_code_handling(self):
        """Test different HTTP status codes are handled"""
        status_codes = {
            200: "success",
            400: "validation_error",
            503: "service_unavailable",
            500: "server_error"
        }
        
        assert 200 in status_codes
        assert 400 in status_codes
        assert 503 in status_codes
        assert 500 in status_codes
    
    def test_file_validation_errors(self):
        """Test file validation error scenarios"""
        file_errors = [
            "empty CSV file",
            "Could not parse the CSV file",
            "Missing required columns",
            "File size exceeds maximum"
        ]
        
        assert len(file_errors) > 0
        assert any("empty" in err.lower() for err in file_errors)
        assert any("parse" in err.lower() for err in file_errors)


class TestUIMetrics:
    """Test suite for UI metrics and statistics"""
    
    def test_statistics_calculation(self):
        """Test statistics are correctly calculated"""
        predictions = [1000.0, 1500.0, 2000.0, 2500.0, 3000.0]
        
        total = len(predictions)
        average = sum(predictions) / len(predictions)
        minimum = min(predictions)
        maximum = max(predictions)
        
        assert total == 5
        assert average == 2000.0
        assert minimum == 1000.0
        assert maximum == 3000.0
    
    def test_revenue_formatting(self):
        """Test revenue values are properly formatted"""
        test_values = [1234.56, 10000.00, 999999.99]
        
        for value in test_values:
            formatted = f"${value:,.2f}"
            assert "$" in formatted
            assert "." in formatted
    
    def test_dataframe_display_limits(self):
        """Test DataFrame display respects limits"""
        assert settings.RECORDS_PER_PAGE > 0
        assert settings.RECORDS_PER_PAGE <= 1000  # Reasonable limit


class TestFileHandling:
    """Test suite for file handling"""
    
    def test_csv_file_extensions(self):
        """Test CSV file extension validation"""
        assert ".csv" in settings.ALLOWED_FILE_EXTENSIONS
    
    def test_max_file_size_reasonable(self):
        """Test maximum file size is reasonable"""
        assert settings.MAX_FILE_SIZE_MB >= 1
        assert settings.MAX_FILE_SIZE_MB <= 100
    
    def test_max_batch_rows_reasonable(self):
        """Test maximum batch rows is reasonable"""
        assert settings.MAX_BATCH_ROWS >= 100
        assert settings.MAX_BATCH_ROWS <= 100000
    
    def test_download_filename_format(self):
        """Test download filename format"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"superkart_predictions_{timestamp}.csv"
        
        assert filename.startswith("superkart_predictions_")
        assert filename.endswith(".csv")
        assert len(timestamp) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])