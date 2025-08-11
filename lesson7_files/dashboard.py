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

# Import simple logging
from simple_logger import logger

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

# Theme configurations
LIGHT_THEME = {
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'glass_bg': 'rgba(255, 255, 255, 0.1)',
    'glass_border': 'rgba(255, 255, 255, 0.2)',
    'text_primary': '#2c3e50',
    'text_secondary': '#34495e',
    'text_muted': '#7f8c8d',
    'card_shadow': 'rgba(0, 0, 0, 0.1)',
    'blur': '20px',
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'info': '#17a2b8',
    'neutral': '#6c757d'
}

DARK_THEME = {
    'background': 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
    'glass_bg': 'rgba(30, 30, 50, 0.2)',
    'glass_border': 'rgba(255, 255, 255, 0.1)',
    'text_primary': '#ecf0f1',
    'text_secondary': '#bdc3c7',
    'text_muted': '#95a5a6',
    'card_shadow': 'rgba(0, 0, 0, 0.3)',
    'blur': '25px',
    'primary': '#3498db',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#1abc9c',
    'neutral': '#95a5a6'
}

def get_current_theme():
    """Get current theme based on session state."""
    return DARK_THEME if st.session_state.get('dark_theme', False) else LIGHT_THEME

def generate_glass_css(theme):
    """Generate comprehensive liquid glass CSS based on theme."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .stApp {{
        background: {theme['background']};
        font-family: 'Inter', sans-serif;
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    
    /* Main container glass effect */
    .main .block-container {{
        background: {theme['glass_bg']};
        backdrop-filter: blur({theme['blur']});
        border: 1px solid {theme['glass_border']};
        border-radius: 20px;
        box-shadow: 
            0 8px 32px {theme['card_shadow']},
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        padding: 2rem;
        margin-top: 2rem;
        transition: all 0.3s ease;
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {theme['text_primary']};
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    h1 {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, {theme['primary']}, {theme['info']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Metric cards glass effect */
    .metric-card, div[data-testid="metric-container"] {{
        background: {theme['glass_bg']};
        backdrop-filter: blur(15px);
        border: 1px solid {theme['glass_border']};
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 
            0 4px 16px {theme['card_shadow']},
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        margin: 0.5rem 0;
    }}
    
    .metric-card:hover, div[data-testid="metric-container"]:hover {{
        transform: translateY(-2px);
        box-shadow: 
            0 8px 25px {theme['card_shadow']},
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    
    /* Selectbox and input styling */
    .stSelectbox > div > div {{
        background: {theme['glass_bg']};
        backdrop-filter: blur(10px);
        border: 1px solid {theme['glass_border']};
        border-radius: 12px;
        color: {theme['text_primary']};
        transition: all 0.3s ease;
    }}
    
    .stSelectbox > div > div:hover {{
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 12px {theme['card_shadow']};
    }}
    
    /* Button styling */
    .stButton > button {{
        background: {theme['glass_bg']};
        backdrop-filter: blur(15px);
        border: 1px solid {theme['glass_border']};
        border-radius: 12px;
        color: {theme['text_primary']};
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px {theme['card_shadow']};
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 
            0 6px 20px {theme['card_shadow']},
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        background: linear-gradient(45deg, {theme['glass_bg']}, rgba(255, 255, 255, 0.1));
    }}
    
    .stButton > button:active {{
        transform: translateY(0px);
        box-shadow: 0 2px 8px {theme['card_shadow']};
    }}
    
    /* Chart containers */
    .js-plotly-plot, .plotly {{
        background: {theme['glass_bg']};
        backdrop-filter: blur(12px);
        border: 1px solid {theme['glass_border']};
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 
            0 4px 16px {theme['card_shadow']},
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
        margin: 0.5rem 0;
    }}
    
    .js-plotly-plot:hover, .plotly:hover {{
        transform: translateY(-1px);
        box-shadow: 
            0 6px 20px {theme['card_shadow']},
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }}
    
    /* Text styling */
    p, .stMarkdown {{
        color: {theme['text_secondary']};
        line-height: 1.6;
    }}
    
    /* Subheader styling */
    .stSubheader {{
        color: {theme['text_primary']};
        font-weight: 500;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {theme['glass_border']};
    }}
    
    /* Divider styling */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, {theme['glass_border']}, transparent);
        margin: 2rem 0;
    }}
    
    /* Loading spinner */
    .stSpinner > div {{
        border-color: {theme['primary']};
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {theme['glass_bg']};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {theme['glass_border']};
        border-radius: 10px;
        transition: background 0.3s ease;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(255, 255, 255, 0.3);
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 16px;
        }}
        
        h1 {{
            font-size: 2rem;
        }}
        
        .metric-card, div[data-testid="metric-container"] {{
            padding: 1rem;
            border-radius: 12px;
        }}
    }}
    
    /* Animation keyframes */
    @keyframes glow {{
        0% {{
            box-shadow: 0 4px 16px {theme['card_shadow']};
        }}
        50% {{
            box-shadow: 0 8px 25px {theme['card_shadow']}, 0 0 20px {theme['primary']}40;
        }}
        100% {{
            box-shadow: 0 4px 16px {theme['card_shadow']};
        }}
    }}
    
    .glow-animation {{
        animation: glow 2s ease-in-out infinite;
    }}
    </style>
    """

