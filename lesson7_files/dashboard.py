"""
E-commerce Business Analytics Dashboard

Professional Streamlit dashboard providing comprehensive e-commerce analytics 
including revenue trends, product performance, geographic insights, and 
operational metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from data_loader import (
    load_datasets, clean_and_prepare_data, create_sales_dataset,
    filter_data_by_date_range, add_product_categories, 
    add_customer_geography, add_review_data
)
from business_metrics import (
    calculate_revenue_metrics, calculate_growth_metrics, 
    calculate_monthly_trends, calculate_product_category_metrics,
    calculate_geographic_metrics, calculate_customer_experience_metrics,
    calculate_operational_metrics
)

# Business color scheme
COLORS = {
    'primary': '#1f77b4',      # Professional blue
    'success': '#2ca02c',      # Growth green  
    'danger': '#d62728',       # Decline red
    'warning': '#ff7f0e',      # Alert orange
    'info': '#17a2b8',         # Information teal
    'neutral': '#6c757d'       # Neutral gray
}

@st.cache_data
def load_and_process_data():
    """Load and process all e-commerce data with caching."""
    try:
        # Load datasets
        datasets = load_datasets('ecommerce_data')
        
        # Clean and prepare data
        clean_datasets = clean_and_prepare_data(datasets)
        
        # Create consolidated sales dataset
        sales_df = create_sales_dataset(clean_datasets, order_status_filter='delivered')
        sales_df = add_product_categories(sales_df, clean_datasets['products'])
        sales_df = add_customer_geography(sales_df, clean_datasets['orders'], clean_datasets['customers'])
        sales_df = add_review_data(sales_df, clean_datasets['reviews'])
        
        return sales_df, clean_datasets
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def create_metric_card(title, value, delta=None, delta_pct=None):
    """Create a styled metric card."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=f"{delta:+.2f}%" if delta_pct and delta else delta
        )

def format_currency(value):
    """Format currency values for display."""
    if value >= 1000000:
        return f"${value/1000000:.1f}M"
    elif value >= 1000:
        return f"${value/1000:.0f}K"
    else:
        return f"${value:.0f}"

def format_number(value):
    """Format numbers for display."""
    if value >= 1000000:
        return f"{value/1000000:.1f}M"
    elif value >= 1000:
        return f"{value/1000:.0f}K"
    else:
        return f"{value:.0f}"

def create_kpi_row(current_metrics, comparison_metrics, growth_metrics, cx_metrics):
    """Create KPI cards row."""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        revenue_delta = growth_metrics.get('revenue_growth_pct', 0)
        st.metric(
            "Total Revenue",
            format_currency(current_metrics.get('total_revenue', 0)),
            f"{revenue_delta:+.2f}%"
        )
    
    with col2:
        monthly_growth = growth_metrics.get('revenue_growth_pct', 0) / 12  # Approximate monthly
        st.metric(
            "Monthly Growth", 
            f"{monthly_growth:+.2f}%",
            f"{monthly_growth:+.2f}%"
        )
    
    with col3:
        aov_delta = growth_metrics.get('aov_growth_pct', 0)
        st.metric(
            "Average Order Value",
            format_currency(current_metrics.get('avg_order_value', 0)),
            f"{aov_delta:+.2f}%"
        )
    
    with col4:
        orders_delta = growth_metrics.get('order_growth_pct', 0)
        st.metric(
            "Total Orders",
            format_number(current_metrics.get('total_orders', 0)),
            f"{orders_delta:+.2f}%"
        )
    
    with col5:
        satisfaction = cx_metrics.get('avg_review_score', 0)
        satisfaction_delta = 0  # Would need historical data for trend
        st.metric(
            "Customer Satisfaction",
            f"{satisfaction:.2f}/5.0",
            f"{satisfaction_delta:+.2f}%" if satisfaction_delta else None
        )

