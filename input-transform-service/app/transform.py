import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Handles transformation of JSON/CSV data to pandas DataFrame
    """
    
    def __init__(self):
        self.required_columns = [
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
        
        # Normalization mappings
        self.sugar_content_mapping = {
            'reg': 'Regular',
            'REG': 'Regular',
            'regular': 'Regular',
            'low fat': 'Low Sugar',
            'Low Fat': 'Low Sugar',
            'LF': 'Low Sugar',
            'no sugar': 'No Sugar',
            'No Sugar': 'No Sugar'
        }
    
    def json_to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert JSON data to pandas DataFrame
        
        Args:
            data: List of dictionaries with product-store data
            
        Returns:
            pandas DataFrame
        """
        df = pd.DataFrame(data)
        return self.transform_dataframe(df)
    
    def transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply transformations to DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Transformed DataFrame
        """
        df = df.copy()
        
        # Normalize Sugar Content
        df['Product_Sugar_Content'] = df['Product_Sugar_Content'].apply(
            lambda x: self.sugar_content_mapping.get(x, x)
        )
        
        # Ensure correct data types
        df['Product_Weight'] = pd.to_numeric(df['Product_Weight'], errors='coerce')
        df['Product_MRP'] = pd.to_numeric(df['Product_MRP'], errors='coerce')
        df['Product_Allocated_Area'] = pd.to_numeric(df['Product_Allocated_Area'], errors='coerce')
        df['Store_Establishment_Year'] = pd.to_numeric(df['Store_Establishment_Year'], errors='coerce').astype('Int64')
        
        # Strip whitespace from string columns
        string_columns = ['Product_Type', 'Store_Type', 'Store_Location_City_Type', 
                         'Store_Size', 'Product_Sugar_Content']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Check for missing values after transformation
        if df.isnull().any().any():
            null_cols = df.columns[df.isnull().any()].tolist()
            raise ValueError(f"Missing or invalid values found in columns: {null_cols}")
        
        return df[self.required_columns]
    
    def csv_to_dataframe(self, csv_content: str) -> pd.DataFrame:
        """
        Convert CSV content to pandas DataFrame
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            pandas DataFrame
        """
        df = pd.read_csv(pd.io.common.StringIO(csv_content))
        return self.transform_dataframe(df)