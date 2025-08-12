"""
Data loading, processing and cleaning module for e-commerce analysis.

This module provides functions to load and process e-commerce datasets,
handling data cleaning, type conversions, and initial transformations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime
from simple_logger import logger


def load_datasets(data_path: str = 'ecommerce_data') -> Dict[str, pd.DataFrame]:
    """
    Load all e-commerce datasets from CSV files.
    
    Args:
        data_path: Path to the directory containing CSV files
        
    Returns:
        Dictionary containing all loaded datasets
    """
    logger.info(f"Loading datasets from directory: {data_path}")
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
        logger.debug(f"Attempting to load {key} from {file_path}")
        
        try:
            datasets[key] = pd.read_csv(file_path)
            rows, cols = datasets[key].shape
            logger.info(f"Successfully loaded {key}: {rows} rows, {cols} columns")
            
            # Log basic data quality info
            null_count = datasets[key].isnull().sum().sum()
            if null_count > 0:
                logger.warning(f"{key} has {null_count} null values")
                
        except FileNotFoundError:
            error_msg = f"Could not find {file_path}"
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"Error loading {file_path}: {str(e)}"
            logger.error(error_msg)
    
    total_records = sum(len(df) for df in datasets.values())
    logger.info(f"Dataset loading completed: {len(datasets)} files, {total_records} total records")
    return datasets


def clean_and_prepare_data(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Clean and prepare datasets for analysis.
    
    Args:
        datasets: Dictionary of raw datasets
        
    Returns:
        Dictionary of cleaned datasets
    """
    logger.info("Starting data cleaning and preparation")
    cleaned_datasets = datasets.copy()
    
    # Clean orders data
    if 'orders' in cleaned_datasets:
        logger.debug("Cleaning orders dataset")
        orders = cleaned_datasets['orders'].copy()
        initial_count = len(orders)
        
        # Convert timestamp columns to datetime
        timestamp_cols = [
            'order_purchase_timestamp', 
            'order_approved_at',
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]
        
        logger.debug(f"Converting {len(timestamp_cols)} timestamp columns to datetime")
        conversion_stats = {}
        
        for col in timestamp_cols:
            if col in orders.columns:
                before_nulls = orders[col].isnull().sum()
                orders[col] = pd.to_datetime(orders[col], errors='coerce')
                after_nulls = orders[col].isnull().sum()
                conversion_stats[col] = {'before_nulls': before_nulls, 'after_nulls': after_nulls}
                
                if after_nulls > before_nulls:
                    logger.warning(f"{col}: {after_nulls - before_nulls} values became null during datetime conversion")
        
        # Extract date components
        logger.debug("Extracting date components from purchase timestamp")
        if 'order_purchase_timestamp' in orders.columns:
            orders['purchase_date'] = orders['order_purchase_timestamp'].dt.date
            orders['purchase_year'] = orders['order_purchase_timestamp'].dt.year
            orders['purchase_month'] = orders['order_purchase_timestamp'].dt.month
            orders['purchase_day_of_week'] = orders['order_purchase_timestamp'].dt.dayofweek
            
            # Log date range info
            date_range = {
                'min_date': orders['order_purchase_timestamp'].min(),
                'max_date': orders['order_purchase_timestamp'].max()
            }
            logger.info(f"Orders date range: {date_range['min_date']} to {date_range['max_date']}")
        
        cleaned_datasets['orders'] = orders
    else:
        logger.warning("Orders dataset not found in input data")
    
    # Clean reviews data
    if 'reviews' in cleaned_datasets:
        logger.debug("Cleaning reviews dataset")
        reviews = cleaned_datasets['reviews'].copy()
        initial_count = len(reviews)
        
        # Convert review dates
        if 'review_creation_date' in reviews.columns:
            before_nulls = reviews['review_creation_date'].isnull().sum()
            reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'], errors='coerce')
            after_nulls = reviews['review_creation_date'].isnull().sum()
            if after_nulls > before_nulls:
                logger.warning(f"review_creation_date: {after_nulls - before_nulls} values became null during conversion")
        
        if 'review_answer_timestamp' in reviews.columns:
            before_nulls = reviews['review_answer_timestamp'].isnull().sum()
            reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'], errors='coerce')
            after_nulls = reviews['review_answer_timestamp'].isnull().sum()
            if after_nulls > before_nulls:
                logger.warning(f"review_answer_timestamp: {after_nulls - before_nulls} values became null during conversion")
        
        # Log review score distribution
        if 'review_score' in reviews.columns:
            score_dist = reviews['review_score'].value_counts().sort_index()
            logger.info(f"Review score distribution: {score_dist.to_dict()}")
            
        cleaned_datasets['reviews'] = reviews
    else:
        logger.warning("Reviews dataset not found in input data")
    
    logger.info("Data cleaning and preparation completed")
    
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
    logger.info(f"Creating consolidated sales dataset with order status filter: {order_status_filter}")
    
    # Start with order items
    logger.debug("Starting with order items dataset")
    required_cols = ['order_id', 'order_item_id', 'product_id', 'price', 'freight_value']
    available_cols = [col for col in required_cols if col in datasets['order_items'].columns]
    
    if len(available_cols) < len(required_cols):
        missing_cols = set(required_cols) - set(available_cols)
        logger.warning(f"Missing columns in order_items: {missing_cols}")
    
    sales_data = datasets['order_items'][available_cols].copy()
    logger.info(f"Starting with {len(sales_data)} order items")
    
    # Merge with orders
    logger.debug("Merging with orders dataset")
    orders_cols = ['order_id', 'order_status', 'order_purchase_timestamp', 
                   'order_delivered_customer_date', 'purchase_year', 'purchase_month', 'customer_id']
    
    available_order_cols = [col for col in orders_cols if col in datasets['orders'].columns]
    missing_order_cols = set(orders_cols) - set(available_order_cols)
    
    if missing_order_cols:
        logger.warning(f"Missing columns in orders: {missing_order_cols}")
    
    before_merge = len(sales_data)
    sales_data = sales_data.merge(datasets['orders'][available_order_cols], on='order_id', how='left')
    after_merge = len(sales_data)
    
    if before_merge != after_merge:
        logger.warning(f"Row count changed during orders merge: {before_merge} -> {after_merge}")
    
    logger.info(f"After orders merge: {len(sales_data)} records")
    
    # Filter by order status if specified
    if order_status_filter and 'order_status' in sales_data.columns:
        before_filter = len(sales_data)
        status_counts = sales_data['order_status'].value_counts()
        logger.info(f"Order status distribution before filter: {status_counts.to_dict()}")
        
        sales_data = sales_data[sales_data['order_status'] == order_status_filter].copy()
        after_filter = len(sales_data)
        
        logger.info(f"Filtered to '{order_status_filter}' orders: {before_filter} -> {after_filter} records")
    elif order_status_filter:
        logger.warning(f"Cannot filter by order status '{order_status_filter}' - column not available")
    
    # Calculate delivery metrics
    if 'order_delivered_customer_date' in sales_data.columns and 'order_purchase_timestamp' in sales_data.columns:
        logger.debug("Calculating delivery metrics")
        
        # Calculate delivery days
        sales_data['delivery_days'] = (
            sales_data['order_delivered_customer_date'] - sales_data['order_purchase_timestamp']
        ).dt.days
        
        # Log delivery statistics
        delivery_stats = sales_data['delivery_days'].describe()
        logger.info(f"Delivery time statistics: mean={delivery_stats['mean']:.1f} days, median={delivery_stats['50%']:.1f} days")
        
        # Check for negative delivery days (data quality issue)
        negative_delivery = (sales_data['delivery_days'] < 0).sum()
        if negative_delivery > 0:
            logger.warning(f"Found {negative_delivery} records with negative delivery days (data quality issue)")
        
        # Categorize delivery speed
        sales_data['delivery_speed_category'] = sales_data['delivery_days'].apply(categorize_delivery_speed)
        
        # Log delivery speed distribution
        speed_dist = sales_data['delivery_speed_category'].value_counts()
        logger.info(f"Delivery speed distribution: {speed_dist.to_dict()}")
    else:
        logger.warning("Cannot calculate delivery metrics - required timestamp columns not available")
    
    logger.info(f"Sales dataset creation completed: {len(sales_data)} records")
    
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
    logger.debug(f"Filtering data by date range: years={start_year}-{end_year}, months={start_month}-{end_month}")
    filtered_df = df.copy()
    initial_count = len(filtered_df)
    
    if date_column not in df.columns:
        error_msg = f"{date_column} not found in DataFrame"
        logger.error(error_msg)
        return filtered_df
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_column]):
        logger.debug(f"Converting {date_column} to datetime")
        filtered_df[date_column] = pd.to_datetime(filtered_df[date_column])
    
    # Filter by year range
    if start_year is not None:
        before_filter = len(filtered_df)
        filtered_df = filtered_df[filtered_df[date_column].dt.year >= start_year]
        logger.debug(f"Year >= {start_year} filter: {before_filter} -> {len(filtered_df)} records")
        
    if end_year is not None:
        before_filter = len(filtered_df)
        filtered_df = filtered_df[filtered_df[date_column].dt.year <= end_year]
        logger.debug(f"Year <= {end_year} filter: {before_filter} -> {len(filtered_df)} records")
    
    # Filter by month range (within the year range)
    if start_month is not None:
        before_filter = len(filtered_df)
        filtered_df = filtered_df[filtered_df[date_column].dt.month >= start_month]
        logger.debug(f"Month >= {start_month} filter: {before_filter} -> {len(filtered_df)} records")
        
    if end_month is not None:
        before_filter = len(filtered_df)
        filtered_df = filtered_df[filtered_df[date_column].dt.month <= end_month]
        logger.debug(f"Month <= {end_month} filter: {before_filter} -> {len(filtered_df)} records")
    
    final_count = len(filtered_df)
    logger.info(f"Date filtering completed: {initial_count} -> {final_count} records ({100*final_count/initial_count:.1f}% retained)")
    
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
    logger.debug("Adding product categories to sales data")
    initial_count = len(sales_df)
    
    product_cols = ['product_id', 'product_category_name']
    available_cols = [col for col in product_cols if col in products_df.columns]
    
    if 'product_id' not in available_cols:
        error_msg = "product_id not found in products_df, cannot merge product categories"
        logger.error(error_msg)
        return sales_df
    
    if 'product_category_name' not in available_cols:
        warning_msg = "product_category_name not found in products_df"
        logger.warning(warning_msg)
        logger.debug(f"Available columns in products_df: {list(products_df.columns)}")
        
        # Return original dataframe with a placeholder category column
        sales_with_categories = sales_df.copy()
        sales_with_categories['product_category_name'] = 'Unknown'
        logger.info("Added placeholder 'Unknown' category for all products")
        return sales_with_categories
    
    # Check for unique products in both datasets
    sales_products = set(sales_df['product_id'].unique())
    catalog_products = set(products_df['product_id'].unique())
    
    missing_products = sales_products - catalog_products
    if missing_products:
        logger.warning(f"{len(missing_products)} products in sales data not found in product catalog")
    
    # Perform the merge
    result_df = sales_df.merge(products_df[available_cols], on='product_id', how='left')
    
    # Check merge results
    null_categories = result_df['product_category_name'].isnull().sum()
    if null_categories > 0:
        logger.warning(f"{null_categories} records have null product categories after merge")
    
    category_counts = result_df['product_category_name'].value_counts()
    logger.info(f"Product categories added: {len(category_counts)} unique categories")
    logger.debug(f"Top categories: {category_counts.head().to_dict()}")
    
    return result_df


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
    logger.debug("Adding customer geography to sales data")
    initial_count = len(sales_df)
    
    # First merge with orders to get customer_id if not already present
    if 'customer_id' not in sales_df.columns:
        logger.debug("customer_id not in sales_df, merging with orders first")
        before_merge = len(sales_df)
        sales_df = sales_df.merge(orders_df[['order_id', 'customer_id']], on='order_id', how='left')
        after_merge = len(sales_df)
        
        if before_merge != after_merge:
            logger.warning(f"Row count changed during customer_id merge: {before_merge} -> {after_merge}")
        
        null_customers = sales_df['customer_id'].isnull().sum()
        if null_customers > 0:
            logger.warning(f"{null_customers} records have null customer_id after merge")
    
    # Then merge with customers for geography
    geo_cols = ['customer_id', 'customer_state', 'customer_city', 'customer_zip_code_prefix']
    available_geo_cols = [col for col in geo_cols if col in customers_df.columns]
    missing_geo_cols = set(geo_cols) - set(available_geo_cols)
    
    if missing_geo_cols:
        logger.warning(f"Missing geography columns in customers_df: {missing_geo_cols}")
    
    logger.debug(f"Merging with customer geography using columns: {available_geo_cols}")
    
    # Check unique customers
    sales_customers = set(sales_df['customer_id'].dropna().unique())
    geo_customers = set(customers_df['customer_id'].unique())
    missing_geo_customers = sales_customers - geo_customers
    
    if missing_geo_customers:
        logger.warning(f"{len(missing_geo_customers)} customers in sales data not found in customers geography")
    
    result_df = sales_df.merge(customers_df[available_geo_cols], on='customer_id', how='left')
    
    # Log geography statistics
    if 'customer_state' in result_df.columns:
        state_counts = result_df['customer_state'].value_counts()
        logger.info(f"Customer geography added: {len(state_counts)} states represented")
        logger.debug(f"Top states: {state_counts.head().to_dict()}")
        
        null_states = result_df['customer_state'].isnull().sum()
        if null_states > 0:
            logger.warning(f"{null_states} records have null customer_state after merge")
    
    return result_df


