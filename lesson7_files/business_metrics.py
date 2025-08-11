"""
Business metrics calculation module for e-commerce analysis.

This module provides functions to calculate key business metrics including
revenue, growth, customer experience, and operational performance indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from operator import attrgetter
import warnings


def calculate_revenue_metrics(sales_df: pd.DataFrame, 
                             date_column: str = 'order_purchase_timestamp',
                             price_column: str = 'price') -> Dict:
    """
    Calculate comprehensive revenue metrics.
    
    Args:
        sales_df: Sales DataFrame
        date_column: Name of date column for time-based analysis
        price_column: Name of price/revenue column
        
    Returns:
        Dictionary containing revenue metrics
    """
    metrics = {}
    
    # Total revenue
    metrics['total_revenue'] = sales_df[price_column].sum()
    
    # Number of orders and items
    metrics['total_orders'] = sales_df['order_id'].nunique()
    metrics['total_items'] = len(sales_df)
    
    # Average metrics
    metrics['avg_item_price'] = sales_df[price_column].mean()
    metrics['median_item_price'] = sales_df[price_column].median()
    
    # Calculate average order value
    order_values = sales_df.groupby('order_id')[price_column].sum()
    metrics['avg_order_value'] = order_values.mean()
    metrics['median_order_value'] = order_values.median()
    
    # Items per order
    items_per_order = sales_df.groupby('order_id').size()
    metrics['avg_items_per_order'] = items_per_order.mean()
    
    # Revenue distribution percentiles
    metrics['revenue_percentiles'] = {
        '25th': sales_df[price_column].quantile(0.25),
        '75th': sales_df[price_column].quantile(0.75),
        '90th': sales_df[price_column].quantile(0.90),
        '95th': sales_df[price_column].quantile(0.95)
    }
    
    return metrics


def calculate_growth_metrics(current_df: pd.DataFrame, 
                           previous_df: pd.DataFrame,
                           price_column: str = 'price') -> Dict:
    """
    Calculate growth metrics comparing two periods.
    
    Args:
        current_df: DataFrame for current period
        previous_df: DataFrame for previous period
        price_column: Name of price/revenue column
        
    Returns:
        Dictionary containing growth metrics
    """
    current_metrics = calculate_revenue_metrics(current_df, price_column=price_column)
    previous_metrics = calculate_revenue_metrics(previous_df, price_column=price_column)
    
    growth_metrics = {}
    
    # Revenue growth
    revenue_growth = (current_metrics['total_revenue'] - previous_metrics['total_revenue']) / previous_metrics['total_revenue']
    growth_metrics['revenue_growth_pct'] = revenue_growth * 100
    
    # Order growth
    order_growth = (current_metrics['total_orders'] - previous_metrics['total_orders']) / previous_metrics['total_orders']
    growth_metrics['order_growth_pct'] = order_growth * 100
    
    # Average order value growth
    aov_growth = (current_metrics['avg_order_value'] - previous_metrics['avg_order_value']) / previous_metrics['avg_order_value']
    growth_metrics['aov_growth_pct'] = aov_growth * 100
    
    # Items per order growth
    items_growth = (current_metrics['avg_items_per_order'] - previous_metrics['avg_items_per_order']) / previous_metrics['avg_items_per_order']
    growth_metrics['items_per_order_growth_pct'] = items_growth * 100
    
    # Absolute changes
    growth_metrics['revenue_change_absolute'] = current_metrics['total_revenue'] - previous_metrics['total_revenue']
    growth_metrics['order_change_absolute'] = current_metrics['total_orders'] - previous_metrics['total_orders']
    
    return growth_metrics


def calculate_monthly_trends(sales_df: pd.DataFrame, 
                           date_column: str = 'order_purchase_timestamp',
                           price_column: str = 'price',
                           year_filter: Optional[int] = None) -> pd.DataFrame:
    """
    Calculate monthly revenue trends and growth rates.
    
    Args:
        sales_df: Sales DataFrame
        date_column: Name of date column
        price_column: Name of price column
        year_filter: Optional year to filter data
        
    Returns:
        DataFrame with monthly metrics and growth rates
    """
    df = sales_df.copy()
    
    # Ensure datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Filter by year if specified
    if year_filter:
        df = df[df[date_column].dt.year == year_filter]
    
    # Extract year and month
    df['year'] = df[date_column].dt.year
    df['month'] = df[date_column].dt.month
    
    # Group by year-month and calculate metrics
    monthly_metrics = df.groupby(['year', 'month']).agg({
        price_column: ['sum', 'mean', 'count'],
        'order_id': 'nunique'
    }).round(2)
    
    # Flatten column names
    monthly_metrics.columns = ['total_revenue', 'avg_item_price', 'total_items', 'total_orders']
    monthly_metrics = monthly_metrics.reset_index()
    
    # Calculate average order value
    monthly_metrics['avg_order_value'] = (monthly_metrics['total_revenue'] / monthly_metrics['total_orders']).round(2)
    
    # Calculate month-over-month growth
    monthly_metrics['revenue_mom_growth'] = monthly_metrics['total_revenue'].pct_change() * 100
    monthly_metrics['orders_mom_growth'] = monthly_metrics['total_orders'].pct_change() * 100
    monthly_metrics['aov_mom_growth'] = monthly_metrics['avg_order_value'].pct_change() * 100
    
    # Round growth rates
    growth_cols = ['revenue_mom_growth', 'orders_mom_growth', 'aov_mom_growth']
    monthly_metrics[growth_cols] = monthly_metrics[growth_cols].round(2)
    
    return monthly_metrics


def calculate_product_category_metrics(sales_df: pd.DataFrame, 
                                     products_df: pd.DataFrame,
                                     price_column: str = 'price') -> pd.DataFrame:
    """
    Calculate metrics by product category.
    
    Args:
        sales_df: Sales DataFrame
        products_df: Products DataFrame with categories
        price_column: Name of price column
        
    Returns:
        DataFrame with category metrics sorted by revenue
    """
    # Check if product_category_name exists in products_df
    if 'product_category_name' not in products_df.columns:
        print("Warning: 'product_category_name' not found in products_df")
        print(f"Available columns: {list(products_df.columns)}")
        return pd.DataFrame()
    
    # Check if product_category_name already exists in sales_df
    if 'product_category_name' in sales_df.columns:
        print("Product category already exists in sales data, using existing categories")
        category_sales = sales_df.copy()
    else:
        # Merge with product categories
        merge_cols = ['product_id', 'product_category_name']
        available_cols = [col for col in merge_cols if col in products_df.columns]
        
        if len(available_cols) < 2:
            print(f"Warning: Required columns not available. Found: {available_cols}")
            return pd.DataFrame()
            
        category_sales = sales_df.merge(
            products_df[available_cols], 
            on='product_id', 
            how='left'
        )
    
    # Handle duplicate category columns from merge
    if 'product_category_name_x' in category_sales.columns:
        category_sales['product_category_name'] = category_sales['product_category_name_x'].fillna(category_sales['product_category_name_y'])
        category_sales = category_sales.drop(['product_category_name_x', 'product_category_name_y'], axis=1)
    
    # Check if merge was successful
    if 'product_category_name' not in category_sales.columns:
        print("Error: product_category_name not found after merge")
        print(f"Columns after merge: {list(category_sales.columns)}")
        return pd.DataFrame()
    
    # Remove rows where category is null
    category_sales = category_sales.dropna(subset=['product_category_name'])
    
    if category_sales.empty:
        print("Warning: No data available after removing null categories")
        return pd.DataFrame()
    
    # Calculate category metrics
    category_metrics = category_sales.groupby('product_category_name').agg({
        price_column: ['sum', 'mean', 'count'],
        'order_id': 'nunique',
        'product_id': 'nunique'
    }).round(2)
    
    # Flatten columns
    category_metrics.columns = ['total_revenue', 'avg_item_price', 'total_items', 'total_orders', 'unique_products']
    category_metrics = category_metrics.reset_index()
    
    # Calculate additional metrics
    category_metrics['avg_order_value'] = (category_metrics['total_revenue'] / category_metrics['total_orders']).round(2)
    category_metrics['items_per_order'] = (category_metrics['total_items'] / category_metrics['total_orders']).round(2)
    category_metrics['revenue_per_product'] = (category_metrics['total_revenue'] / category_metrics['unique_products']).round(2)
    
    # Calculate revenue share
    total_revenue = category_metrics['total_revenue'].sum()
    category_metrics['revenue_share_pct'] = (category_metrics['total_revenue'] / total_revenue * 100).round(2)
    
    # Sort by revenue descending
    category_metrics = category_metrics.sort_values('total_revenue', ascending=False)
    
    return category_metrics


def calculate_geographic_metrics(sales_df: pd.DataFrame, 
                               orders_df: pd.DataFrame,
                               customers_df: pd.DataFrame,
                               price_column: str = 'price',
                               geographic_level: str = 'state') -> pd.DataFrame:
    """
    Calculate metrics by geographic region.
    
    Args:
        sales_df: Sales DataFrame
        orders_df: Orders DataFrame
        customers_df: Customers DataFrame
        price_column: Name of price column
        geographic_level: Level of geography ('state', 'city', or 'zip')
        
    Returns:
        DataFrame with geographic metrics
    """
    # Check if geographic data already exists in sales_df
    if geographic_level == 'state' and 'customer_state' in sales_df.columns:
        print("Geographic data already exists in sales data, using existing data")
        geo_sales = sales_df.copy()
        group_col = 'customer_state'
    else:
        # Merge with customer geography
        geo_sales = sales_df.copy()
        
        # Add customer_id if not present
        if 'customer_id' not in geo_sales.columns:
            geo_sales = geo_sales.merge(orders_df[['order_id', 'customer_id']], on='order_id', how='left')
        
        # Add geographic information
        geo_cols = ['customer_id']
        if geographic_level == 'state':
            geo_cols.append('customer_state')
            group_col = 'customer_state'
        elif geographic_level == 'city':
            geo_cols.extend(['customer_state', 'customer_city'])
            group_col = ['customer_state', 'customer_city']
        else:  # zip
            geo_cols.extend(['customer_state', 'customer_city', 'customer_zip_code_prefix'])
            group_col = ['customer_state', 'customer_zip_code_prefix']
        
        # Filter available columns
        available_geo_cols = [col for col in geo_cols if col in customers_df.columns]
        
        if len(available_geo_cols) < 2:  # Need at least customer_id and one geo column
            print(f"Warning: Insufficient geographic columns available. Found: {available_geo_cols}")
            return pd.DataFrame()
        
        geo_sales = geo_sales.merge(customers_df[available_geo_cols], on='customer_id', how='left')
    
    # Remove rows where geographic info is missing
    if geographic_level == 'state':
        if 'customer_state' not in geo_sales.columns:
            print("Error: customer_state column not found")
            print(f"Available columns: {list(geo_sales.columns)}")
            return pd.DataFrame()
            
        geo_sales = geo_sales.dropna(subset=['customer_state'])
        group_col = 'customer_state'
    
    # Check if we have data after cleaning
    if geo_sales.empty:
        print("Warning: No geographic data available after filtering")
        return pd.DataFrame()
    
    # Calculate geographic metrics
    if isinstance(group_col, list):
        # For multi-level grouping
        if all(col in geo_sales.columns for col in group_col):
            geo_metrics = geo_sales.groupby(group_col).agg({
                price_column: ['sum', 'mean'],
                'order_id': 'nunique',
                'customer_id': 'nunique'
            }).round(2)
        else:
            missing_cols = [col for col in group_col if col not in geo_sales.columns]
            print(f"Warning: Missing columns for grouping: {missing_cols}")
            return pd.DataFrame()
    else:
        # For single-level grouping
        if group_col in geo_sales.columns:
            geo_metrics = geo_sales.groupby(group_col).agg({
                price_column: ['sum', 'mean'],
                'order_id': 'nunique',
                'customer_id': 'nunique'
            }).round(2)
        else:
            print(f"Warning: Grouping column '{group_col}' not found in data")
            print(f"Available columns: {list(geo_sales.columns)}")
            return pd.DataFrame()
    
    # Flatten columns
    geo_metrics.columns = ['total_revenue', 'avg_item_price', 'total_orders', 'unique_customers']
    geo_metrics = geo_metrics.reset_index()
    
    # Calculate additional metrics
    geo_metrics['avg_order_value'] = (geo_metrics['total_revenue'] / geo_metrics['total_orders']).round(2)
    geo_metrics['revenue_per_customer'] = (geo_metrics['total_revenue'] / geo_metrics['unique_customers']).round(2)
    geo_metrics['orders_per_customer'] = (geo_metrics['total_orders'] / geo_metrics['unique_customers']).round(2)
    
    # Calculate revenue share
    total_revenue = geo_metrics['total_revenue'].sum()
    geo_metrics['revenue_share_pct'] = (geo_metrics['total_revenue'] / total_revenue * 100).round(2)
    
    # Sort by revenue
    geo_metrics = geo_metrics.sort_values('total_revenue', ascending=False)
    
    return geo_metrics


def calculate_customer_experience_metrics(sales_df: pd.DataFrame, 
                                        reviews_df: pd.DataFrame,
                                        date_column: str = 'order_purchase_timestamp') -> Dict:
    """
    Calculate customer experience and satisfaction metrics.
    
    Args:
        sales_df: Sales DataFrame with delivery information
        reviews_df: Reviews DataFrame
        date_column: Name of date column
        
    Returns:
        Dictionary containing customer experience metrics
    """
    metrics = {}
    
    # Check if review_score already exists in sales_df
    if 'review_score' in sales_df.columns:
        print("Review score already exists in sales data, using existing data")
        experience_df = sales_df.copy()
    else:
        # Merge with reviews
        experience_df = sales_df.merge(reviews_df[['order_id', 'review_score']], on='order_id', how='left')
    
    # Handle duplicate review_score columns from merge (if any)
    if 'review_score_x' in experience_df.columns and 'review_score_y' in experience_df.columns:
        # Use the column with more data, or fallback to _x
        if experience_df['review_score_y'].notna().sum() > experience_df['review_score_x'].notna().sum():
            experience_df['review_score'] = experience_df['review_score_y']
        else:
            experience_df['review_score'] = experience_df['review_score_x']
        # Drop duplicate columns
        experience_df = experience_df.drop(['review_score_x', 'review_score_y'], axis=1, errors='ignore')
    
    # Deduplicate by order for delivery metrics
    order_level_df = experience_df.drop_duplicates(subset=['order_id'])
    
    # Review score metrics
    if 'review_score' in experience_df.columns and not experience_df['review_score'].isna().all():
        metrics['avg_review_score'] = experience_df['review_score'].mean()
        metrics['median_review_score'] = experience_df['review_score'].median()
        metrics['review_score_distribution'] = experience_df['review_score'].value_counts(normalize=True).to_dict()
        
        # Satisfaction rate (4-5 stars)
        high_satisfaction = experience_df[experience_df['review_score'] >= 4]['review_score'].count()
        total_reviews = experience_df['review_score'].count()
        metrics['satisfaction_rate_pct'] = (high_satisfaction / total_reviews * 100) if total_reviews > 0 else 0
    
    # Delivery speed metrics
    if 'delivery_days' in order_level_df.columns:
        delivery_data = order_level_df.dropna(subset=['delivery_days'])
        
        if not delivery_data.empty:
            metrics['avg_delivery_days'] = delivery_data['delivery_days'].mean()
            metrics['median_delivery_days'] = delivery_data['delivery_days'].median()
            
            # Delivery speed categories
            if 'delivery_speed_category' in delivery_data.columns:
                delivery_distribution = delivery_data['delivery_speed_category'].value_counts(normalize=True)
                metrics['delivery_speed_distribution'] = delivery_distribution.to_dict()
            
            # Fast delivery rate (<=3 days)
            fast_delivery = delivery_data[delivery_data['delivery_days'] <= 3]['delivery_days'].count()
            total_delivered = len(delivery_data)
            metrics['fast_delivery_rate_pct'] = (fast_delivery / total_delivered * 100) if total_delivered > 0 else 0
    
    # Delivery speed vs satisfaction correlation
    if 'delivery_days' in experience_df.columns and 'review_score' in experience_df.columns:
        correlation_data = experience_df.dropna(subset=['delivery_days', 'review_score'])
        
        if len(correlation_data) > 10:  # Minimum sample size
            # Group by delivery speed category and calculate avg review
            if 'delivery_speed_category' in correlation_data.columns:
                speed_satisfaction = correlation_data.groupby('delivery_speed_category')['review_score'].agg(['mean', 'count'])
                metrics['delivery_speed_vs_satisfaction'] = speed_satisfaction.to_dict()
            
            # Calculate correlation coefficient
            correlation = correlation_data['delivery_days'].corr(correlation_data['review_score'])
            metrics['delivery_satisfaction_correlation'] = correlation
    
    return metrics


def calculate_operational_metrics(sales_df: pd.DataFrame, 
                                orders_df: pd.DataFrame) -> Dict:
    """
    Calculate operational performance metrics.
    
    Args:
        sales_df: Sales DataFrame
        orders_df: Orders DataFrame with status information
        
    Returns:
        Dictionary containing operational metrics
    """
    metrics = {}
    
    # Order status distribution
    if 'order_status' in orders_df.columns:
        status_dist = orders_df['order_status'].value_counts(normalize=True)
        metrics['order_status_distribution'] = status_dist.to_dict()
        
        # Key operational rates
        total_orders = len(orders_df)
        metrics['delivery_rate_pct'] = (status_dist.get('delivered', 0) * 100)
        metrics['cancellation_rate_pct'] = (status_dist.get('canceled', 0) * 100)
        metrics['return_rate_pct'] = (status_dist.get('returned', 0) * 100)
    
    # Revenue from delivered orders only
    delivered_sales = sales_df[sales_df['order_status'] == 'delivered'] if 'order_status' in sales_df.columns else sales_df
    metrics['delivered_revenue'] = delivered_sales['price'].sum() if 'price' in delivered_sales.columns else 0
    
    # Calculate fulfillment efficiency
    if 'order_status' in orders_df.columns:
        successful_orders = orders_df[orders_df['order_status'].isin(['delivered', 'shipped'])]
        metrics['fulfillment_rate_pct'] = (len(successful_orders) / len(orders_df) * 100) if len(orders_df) > 0 else 0
    
    return metrics


def calculate_cohort_metrics(sales_df: pd.DataFrame, 
                           date_column: str = 'order_purchase_timestamp',
                           customer_column: str = 'customer_id',
                           price_column: str = 'price') -> pd.DataFrame:
    """
    Calculate customer cohort metrics for retention analysis.
    
    Args:
        sales_df: Sales DataFrame
        date_column: Name of date column
        customer_column: Name of customer ID column
        price_column: Name of price column
        
    Returns:
        DataFrame with cohort analysis
    """
    df = sales_df.copy()
    
    # Ensure datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Extract period information
    df['year_month'] = df[date_column].dt.to_period('M')
    
    # Get customer's first purchase month
    customer_cohorts = df.groupby(customer_column)[date_column].min().reset_index()
    customer_cohorts['cohort_month'] = customer_cohorts[date_column].dt.to_period('M')
    customer_cohorts = customer_cohorts[[customer_column, 'cohort_month']]
    
    # Merge cohort info back to sales data
    df = df.merge(customer_cohorts, on=customer_column)
    
    # Calculate period number (months since first purchase)
    df['period_number'] = (df['year_month'] - df['cohort_month']).apply(attrgetter('n'))
    
    # Create cohort table
    cohort_data = df.groupby(['cohort_month', 'period_number'])[customer_column].nunique().reset_index()
    cohort_table = cohort_data.pivot(index='cohort_month', columns='period_number', values=customer_column)
    
    # Calculate retention rates
    cohort_sizes = df.groupby('cohort_month')[customer_column].nunique()
    retention_table = cohort_table.divide(cohort_sizes, axis=0)
    
    return retention_table


def generate_metrics_summary(sales_df: pd.DataFrame,
                           products_df: pd.DataFrame,
                           orders_df: pd.DataFrame,
                           customers_df: pd.DataFrame,
                           reviews_df: pd.DataFrame,
                           analysis_period: str = "Current Period") -> Dict:
    """
    Generate a comprehensive metrics summary.
    
    Args:
        sales_df: Sales DataFrame
        products_df: Products DataFrame
        orders_df: Orders DataFrame
        customers_df: Customers DataFrame
        reviews_df: Reviews DataFrame
        analysis_period: Description of the analysis period
        
    Returns:
        Comprehensive metrics dictionary
    """
    summary = {'period': analysis_period}
    
    try:
        # Revenue metrics
        summary['revenue'] = calculate_revenue_metrics(sales_df)
        
        # Product category metrics
        summary['categories'] = calculate_product_category_metrics(sales_df, products_df)
        
        # Geographic metrics (state level)
        summary['geography'] = calculate_geographic_metrics(sales_df, orders_df, customers_df)
        
        # Customer experience metrics
        summary['customer_experience'] = calculate_customer_experience_metrics(sales_df, reviews_df)
        
        # Operational metrics
        summary['operations'] = calculate_operational_metrics(sales_df, orders_df)
        
    except Exception as e:
        warnings.warn(f"Error calculating some metrics: {str(e)}")
        
    return summary