def create_revenue_trend_chart(monthly_data, comparison_data=None):
    """Create revenue trend line chart."""
    fig = go.Figure()
    
    # Current period line (solid)
    fig.add_trace(go.Scatter(
        x=monthly_data['month'],
        y=monthly_data['total_revenue'],
        mode='lines+markers',
        name='Current Period',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8)
    ))
    
    # Previous period line (dashed) if available
    if comparison_data is not None and not comparison_data.empty:
        fig.add_trace(go.Scatter(
            x=comparison_data['month'],
            y=comparison_data['total_revenue'],
            mode='lines+markers',
            name='Previous Period',
            line=dict(color=COLORS['neutral'], width=2, dash='dash'),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Revenue Trend Comparison",
        xaxis_title="Month",
        yaxis_title="Revenue",
        yaxis_tickformat="$,.0s",
        template='plotly_white',
        height=400,
        showlegend=True,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )
    
    return fig

def create_top_categories_chart(category_metrics):
    """Create top categories bar chart."""
    top_categories = category_metrics.head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            y=top_categories['product_category_name'].str.replace('_', ' ').str.title(),
            x=top_categories['total_revenue'],
            orientation='h',
            marker=dict(
                color=top_categories['total_revenue'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="Revenue")
            ),
            text=[format_currency(x) for x in top_categories['total_revenue']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Categories by Revenue",
        xaxis_title="Revenue",
        yaxis_title="Category",
        yaxis={'categoryorder': 'total ascending'},
        template='plotly_white',
        height=400,
        margin=dict(l=150)
    )
    
    return fig

def create_revenue_map(state_metrics):
    """Create US revenue choropleth map."""
    fig = px.choropleth(
        state_metrics,
        locations='customer_state',
        color='total_revenue',
        locationmode='USA-states',
        scope='usa',
        title='Revenue by State',
        color_continuous_scale='Blues',
        labels={'total_revenue': 'Revenue ($)'},
        hover_data={
            'total_orders': True,
            'unique_customers': True,
            'total_revenue': ':$,.0f'
        }
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    
    return fig

def create_satisfaction_delivery_scatter(sales_df):
    """Create customer satisfaction vs delivery time scatter plot."""
    # Create delivery time buckets
    bins = [0, 3, 7, 14, float('inf')]
    labels = ['1-3 days', '4-7 days', '8-14 days', '15+ days']
    sales_df['delivery_bucket'] = pd.cut(sales_df['delivery_days'], bins=bins, labels=labels, right=False)
    
    # Calculate metrics by bucket
    bucket_metrics = sales_df.groupby('delivery_bucket').agg({
        'review_score': 'mean',
        'order_id': 'count'
    }).reset_index()
    
    fig = go.Figure(data=go.Scatter(
        x=bucket_metrics['delivery_bucket'],
        y=bucket_metrics['review_score'],
        mode='markers',
        marker=dict(
            size=bucket_metrics['order_id']/20,  # Size by order volume
            color=bucket_metrics['review_score'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Review Score"),
            sizemode='diameter',
            sizeref=2.*max(bucket_metrics['order_id'])/(40.**2),
            sizemin=4
        ),
        text=[f'Orders: {orders}<br>Avg Score: {score:.2f}' 
              for orders, score in zip(bucket_metrics['order_id'], bucket_metrics['review_score'])],
        hovertemplate='<b>%{x}</b><br>%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Customer Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        template='plotly_white',
        height=400,
        yaxis=dict(range=[1, 5])
    )
    
    return fig

def create_seasonal_pattern_chart(current_data, previous_data=None):
    """Create seasonal revenue pattern chart."""
    fig = go.Figure()
    
    # Current year
    fig.add_trace(go.Scatter(
        x=current_data['month'],
        y=current_data['total_revenue'],
        mode='lines+markers',
        name='Current Year',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8)
    ))
    
    # Previous year if available
    if previous_data is not None and not previous_data.empty:
        fig.add_trace(go.Scatter(
            x=previous_data['month'],
            y=previous_data['total_revenue'],
            mode='lines+markers',
            name='Previous Year',
            line=dict(color=COLORS['neutral'], width=2, dash='dash'),
            marker=dict(size=6)
        ))
    
    # Highlight peak and low seasons
    peak_month = current_data.loc[current_data['total_revenue'].idxmax(), 'month']
    low_month = current_data.loc[current_data['total_revenue'].idxmin(), 'month']
    
    fig.add_annotation(
        x=peak_month, y=current_data.loc[current_data['month']==peak_month, 'total_revenue'].iloc[0],
        text="Peak", showarrow=True, arrowcolor=COLORS['success']
    )
    fig.add_annotation(
        x=low_month, y=current_data.loc[current_data['month']==low_month, 'total_revenue'].iloc[0],
        text="Low", showarrow=True, arrowcolor=COLORS['danger']
    )
    
    fig.update_layout(
        title="Monthly Seasonal Revenue Pattern",
        xaxis_title="Month",
        yaxis_title="Revenue",
        yaxis_tickformat="$,.0s",
        template='plotly_white',
        height=400,
        showlegend=True
    )
    
    return fig

def create_customer_segmentation_chart(sales_df):
    """Create customer segmentation bubble chart."""
    # Calculate customer metrics
    customer_summary = sales_df.groupby('customer_id').agg({
        'price': 'sum',  # Customer lifetime value
        'order_id': 'nunique',  # Order frequency
        'review_score': 'mean'  # Satisfaction score
    }).reset_index()
    
    customer_summary.columns = ['customer_id', 'clv', 'order_frequency', 'satisfaction']
    
    # Create segments for visualization (sample for performance)
    if len(customer_summary) > 1000:
        customer_sample = customer_summary.sample(1000)
    else:
        customer_sample = customer_summary
    
    # Count customers in each segment for bubble size
    segment_counts = customer_sample.groupby(['order_frequency', pd.cut(customer_sample['clv'], bins=5)]).size().reset_index()
    
    fig = px.scatter(
        customer_sample,
        x='order_frequency',
        y='clv',
        size=customer_sample['order_frequency'],  # Bubble size
        color='satisfaction',
        color_continuous_scale='RdYlGn',
        title="Customer Segmentation Analysis",
        labels={
            'order_frequency': 'Order Frequency (Number of Orders)',
            'clv': 'Customer Lifetime Value ($)',
            'satisfaction': 'Satisfaction Score'
        }
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    
    return fig

def create_bottom_cards(cx_metrics, state_metrics):
    """Create bottom row cards."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_delivery = cx_metrics.get('avg_delivery_days', 0)
        delivery_trend = 0  # Would need historical data
        st.metric(
            "Average Delivery Time",
            f"{avg_delivery:.1f} days",
            f"{delivery_trend:+.2f}%" if delivery_trend else None
        )
    
    with col2:
        review_score = cx_metrics.get('avg_review_score', 0)
        stars = '★' * int(review_score) + '☆' * (5 - int(review_score))
        st.markdown(f"""
        <div style='text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>{review_score:.2f}</h1>
            <div style='font-size: 1.5em; color: #ffd700;'>{stars}</div>
            <p style='margin: 0; color: #666;'>Average Review Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if not state_metrics.empty:
            states_served = len(state_metrics)
            top_state = state_metrics.iloc[0]
            top_state_revenue = format_currency(top_state['total_revenue'])
            
            st.markdown(f"""
            <div style='text-align: center;'>
                <h1 style='margin: 0; font-size: 3em;'>{states_served}</h1>
                <p style='margin: 5px 0; font-weight: bold;'>States Served</p>
                <p style='margin: 0; color: #666;'>Top: {top_state['customer_state']} ({top_state_revenue})</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="E-commerce Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    h1 {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stSelectbox > div > div {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("E-commerce Analytics Dashboard")
    
    with col2:
        # Date range filter
        years_available = [2022, 2023]
        selected_year = st.selectbox("Select Year", years_available, index=1)
    
    # Load data
    with st.spinner("Loading data..."):
        sales_df, clean_datasets = load_and_process_data()
    
    if sales_df is None:
        st.error("Failed to load data. Please check the data files.")
        return
    
    # Filter data based on selected year
    current_period_df = filter_data_by_date_range(
        sales_df, start_year=selected_year, end_year=selected_year
    )
    comparison_period_df = filter_data_by_date_range(
        sales_df, start_year=selected_year-1, end_year=selected_year-1
    )
    
    # Calculate metrics
    current_metrics = calculate_revenue_metrics(current_period_df)
    comparison_metrics = calculate_revenue_metrics(comparison_period_df) if not comparison_period_df.empty else {}
    growth_metrics = calculate_growth_metrics(current_period_df, comparison_period_df) if not comparison_period_df.empty else {}
    cx_metrics = calculate_customer_experience_metrics(current_period_df, clean_datasets['reviews'])
    category_metrics = calculate_product_category_metrics(current_period_df, clean_datasets['products'])
    state_metrics = calculate_geographic_metrics(current_period_df, clean_datasets['orders'], clean_datasets['customers'])
    
    # Calculate monthly trends
    monthly_current = calculate_monthly_trends(current_period_df, year_filter=selected_year)
    monthly_comparison = calculate_monthly_trends(comparison_period_df, year_filter=selected_year-1) if not comparison_period_df.empty else None
    
    # KPI Row
    st.subheader("Key Performance Indicators")
    create_kpi_row(current_metrics, comparison_metrics, growth_metrics, cx_metrics)
    
    st.markdown("---")
    
    # Charts Grid (2x3 layout)
    st.subheader("Performance Analytics")
    
    # Row 1
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = create_revenue_trend_chart(monthly_current, monthly_comparison)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not category_metrics.empty:
            fig = create_top_categories_chart(category_metrics)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Category data not available")
    
    with col3:
        if not state_metrics.empty:
            fig = create_revenue_map(state_metrics)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Geographic data not available")
    
    # Row 2  
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = create_satisfaction_delivery_scatter(current_period_df.copy())
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_seasonal_pattern_chart(monthly_current, monthly_comparison)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = create_customer_segmentation_chart(current_period_df.copy())
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Bottom Row
    st.subheader("Operational Insights")
    create_bottom_cards(cx_metrics, state_metrics)

if __name__ == "__main__":
    main()