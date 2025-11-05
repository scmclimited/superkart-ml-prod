import pytest
import pandas as pd
from app.validators import InputValidator


class TestInputValidator:
    """Test suite for InputValidator class"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance for testing"""
        return InputValidator()
    
    @pytest.fixture
    def valid_single_input(self):
        """Valid single input record"""
        return {
            "Product_Type": "Meat",
            "Store_Type": "Supermarket Type1",
            "Store_Location_City_Type": "Tier 1",
            "Store_Size": "Small",
            "Product_Sugar_Content": "No Sugar",
            "Product_Weight": 10.0,
            "Product_MRP": 200.0,
            "Product_Allocated_Area": 0.2,
            "Store_Establishment_Year": 2010
        }
    
    @pytest.fixture
    def valid_batch_df(self):
        """Valid batch DataFrame"""
        data = {
            "Product_Type": ["Meat", "Dairy", "Snack Foods"],
            "Store_Type": ["Supermarket Type1", "Grocery Store", "Supermarket Type2"],
            "Store_Location_City_Type": ["Tier 1", "Tier 2", "Tier 3"],
            "Store_Size": ["Small", "Medium", "High"],
            "Product_Sugar_Content": ["No Sugar", "Low Sugar", "Regular"],
            "Product_Weight": [10.0, 15.0, 20.0],
            "Product_MRP": [200.0, 150.0, 300.0],
            "Product_Allocated_Area": [0.2, 0.3, 0.4],
            "Store_Establishment_Year": [2010, 2005, 2015]
        }
        return pd.DataFrame(data)
    
    def test_validate_single_valid_input(self, validator, valid_single_input):
        """Test validation of valid single input"""
        assert validator.validate_single(valid_single_input) is True
    
    def test_validate_single_missing_fields(self, validator):
        """Test validation fails with missing fields"""
        incomplete_data = {
            "Product_Type": "Meat",
            "Store_Type": "Supermarket Type1"
        }
        with pytest.raises(ValueError, match="Missing required fields"):
            validator.validate_single(incomplete_data)
    
    def test_validate_single_invalid_product_type(self, validator, valid_single_input):
        """Test validation fails with invalid Product_Type"""
        valid_single_input["Product_Type"] = "Invalid Type"
        with pytest.raises(ValueError, match="Invalid Product_Type"):
            validator.validate_single(valid_single_input)
    
    def test_validate_single_invalid_store_type(self, validator, valid_single_input):
        """Test validation fails with invalid Store_Type"""
        valid_single_input["Store_Type"] = "Invalid Store"
        with pytest.raises(ValueError, match="Invalid Store_Type"):
            validator.validate_single(valid_single_input)
    
    def test_validate_single_out_of_range_weight(self, validator, valid_single_input):
        """Test validation fails with out of range Product_Weight"""
        valid_single_input["Product_Weight"] = 100.0
        with pytest.raises(ValueError, match="Product_Weight must be between"):
            validator.validate_single(valid_single_input)
    
    def test_validate_single_out_of_range_mrp(self, validator, valid_single_input):
        """Test validation fails with out of range Product_MRP"""
        valid_single_input["Product_MRP"] = 2000.0
        with pytest.raises(ValueError, match="Product_MRP must be between"):
            validator.validate_single(valid_single_input)
    
    def test_validate_single_invalid_year(self, validator, valid_single_input):
        """Test validation fails with invalid establishment year"""
        valid_single_input["Store_Establishment_Year"] = 1900
        with pytest.raises(ValueError, match="Store_Establishment_Year must be between"):
            validator.validate_single(valid_single_input)
    
    def test_validate_batch_valid_data(self, validator, valid_batch_df):
        """Test batch validation with valid DataFrame"""
        assert validator.validate_batch(valid_batch_df) is True
    
    def test_validate_batch_missing_columns(self, validator):
        """Test batch validation fails with missing columns"""
        incomplete_df = pd.DataFrame({
            "Product_Type": ["Meat"],
            "Store_Type": ["Supermarket Type1"]
        })
        with pytest.raises(ValueError, match="Missing required columns"):
            validator.validate_batch(incomplete_df)
    
    def test_validate_batch_empty_dataframe(self, validator):
        """Test batch validation fails with empty DataFrame"""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="DataFrame is empty"):
            validator.validate_batch(empty_df)
    
    def test_normalize_sugar_content(self, validator):
        """Test sugar content normalization"""
        assert validator._normalize_sugar_content("reg") == "Regular"
        assert validator._normalize_sugar_content("REG") == "Regular"
        assert validator._normalize_sugar_content("LF") == "Low Sugar"
        assert validator._normalize_sugar_content("low fat") == "Low Sugar"
        assert validator._normalize_sugar_content("no sugar") == "No Sugar"
        assert validator._normalize_sugar_content("NS") == "No Sugar"
        assert validator._normalize_sugar_content("Regular") == "Regular"
    
    def test_get_valid_values(self, validator):
        """Test getting valid values dictionary"""
        valid_values = validator.get_valid_values()
        
        assert "Product_Type" in valid_values
        assert "Store_Type" in valid_values
        assert "Product_Weight" in valid_values
        assert "Product_MRP" in valid_values
        
        assert valid_values["Product_Type"]["type"] == "categorical"
        assert valid_values["Product_Weight"]["type"] == "float"
        assert valid_values["Product_Weight"]["min"] == 0.0
        assert valid_values["Product_Weight"]["max"] == 50.0
    
    def test_validate_and_report_success(self, validator, valid_batch_df):
        """Test validation report with valid data"""
        report = validator.validate_and_report(valid_batch_df)
        
        assert report["status"] == "success"
        assert report["total_rows"] == 3
        assert report["valid_rows"] == 3
        assert report["invalid_rows"] == 0
        assert len(report["errors"]) == 0
    
    def test_validate_and_report_with_errors(self, validator):
        """Test validation report with invalid data"""
        invalid_df = pd.DataFrame({
            "Product_Type": ["Invalid Type", "Meat"],
            "Store_Type": ["Supermarket Type1", "Invalid Store"],
            "Store_Location_City_Type": ["Tier 1", "Tier 2"],
            "Store_Size": ["Small", "Medium"],
            "Product_Sugar_Content": ["No Sugar", "Regular"],
            "Product_Weight": [10.0, 100.0],
            "Product_MRP": [200.0, 150.0],
            "Product_Allocated_Area": [0.2, 0.3],
            "Store_Establishment_Year": [2010, 2005]
        })
        
        report = validator.validate_and_report(invalid_df)
        
        assert report["status"] == "failed"
        assert report["total_rows"] == 2
        assert report["invalid_rows"] > 0
        assert len(report["errors"]) > 0
    
    def test_get_validation_summary(self, validator, valid_batch_df):
        """Test getting validation summary"""
        summary = validator.get_validation_summary(valid_batch_df)
        
        assert summary["total_rows"] == 3
        assert summary["column_count"] == 9
        assert len(summary["missing_columns"]) == 0
        assert len(summary["null_counts"]) == 0
        assert len(summary["invalid_categorical_counts"]) == 0
        assert len(summary["out_of_range_counts"]) == 0
    
    def test_validate_batch_with_null_values(self, validator, valid_batch_df):
        """Test batch validation detects null values"""
        valid_batch_df.loc[0, "Product_Weight"] = None
        
        with pytest.raises(ValueError, match="Null values"):
            validator.validate_batch(valid_batch_df)
    
    def test_validate_batch_multiple_errors_per_row(self, validator):
        """Test batch validation reports multiple errors per row"""
        invalid_df = pd.DataFrame({
            "Product_Type": ["Invalid Type"],
            "Store_Type": ["Invalid Store"],
            "Store_Location_City_Type": ["Tier 1"],
            "Store_Size": ["Small"],
            "Product_Sugar_Content": ["No Sugar"],
            "Product_Weight": [100.0],
            "Product_MRP": [2000.0],
            "Product_Allocated_Area": [0.2],
            "Store_Establishment_Year": [1900]
        })
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_batch(invalid_df)
        
        error_message = str(exc_info.value)
        assert "Invalid Product_Type" in error_message
        assert "Invalid Store_Type" in error_message
        assert "out of range" in error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])