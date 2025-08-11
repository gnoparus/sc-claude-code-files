"""
Data loading, processing and cleaning module for e-commerce analysis.

This module provides functions to load and process e-commerce datasets,
handling data cleaning, type conversions, and initial transformations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime


def load_datasets(data_path: str = 'ecommerce_data') -> Dict[str, pd.DataFrame]:
    """
    Load all e-commerce datasets from CSV files.
    
    Args:
        data_path: Path to the directory containing CSV files
        
    Returns:
        Dictionary containing all loaded datasets
    """
    datasets = {}
    
    # Define file mappings
    files = {
        'orders': 'orders_dataset.csv',
        'order_items': 'order_items_dataset.csv',
        'products': 'products_dataset.csv',
        'customers': 'customers_dataset.csv',
        'reviews': 'order_reviews_dataset.csv'
    }
    
    # Load each dataset
    for key, filename in files.items():
        file_path = f"{data_path}/{filename}"
        try:
            datasets[key] = pd.read_csv(file_path)
            print(f"Loaded {key}: {datasets[key].shape[0]} rows, {datasets[key].shape[1]} columns")
        except FileNotFoundError:
            print(f"Warning: Could not find {file_path}")
            
    return datasets


def clean_and_prepare_data(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Clean and prepare datasets for analysis.
    
    Args:
        datasets: Dictionary of raw datasets
        
    Returns:
        Dictionary of cleaned datasets
    """
    cleaned_datasets = datasets.copy()
    
    # Clean orders data
    if 'orders' in cleaned_datasets:
        orders = cleaned_datasets['orders'].copy()
        
        # Convert timestamp columns to datetime
        timestamp_cols = [
            'order_purchase_timestamp', 
            'order_approved_at',
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]
        
        for col in timestamp_cols:
            if col in orders.columns:
                orders[col] = pd.to_datetime(orders[col], errors='coerce')
        
        # Extract date components
        orders['purchase_date'] = orders['order_purchase_timestamp'].dt.date
        orders['purchase_year'] = orders['order_purchase_timestamp'].dt.year
        orders['purchase_month'] = orders['order_purchase_timestamp'].dt.month
        orders['purchase_day_of_week'] = orders['order_purchase_timestamp'].dt.dayofweek
        
        cleaned_datasets['orders'] = orders
    
    # Clean reviews data
    if 'reviews' in cleaned_datasets:
        reviews = cleaned_datasets['reviews'].copy()
        
        # Convert review dates
        if 'review_creation_date' in reviews.columns:
            reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'], errors='coerce')
        if 'review_answer_timestamp' in reviews.columns:
            reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'], errors='coerce')
            
        cleaned_datasets['reviews'] = reviews
    
    return cleaned_datasets


def create_sales_dataset(datasets: Dict[str, pd.DataFrame], 
                        order_status_filter: Optional[str] = 'delivered') -> pd.DataFrame:
    """
    Create a consolidated sales dataset by merging relevant tables.
    
    Args:
        datasets: Dictionary of cleaned datasets
        order_status_filter: Filter orders by status (default: 'delivered')
        
    Returns:
        Consolidated sales DataFrame
    """
    # Start with order items
    sales_data = datasets['order_items'][['order_id', 'order_item_id', 'product_id', 'price', 'freight_value']].copy()
    
    # Merge with orders
    orders_cols = ['order_id', 'order_status', 'order_purchase_timestamp', 
                   'order_delivered_customer_date', 'purchase_year', 'purchase_month', 'customer_id']
    
    available_order_cols = [col for col in orders_cols if col in datasets['orders'].columns]
    sales_data = sales_data.merge(datasets['orders'][available_order_cols], on='order_id', how='left')
    
    # Filter by order status if specified
    if order_status_filter:
        sales_data = sales_data[sales_data['order_status'] == order_status_filter].copy()
    
    # Calculate delivery metrics
    if 'order_delivered_customer_date' in sales_data.columns and 'order_purchase_timestamp' in sales_data.columns:
        sales_data['delivery_days'] = (
            sales_data['order_delivered_customer_date'] - sales_data['order_purchase_timestamp']
        ).dt.days
        
        # Categorize delivery speed
        sales_data['delivery_speed_category'] = sales_data['delivery_days'].apply(categorize_delivery_speed)
    
    return sales_data