@st.cache_data
def load_and_process_data():
    """Load and process all e-commerce data with caching."""
    logger.info("Starting data loading and processing")
    
    try:
        # Load datasets
        logger.info("Loading datasets from ecommerce_data directory")
        datasets = load_datasets('ecommerce_data')
        
        # Clean and prepare data
        logger.info("Cleaning and preparing datasets")
        clean_datasets = clean_and_prepare_data(datasets)
        
        # Create consolidated sales dataset
        logger.info("Creating consolidated sales dataset")
        sales_df = create_sales_dataset(clean_datasets, order_status_filter='delivered')
        logger.info(f"Initial sales dataset created with {len(sales_df)} records")
        
        sales_df = add_product_categories(sales_df, clean_datasets['products'])
        logger.info("Product categories added to sales data")
        
        sales_df = add_customer_geography(sales_df, clean_datasets['orders'], clean_datasets['customers'])
        logger.info("Customer geography added to sales data")
        
        sales_df = add_review_data(sales_df, clean_datasets['reviews'])
        logger.info(f"Final sales dataset prepared with {len(sales_df)} records")
        
        return sales_df, clean_datasets
        
    except Exception as e:
        error_msg = f"Error loading data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
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
    theme = get_current_theme()
    fig = go.Figure()
    
    # Current period line (solid)
    fig.add_trace(go.Scatter(
        x=monthly_data['month'],
        y=monthly_data['total_revenue'],
        mode='lines+markers',
        name='Current Period',
        line=dict(color=theme['primary'], width=3),
        marker=dict(size=8)
    ))
    
    # Previous period line (dashed) if available
    if comparison_data is not None and not comparison_data.empty:
        fig.add_trace(go.Scatter(
            x=comparison_data['month'],
            y=comparison_data['total_revenue'],
            mode='lines+markers',
            name='Previous Period',
            line=dict(color=theme['neutral'], width=2, dash='dash'),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Revenue Trend Comparison",
        xaxis_title="Month",
        yaxis_title="Revenue",
        yaxis_tickformat="$,.0s",
        template='plotly_dark' if st.session_state.get('dark_theme', False) else 'plotly_white',
        height=400,
        showlegend=True,
        xaxis=dict(showgrid=True, gridcolor=theme['glass_border']),
        yaxis=dict(showgrid=True, gridcolor=theme['glass_border']),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'])
    )
    
    return fig

def create_top_categories_chart(category_metrics):
    """Create top categories bar chart."""
    theme = get_current_theme()
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
                colorbar=dict(title=dict(text="Revenue", font=dict(color=theme['text_primary'])))
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
        template='plotly_dark' if st.session_state.get('dark_theme', False) else 'plotly_white',
        height=400,
        margin=dict(l=150),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'])
    )
    
    return fig

