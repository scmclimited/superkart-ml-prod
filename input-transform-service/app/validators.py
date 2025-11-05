import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates input data against schema and business rules
    """
    
    def __init__(self):
        # Define valid categorical values
        self.valid_product_types = [
            "Meat", "Snack Foods", "Soft Drinks", "Dairy", "Household",
            "Fruits and Vegetables", "Frozen Foods", "Breakfast",
            "Baking Goods", "Health and Hygiene", "Starchy Foods",
            "Breads", "Canned", "Seafood", "Hard Drinks", "Others"
        ]
        
        self.valid_store_types = [
            "Supermarket Type1", "Supermarket Type2", "Supermarket Type3",
            "Grocery Store"
        ]
        
        self.valid_city_types = ["Tier 1", "Tier 2", "Tier 3"]
        
        self.valid_store_sizes = ["Small", "Medium", "High"]
        
        self.valid_sugar_content = ["No Sugar", "Low Sugar", "Regular"]
        
        # Define numerical ranges
        self.numerical_ranges = {
            "Product_Weight": (0.0, 50.0),
            "Product_MRP": (0.0, 1000.0),
            "Product_Allocated_Area": (0.0, 1.0),
            "Store_Establishment_Year": (1950, 2025)
        }
        
        self.required_fields = [
            "Product_Type", "Store_Type", "Store_Location_City_Type",
            "Store_Size", "Product_Sugar_Content", "Product_Weight",
            "Product_MRP", "Product_Allocated_Area", "Store_Establishment_Year"
        ]
    
    def validate_single(self, data: Dict[str, Any]) -> bool:
        """
        Validate single input record
        
        Args:
            data: Dictionary with input data
            
        Returns:
            True if valid
            
        Raises:
            ValueError if validation fails
        """
        # Check required fields
        missing_fields = set(self.required_fields) - set(data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Validate categorical fields
        if data["Product_Type"] not in self.valid_product_types:
            raise ValueError(f"Invalid Product_Type: {data['Product_Type']}. Must be one of {self.valid_product_types}")
        
        if data["Store_Type"] not in self.valid_store_types:
            raise ValueError(f"Invalid Store_Type: {data['Store_Type']}. Must be one of {self.valid_store_types}")
        
        if data["Store_Location_City_Type"] not in self.valid_city_types:
            raise ValueError(f"Invalid Store_Location_City_Type: {data['Store_Location_City_Type']}. Must be one of {self.valid_city_types}")
        
        if data["Store_Size"] not in self.valid_store_sizes:
            raise ValueError(f"Invalid Store_Size: {data['Store_Size']}. Must be one of {self.valid_store_sizes}")
        
        # Normalize and validate sugar content
        sugar_content = data["Product_Sugar_Content"]
        normalized_sugar = self._normalize_sugar_content(sugar_content)
        if normalized_sugar not in self.valid_sugar_content:
            raise ValueError(f"Invalid Product_Sugar_Content: {sugar_content}")
        
        # Validate numerical fields
        for field, (min_val, max_val) in self.numerical_ranges.items():
            value = data[field]
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"{field} must be a number, got {value}")
            
            if not min_val <= value <= max_val:
                raise ValueError(f"{field} must be between {min_val} and {max_val}, got {value}")
        
        return True
    
    def validate_batch(self, df: pd.DataFrame) -> bool:
        """
        Validate batch DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            True if valid
            
        Raises:
            ValueError if validation fails
        """
        # Check required columns
        missing_cols = set(self.required_fields) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Check for empty DataFrame
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        # Collect all validation errors
        validation_errors = []
        
        # Validate each row
        for idx, row in df.iterrows():
            row_errors = []
            
            # Validate Product_Type
            if row["Product_Type"] not in self.valid_product_types:
                row_errors.append(f"Invalid Product_Type: {row['Product_Type']}")
            
            # Validate Store_Type
            if row["Store_Type"] not in self.valid_store_types:
                row_errors.append(f"Invalid Store_Type: {row['Store_Type']}")
            
            # Validate Store_Location_City_Type
            if row["Store_Location_City_Type"] not in self.valid_city_types:
                row_errors.append(f"Invalid Store_Location_City_Type: {row['Store_Location_City_Type']}")
            
            # Validate Store_Size
            if row["Store_Size"] not in self.valid_store_sizes:
                row_errors.append(f"Invalid Store_Size: {row['Store_Size']}")
            
            # Validate Product_Sugar_Content
            normalized_sugar = self._normalize_sugar_content(row["Product_Sugar_Content"])
            if normalized_sugar not in self.valid_sugar_content:
                row_errors.append(f"Invalid Product_Sugar_Content: {row['Product_Sugar_Content']}")
            
            # Validate numerical fields
            for field, (min_val, max_val) in self.numerical_ranges.items():
                try:
                    value = float(row[field])
                    if not min_val <= value <= max_val:
                        row_errors.append(f"{field}={value} is out of range [{min_val}, {max_val}]")
                except (ValueError, TypeError):
                    row_errors.append(f"{field} must be numeric, got: {row[field]}")
            
            # Check for null values
            null_fields = [col for col in self.required_fields if pd.isna(row[col])]
            if null_fields:
                row_errors.append(f"Null values in: {null_fields}")
            
            # If row has errors, add to validation errors
            if row_errors:
                validation_errors.append(f"Row {idx + 1}: {'; '.join(row_errors)}")
        
        # If there are validation errors, raise them all at once
        if validation_errors:
            error_msg = "Validation failed for the following rows:\n" + "\n".join(validation_errors[:10])
            if len(validation_errors) > 10:
                error_msg += f"\n... and {len(validation_errors) - 10} more errors"
            raise ValueError(error_msg)
        
        logger.info(f"Validated {len(df)} records successfully")
        return True
    
    def _normalize_sugar_content(self, value: str) -> str:
        """
        Normalize sugar content values to standard format
        
        Args:
            value: Raw sugar content value
            
        Returns:
            Normalized sugar content value
        """
        # Mapping for common variations
        normalization_map = {
            'reg': 'Regular',
            'REG': 'Regular',
            'regular': 'Regular',
            'Regular': 'Regular',
            'low fat': 'Low Sugar',
            'Low Fat': 'Low Sugar',
            'LF': 'Low Sugar',
            'low sugar': 'Low Sugar',
            'Low Sugar': 'Low Sugar',
            'no sugar': 'No Sugar',
            'No Sugar': 'No Sugar',
            'NS': 'No Sugar'
        }
        
        # Return normalized value or original if not in map
        return normalization_map.get(str(value).strip(), str(value).strip())
    
    def get_valid_values(self) -> Dict[str, Any]:
        """
        Get dictionary of valid values for all fields
        
        Returns:
            Dictionary with valid values and ranges for each field
        """
        return {
            "Product_Type": {
                "type": "categorical",
                "valid_values": self.valid_product_types
            },
            "Store_Type": {
                "type": "categorical",
                "valid_values": self.valid_store_types
            },
            "Store_Location_City_Type": {
                "type": "categorical",
                "valid_values": self.valid_city_types
            },
            "Store_Size": {
                "type": "categorical",
                "valid_values": self.valid_store_sizes
            },
            "Product_Sugar_Content": {
                "type": "categorical",
                "valid_values": self.valid_sugar_content,
                "note": "Variants like 'reg', 'REG', 'LF' are auto-normalized"
            },
            "Product_Weight": {
                "type": "float",
                "min": self.numerical_ranges["Product_Weight"][0],
                "max": self.numerical_ranges["Product_Weight"][1],
                "unit": "kg"
            },
            "Product_MRP": {
                "type": "float",
                "min": self.numerical_ranges["Product_MRP"][0],
                "max": self.numerical_ranges["Product_MRP"][1],
                "unit": "currency"
            },
            "Product_Allocated_Area": {
                "type": "float",
                "min": self.numerical_ranges["Product_Allocated_Area"][0],
                "max": self.numerical_ranges["Product_Allocated_Area"][1],
                "unit": "ratio (0-1)"
            },
            "Store_Establishment_Year": {
                "type": "integer",
                "min": int(self.numerical_ranges["Store_Establishment_Year"][0]),
                "max": int(self.numerical_ranges["Store_Establishment_Year"][1]),
                "unit": "year"
            }
        }
    
    def validate_and_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame and return detailed report
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with validation results and statistics
        """
        report = {
            "total_rows": len(df),
            "valid_rows": 0,
            "invalid_rows": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            self.validate_batch(df)
            report["valid_rows"] = len(df)
            report["status"] = "success"
        except ValueError as e:
            report["status"] = "failed"
            report["errors"].append(str(e))
            # Count invalid rows from error message
            error_lines = str(e).split('\n')
            report["invalid_rows"] = len([line for line in error_lines if line.startswith("Row")])
            report["valid_rows"] = report["total_rows"] - report["invalid_rows"]
        
        return report
    
    def get_validation_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics about data quality without raising errors
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with validation summary
        """
        summary = {
            "total_rows": len(df),
            "column_count": len(df.columns),
            "missing_columns": list(set(self.required_fields) - set(df.columns)),
            "extra_columns": list(set(df.columns) - set(self.required_fields)),
            "null_counts": {},
            "invalid_categorical_counts": {},
            "out_of_range_counts": {}
        }
        
        # Check for null values
        for col in self.required_fields:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    summary["null_counts"][col] = int(null_count)
        
        # Check categorical fields
        categorical_fields = {
            "Product_Type": self.valid_product_types,
            "Store_Type": self.valid_store_types,
            "Store_Location_City_Type": self.valid_city_types,
            "Store_Size": self.valid_store_sizes,
            "Product_Sugar_Content": self.valid_sugar_content
        }
        
        for field, valid_values in categorical_fields.items():
            if field in df.columns:
                invalid_count = (~df[field].isin(valid_values)).sum()
                if invalid_count > 0:
                    summary["invalid_categorical_counts"][field] = int(invalid_count)
        
        # Check numerical ranges
        for field, (min_val, max_val) in self.numerical_ranges.items():
            if field in df.columns:
                try:
                    numeric_col = pd.to_numeric(df[field], errors='coerce')
                    out_of_range = ((numeric_col < min_val) | (numeric_col > max_val)).sum()
                    if out_of_range > 0:
                        summary["out_of_range_counts"][field] = int(out_of_range)
                except Exception as e:
                    logger.warning(f"Could not validate range for {field}: {str(e)}")
        
        return summary