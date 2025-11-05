import streamlit as st
import pandas as pd
import requests
from datetime import datetime

from app.config import settings

# Configure page
st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon=settings.APP_ICON,
    layout=settings.APP_LAYOUT
)

# UI Title and Subtitle
st.title(f"{settings.APP_ICON} {settings.APP_TITLE} App")
st.write("This tool predicts **product-level revenue** in a specific store using historical and categorical inputs.")

# UI for Input Features
st.subheader("Enter Product & Store Details:")

# Categorical Inputs - All valid product types from training data
product_type = st.selectbox("Product Type", [
    "Meat", "Snack Foods", "Soft Drinks", "Dairy", "Household", "Fruits and Vegetables",
    "Frozen Foods", "Breakfast", "Baking Goods", "Health and Hygiene", "Starchy Foods",
    "Breads", "Canned", "Seafood", "Hard Drinks", "Others"
])

store_type = st.selectbox("Store Type", [
    "Supermarket Type1", "Supermarket Type2", "Supermarket Type3", "Grocery Store"
])

city_type = st.selectbox("City Type", ["Tier 1", "Tier 2", "Tier 3"])
store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
sugar_content = st.selectbox("Product Sugar Content", ["No Sugar", "Low Sugar", "Regular"])

# Numerical Inputs - Based on training data ranges from EDA
# Product_Weight: min=4.0, max=22.0 (from training data describe())
product_weight = st.number_input("Product Weight (kg)", min_value=4.0, max_value=22.0, value=12.66, step=0.1)
# Product_MRP: min=31.0, max=266.0 (from training data describe())
product_mrp = st.number_input("Product MRP", min_value=31.0, max_value=266.0, value=146.74, step=1.0)
# Product_Allocated_Area: min=0.004, max=0.298 (from training data describe())
# Use step=0.01 for better increment/decrement button functionality (Streamlit works better with larger steps)
allocated_area = st.number_input("Allocated Display Area (0-1)", min_value=0.004, max_value=0.298, value=0.056, step=0.01, format="%.3f")
# Store_Establishment_Year: min=1987, max=2009 (from training data describe())
# Explicitly set step=1 for integer fields to ensure increment/decrement buttons work
store_est_year = st.number_input("Store Establishment Year", min_value=1987, max_value=2009, value=2009, step=1)

# Convert to DataFrame
input_data = pd.DataFrame({
    'Product_Type': [product_type],
    'Store_Type': [store_type],
    'Store_Location_City_Type': [city_type],
    'Store_Size': [store_size],
    'Product_Sugar_Content': [sugar_content],
    'Product_Weight': [product_weight],
    'Product_MRP': [product_mrp],
    'Product_Allocated_Area': [allocated_area],
    'Store_Establishment_Year': [store_est_year],
})