def create_revenue_map(state_metrics):
    """Create US revenue choropleth map."""
    theme = get_current_theme()
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
        template='plotly_dark' if st.session_state.get('dark_theme', False) else 'plotly_white',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'])
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
    
    theme = get_current_theme()
    fig.update_layout(
        title="Customer Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        template='plotly_dark' if st.session_state.get('dark_theme', False) else 'plotly_white',
        height=400,
        yaxis=dict(range=[1, 5]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'])
    )
    
    return fig

def create_seasonal_pattern_chart(current_data, previous_data=None):
    """Create seasonal revenue pattern chart."""
    theme = get_current_theme()
    fig = go.Figure()
    
    # Current year
    fig.add_trace(go.Scatter(
        x=current_data['month'],
        y=current_data['total_revenue'],
        mode='lines+markers',
        name='Current Year',
        line=dict(color=theme['primary'], width=3),
        marker=dict(size=8)
    ))
    
    # Previous year if available
    if previous_data is not None and not previous_data.empty:
        fig.add_trace(go.Scatter(
            x=previous_data['month'],
            y=previous_data['total_revenue'],
            mode='lines+markers',
            name='Previous Year',
            line=dict(color=theme['neutral'], width=2, dash='dash'),
            marker=dict(size=6)
        ))
    
    # Highlight peak and low seasons
    peak_month = current_data.loc[current_data['total_revenue'].idxmax(), 'month']
    low_month = current_data.loc[current_data['total_revenue'].idxmin(), 'month']
    
    fig.add_annotation(
        x=peak_month, y=current_data.loc[current_data['month']==peak_month, 'total_revenue'].iloc[0],
        text="Peak", showarrow=True, arrowcolor=theme['success']
    )
    fig.add_annotation(
        x=low_month, y=current_data.loc[current_data['month']==low_month, 'total_revenue'].iloc[0],
        text="Low", showarrow=True, arrowcolor=theme['danger']
    )
    
    fig.update_layout(
        title="Monthly Seasonal Revenue Pattern",
        xaxis_title="Month",
        yaxis_title="Revenue",
        yaxis_tickformat="$,.0s",
        template='plotly_dark' if st.session_state.get('dark_theme', False) else 'plotly_white',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'])
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
    
    theme = get_current_theme()
    fig.update_layout(
        template='plotly_dark' if st.session_state.get('dark_theme', False) else 'plotly_white',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text_primary'])
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
    logger.info("Starting E-commerce Analytics Dashboard")
    
    st.set_page_config(
        page_title="E-commerce Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    logger.debug("Streamlit page configuration set")
    
    # Apply liquid glass theme
    theme = get_current_theme()
    st.markdown(generate_glass_css(theme), unsafe_allow_html=True)
    
    # Header with enhanced filters
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.title("E-commerce Analytics Dashboard")
    
    with col2:
        # Theme toggle
        if 'dark_theme' not in st.session_state:
            st.session_state.dark_theme = False
        
        theme_label = "🌙" if st.session_state.dark_theme else "☀️"
        if st.button(f"{theme_label} Theme", key="theme_toggle"):
            old_theme = st.session_state.dark_theme
            st.session_state.dark_theme = not st.session_state.dark_theme
            new_theme = "dark" if st.session_state.dark_theme else "light"
            logger.info(f"User switched to {new_theme} theme")
            st.rerun()
    
    with col3:
        # Year filter (default to 2023)
        years_available = [2022, 2023]
        selected_year = st.selectbox("Year", years_available, index=1)
        if 'previous_year' not in st.session_state:
            st.session_state.previous_year = selected_year
        elif st.session_state.previous_year != selected_year:
            st.session_state.previous_year = selected_year
    
    with col4:
        # Month filter
        months = {
            "All": None,
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        selected_month_name = st.selectbox("Month", list(months.keys()), index=0)
        selected_month = months[selected_month_name]
        if 'previous_month' not in st.session_state:
            st.session_state.previous_month = selected_month_name
        elif st.session_state.previous_month != selected_month_name:
            st.session_state.previous_month = selected_month_name
    
    # Load data
    logger.info("Starting data loading process")
    with st.spinner("Loading data..."):
        sales_df, clean_datasets = load_and_process_data()
    
    if sales_df is None:
        error_msg = "Failed to load data. Please check the data files."
        logger.error(error_msg)
        st.error(error_msg)
        return
    
    logger.info(f"Data loaded successfully - {len(sales_df)} records available")
    
    # Filter data based on selected year and month
    logger.info(f"Filtering data for year: {selected_year}, month: {selected_month_name}")
    
    if selected_month:
        logger.debug(f"Filtering for specific month: {selected_month}")
        current_period_df = filter_data_by_date_range(
            sales_df, start_year=selected_year, end_year=selected_year,
            start_month=selected_month, end_month=selected_month
        )
        comparison_period_df = filter_data_by_date_range(
            sales_df, start_year=selected_year-1, end_year=selected_year-1,
            start_month=selected_month, end_month=selected_month
        )
    else:
        logger.debug(f"Filtering for full year: {selected_year}")
        current_period_df = filter_data_by_date_range(
            sales_df, start_year=selected_year, end_year=selected_year
        )
        comparison_period_df = filter_data_by_date_range(
            sales_df, start_year=selected_year-1, end_year=selected_year-1
        )
    
    logger.info(f"Current period: {len(current_period_df)} records, Comparison period: {len(comparison_period_df)} records")
    
    # Calculate metrics
    logger.info("Starting metrics calculation")
    
    try:
        logger.debug("Calculating revenue metrics")
        current_metrics = calculate_revenue_metrics(current_period_df)
        
        comparison_metrics = calculate_revenue_metrics(comparison_period_df) if not comparison_period_df.empty else {}
        growth_metrics = calculate_growth_metrics(current_period_df, comparison_period_df) if not comparison_period_df.empty else {}
        
        logger.debug("Calculating customer experience metrics")
        cx_metrics = calculate_customer_experience_metrics(current_period_df, clean_datasets['reviews'])
        
        logger.debug("Calculating product category metrics")
        category_metrics = calculate_product_category_metrics(current_period_df, clean_datasets['products'])
        
        logger.debug("Calculating geographic metrics")
        state_metrics = calculate_geographic_metrics(current_period_df, clean_datasets['orders'], clean_datasets['customers'])
        
        logger.info("All metrics calculated successfully")
        
        # Log key metrics for monitoring
        if current_metrics:
            logger.debug(f"Revenue: ${current_metrics.get('total_revenue', 0):,.0f}, Orders: {current_metrics.get('total_orders', 0)}")
            
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        st.error(f"Error calculating metrics: {str(e)}")
        return
    
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
        logger.debug("Rendering revenue trend chart")
        fig = create_revenue_trend_chart(monthly_current, monthly_comparison)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not category_metrics.empty:
            logger.debug("Rendering top categories chart")
            fig = create_top_categories_chart(category_metrics)
            st.plotly_chart(fig, use_container_width=True)
        else:
            warning_msg = "Category data not available"
            logger.warning(warning_msg)
            st.warning(warning_msg)
    
    with col3:
        if not state_metrics.empty:
            logger.debug("Rendering revenue map")
            fig = create_revenue_map(state_metrics)
            st.plotly_chart(fig, use_container_width=True)
        else:
            warning_msg = "Geographic data not available"
            logger.warning(warning_msg)
            st.warning(warning_msg)
    
    # Row 2  
    col1, col2, col3 = st.columns(3)
    
    with col1:
        logger.debug("Rendering satisfaction vs delivery scatter plot")
        fig = create_satisfaction_delivery_scatter(current_period_df.copy())
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        logger.debug("Rendering seasonal pattern chart")
        fig = create_seasonal_pattern_chart(monthly_current, monthly_comparison)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        logger.debug("Rendering customer segmentation chart")
        fig = create_customer_segmentation_chart(current_period_df.copy())
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Bottom Row
    st.subheader("Operational Insights")
    create_bottom_cards(cx_metrics, state_metrics)

if __name__ == "__main__":
    try:
        logger.info("=" * 50)
        logger.info("E-commerce Analytics Dashboard Starting")
        logger.info("=" * 50)
        main()
        logger.info("Dashboard session completed successfully")
    except Exception as e:
        logger.error(f"Fatal error in dashboard: {str(e)}")
        st.error(f"A critical error occurred: {str(e)}")
        raise