def categorize_delivery_speed(days: float) -> str:
    """
    Categorize delivery speed based on number of days.
    
    Args:
        days: Number of delivery days
        
    Returns:
        Delivery speed category string
    """
    if pd.isna(days):
        return 'Unknown'
    elif days <= 3:
        return '1-3 days'
    elif days <= 7:
        return '4-7 days'
    else:
        return '8+ days'


def filter_data_by_date_range(df: pd.DataFrame, 
                             start_year: Optional[int] = None,
                             end_year: Optional[int] = None,
                             start_month: Optional[int] = None,
                             end_month: Optional[int] = None,
                             date_column: str = 'order_purchase_timestamp') -> pd.DataFrame:
    """
    Filter DataFrame by date range.
    
    Args:
        df: Input DataFrame
        start_year: Starting year (inclusive)
        end_year: Ending year (inclusive)
        start_month: Starting month (inclusive, 1-12)
        end_month: Ending month (inclusive, 1-12)
        date_column: Name of the date column to filter on
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    if date_column not in df.columns:
        print(f"Warning: {date_column} not found in DataFrame")
        return filtered_df
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_column]):
        filtered_df[date_column] = pd.to_datetime(filtered_df[date_column])
    
    # Filter by year range
    if start_year is not None:
        filtered_df = filtered_df[filtered_df[date_column].dt.year >= start_year]
    if end_year is not None:
        filtered_df = filtered_df[filtered_df[date_column].dt.year <= end_year]
    
    # Filter by month range (within the year range)
    if start_month is not None:
        filtered_df = filtered_df[filtered_df[date_column].dt.month >= start_month]
    if end_month is not None:
        filtered_df = filtered_df[filtered_df[date_column].dt.month <= end_month]
    
    return filtered_df


def add_product_categories(sales_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add product category information to sales data.
    
    Args:
        sales_df: Sales DataFrame
        products_df: Products DataFrame
        
    Returns:
        Sales DataFrame with product categories
    """
    product_cols = ['product_id', 'product_category_name']
    available_cols = [col for col in product_cols if col in products_df.columns]
    
    if 'product_id' not in available_cols:
        print("Warning: product_id not found in products_df, cannot merge product categories")
        return sales_df
    
    if 'product_category_name' not in available_cols:
        print("Warning: product_category_name not found in products_df")
        print(f"Available columns in products_df: {list(products_df.columns)}")
        # Return original dataframe with a placeholder category column
        sales_with_categories = sales_df.copy()
        sales_with_categories['product_category_name'] = 'Unknown'
        return sales_with_categories
    
    return sales_df.merge(products_df[available_cols], on='product_id', how='left')


def add_customer_geography(sales_df: pd.DataFrame, 
                          orders_df: pd.DataFrame, 
                          customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add customer geographic information to sales data.
    
    Args:
        sales_df: Sales DataFrame
        orders_df: Orders DataFrame  
        customers_df: Customers DataFrame
        
    Returns:
        Sales DataFrame with customer geography
    """
    # First merge with orders to get customer_id if not already present
    if 'customer_id' not in sales_df.columns:
        sales_df = sales_df.merge(orders_df[['order_id', 'customer_id']], on='order_id', how='left')
    
    # Then merge with customers for geography
    geo_cols = ['customer_id', 'customer_state', 'customer_city', 'customer_zip_code_prefix']
    available_geo_cols = [col for col in geo_cols if col in customers_df.columns]
    
    return sales_df.merge(customers_df[available_geo_cols], on='customer_id', how='left')


def add_review_data(sales_df: pd.DataFrame, reviews_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add review information to sales data.
    
    Args:
        sales_df: Sales DataFrame
        reviews_df: Reviews DataFrame
        
    Returns:
        Sales DataFrame with review information
    """
    review_cols = ['order_id', 'review_score', 'review_creation_date']
    available_review_cols = [col for col in review_cols if col in reviews_df.columns]
    
    return sales_df.merge(reviews_df[available_review_cols], on='order_id', how='left')


def get_data_summary(df: pd.DataFrame) -> Dict:
    """
    Get summary statistics for a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary containing summary statistics
    """
    summary = {
        'shape': df.shape,
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'date_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist()
    }
    
    # Add date range if date columns exist
    for date_col in summary['date_columns']:
        if not df[date_col].isna().all():
            summary[f'{date_col}_range'] = {
                'min': df[date_col].min(),
                'max': df[date_col].max()
            }
    
    return summary