def add_review_data(sales_df: pd.DataFrame, reviews_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add review information to sales data.
    
    Args:
        sales_df: Sales DataFrame
        reviews_df: Reviews DataFrame
        
    Returns:
        Sales DataFrame with review information
    """
    logger.debug("Adding review data to sales")
    initial_count = len(sales_df)
    
    review_cols = ['order_id', 'review_score', 'review_creation_date']
    available_review_cols = [col for col in review_cols if col in reviews_df.columns]
    missing_review_cols = set(review_cols) - set(available_review_cols)
    
    if missing_review_cols:
        logger.warning(f"Missing review columns: {missing_review_cols}")
    
    # Check for duplicate reviews
    duplicate_reviews = reviews_df['order_id'].duplicated().sum()
    if duplicate_reviews > 0:
        logger.warning(f"{duplicate_reviews} duplicate order_ids found in reviews data")
    
    # Check order coverage
    sales_orders = set(sales_df['order_id'].unique())
    review_orders = set(reviews_df['order_id'].unique())
    orders_with_reviews = len(sales_orders & review_orders)
    orders_without_reviews = len(sales_orders - review_orders)
    
    logger.info(f"Review coverage: {orders_with_reviews} orders with reviews, {orders_without_reviews} without")
    
    result_df = sales_df.merge(reviews_df[available_review_cols], on='order_id', how='left')
    
    # Log review statistics
    if 'review_score' in result_df.columns:
        review_stats = result_df['review_score'].describe()
        logger.info(f"Review scores - Mean: {review_stats['mean']:.2f}, Count: {review_stats['count']:.0f}")
        
        null_scores = result_df['review_score'].isnull().sum()
        if null_scores > 0:
            logger.info(f"{null_scores} records without review scores")
    
    return result_df


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