# Make prediction when the "Predict" button is clicked
if st.button("Predict"):
    try:
        # Use transform service for single prediction
        transform_url = f"{settings.TRANSFORM_SERVICE_URL}/transform/single"
        
        with st.spinner("Making prediction..."):
            response = requests.post(
                transform_url,
                json=input_data.to_dict(orient='records')[0],
                timeout=settings.API_TIMEOUT
            )
        
        if response.status_code == 200:
            result = response.json()
            # Check for different possible response formats
            if 'predicted_revenue' in result:
                prediction = result['predicted_revenue']
            elif 'Predicted_Store_Sales_Total' in result:
                prediction = result['Predicted_Store_Sales_Total']
            else:
                prediction = result.get('prediction', 'N/A')
            
            st.success(f"Predicted Revenue (in dollars): ${prediction:,.2f}")
            
            if settings.DEBUG_MODE:
                st.json(result)
        else:
            error_msg = response.json().get('error', 'Error making prediction.')
            st.error(f"Error: {error_msg}")
            if settings.DEBUG_MODE:
                st.json(response.json())
                
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the prediction service. Please check if the service is running.")
    except requests.exceptions.Timeout:
        st.error(f"Request timed out after {settings.API_TIMEOUT} seconds.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if settings.DEBUG_MODE:
            st.exception(e)

# Section for batch prediction
if settings.ENABLE_BATCH_PREDICTION:
    st.subheader("Batch Prediction")
    
    # Allow users to upload a CSV file for batch prediction
    uploaded_file = st.file_uploader(
        "Upload CSV file for batch prediction",
        type=settings.ALLOWED_FILE_EXTENSIONS,
        help=f"Maximum file size: {settings.MAX_FILE_SIZE_MB}MB. Maximum rows: {settings.MAX_BATCH_ROWS}"
    )
    
    # Make batch prediction when the "Predict Batch" button is clicked
    if uploaded_file is not None:
        try:
            # Read and validate CSV
            df = pd.read_csv(uploaded_file)
            
            # Check file size
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            if file_size_mb > settings.MAX_FILE_SIZE_MB:
                st.error(f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({settings.MAX_FILE_SIZE_MB}MB)")
            elif len(df) > settings.MAX_BATCH_ROWS:
                st.error(f"Number of rows ({len(df)}) exceeds maximum allowed ({settings.MAX_BATCH_ROWS})")
            else:
                # Validate required columns
                required_fields = [
                    "Product_Type", "Store_Type", "Store_Location_City_Type",
                    "Store_Size", "Product_Sugar_Content", "Product_Weight",
                    "Product_MRP", "Product_Allocated_Area", "Store_Establishment_Year"
                ]
                missing_fields = [f for f in required_fields if f not in df.columns]
                
                if missing_fields:
                    st.error(f"Missing required columns: {', '.join(missing_fields)}")
                    st.write("Required columns:", ", ".join(required_fields))
                else:
                    st.success(f"File loaded successfully. {len(df)} rows found.")
                    
                    if st.button("Predict Batch"):
                        try:
                            # Use transform service for batch prediction
                            batch_url = f"{settings.TRANSFORM_SERVICE_URL}/transform/batch"
                            
                            with st.spinner(f"Processing {len(df)} predictions..."):
                                # Convert DataFrame to CSV string
                                csv_string = df.to_csv(index=False)
                                files = {'file': ('batch_input.csv', csv_string, 'text/csv')}
                                
                                response = requests.post(
                                    batch_url,
                                    files=files,
                                    timeout=settings.API_TIMEOUT
                                )
                            
                            if response.status_code == 200:
                                result = response.json()
                                predictions = result.get('predictions', result.get('Predicted_Store_Sales_Total', []))
                                
                                st.success(f"Batch predictions completed! {len(predictions)} predictions generated.")
                                
                                # Create results DataFrame
                                results_df = df.copy()
                                results_df['Predicted_Revenue'] = predictions
                                
                                # Display results
                                st.dataframe(results_df, use_container_width=True)
                                
                                # Statistics
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Records", len(predictions))
                                with col2:
                                    st.metric("Average Revenue", f"${sum(predictions)/len(predictions):,.2f}")
                                with col3:
                                    st.metric("Min Revenue", f"${min(predictions):,.2f}")
                                with col4:
                                    st.metric("Max Revenue", f"${max(predictions):,.2f}")
                                
                                # Download option
                                if settings.ENABLE_DOWNLOAD:
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    csv_download = results_df.to_csv(index=False)
                                    st.download_button(
                                        label="Download Results as CSV",
                                        data=csv_download,
                                        file_name=f"superkart_predictions_{timestamp}.csv",
                                        mime="text/csv"
                                    )
                            else:
                                error_msg = response.json().get('error', 'Error making batch prediction.')
                                st.error(f"Error: {error_msg}")
                                if settings.DEBUG_MODE:
                                    st.json(response.json())
                                    
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to the prediction service. Please check if the service is running.")
                        except requests.exceptions.Timeout:
                            st.error(f"Request timed out after {settings.API_TIMEOUT} seconds.")
                        except Exception as e:
                            st.error(f"An error occurred during batch prediction: {str(e)}")
                            if settings.DEBUG_MODE:
                                st.exception(e)
                                
        except pd.errors.EmptyDataError:
            st.error("The uploaded CSV file is empty.")
        except pd.errors.ParserError:
            st.error("Could not parse the CSV file. Please check the file format.")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            if settings.DEBUG_MODE:
                st.exception(e)

