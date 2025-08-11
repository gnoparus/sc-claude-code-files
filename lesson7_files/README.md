# E-commerce Business Analytics Dashboard

## Overview

This professional Streamlit dashboard provides comprehensive e-commerce analytics with an interactive web interface. Built from the refactored analysis framework, it transforms raw transactional data into actionable business insights through real-time visualizations, KPI tracking, and dynamic filtering.

## Key Features

- **Interactive Streamlit Dashboard**: Professional web interface with real-time updates
- **KPI Dashboard**: 5-card KPI row with trend indicators and growth metrics
- **Dynamic Filtering**: Year selection with automatic data filtering
- **6-Chart Analytics Grid**: Revenue trends, category performance, geographic insights
- **Professional Styling**: Consistent color coding and business-oriented design
- **Responsive Layout**: Optimized for desktop and mobile viewing
- **Real-time Calculations**: Automatic metric updates based on selected filters

## Project Structure

```
├── dashboard.py                  # Main Streamlit dashboard application
├── EDA_Refactored.ipynb          # Original analysis notebook
├── data_loader.py                # Data loading and processing functions
├── business_metrics.py           # Business metric calculation functions
├── requirements.txt              # Python dependencies
├── README.md                     # This documentation
└── ecommerce_data/               # Data directory
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── products_dataset.csv
    ├── customers_dataset.csv
    └── order_reviews_dataset.csv
```

## Quick Start

### 1. Setup Environment

```bash
# Install required dependencies
pip install -r requirements.txt
```

### 2. Launch Dashboard

```bash
# Start the Streamlit dashboard
streamlit run dashboard.py
```

### 3. Access Dashboard

Open your web browser and navigate to:
```
http://localhost:8501
```

### 4. Use Interactive Features

- **Year Filter**: Select different years using the dropdown in the header
- **KPI Cards**: View key metrics with trend indicators
- **Interactive Charts**: Hover over charts for detailed information
- **Responsive Design**: Access from desktop or mobile devices

## Data Requirements

The framework expects five CSV files in the specified data directory:

| File | Required Columns | Description |
|------|------------------|-------------|
| `orders_dataset.csv` | order_id, customer_id, order_status, order_purchase_timestamp | Order information and status |
| `order_items_dataset.csv` | order_id, product_id, price, freight_value | Individual items and pricing |
| `products_dataset.csv` | product_id, product_category_name | Product catalog and categories |
| `customers_dataset.csv` | customer_id, customer_state, customer_city | Customer geographic information |
| `order_reviews_dataset.csv` | order_id, review_score, review_creation_date | Customer satisfaction data |

## Dashboard Layout

### Header Section
- **Title**: E-commerce Analytics Dashboard
- **Date Filter**: Year selection dropdown (applies globally to all metrics)

### KPI Row (5 Cards)
- **Total Revenue**: Current period revenue with YoY growth indicator
- **Monthly Growth**: Average monthly growth rate with trend
- **Average Order Value**: AOV with period-over-period change
- **Total Orders**: Order count with growth percentage
- **Customer Satisfaction**: Review score with trend indicator

### Charts Grid (2x3 Layout)

**Row 1:**
- **Revenue Trend Chart**: Line chart comparing current vs previous period
- **Top Categories**: Bar chart of top 10 categories by revenue
- **Revenue by State**: US choropleth map with color-coded revenue

**Row 2:**  
- **Satisfaction vs Delivery**: Scatter plot showing delivery time impact
- **Seasonal Patterns**: Monthly revenue comparison with peak/low seasons
- **Customer Segmentation**: Bubble chart of customer value segments

### Bottom Cards (3 Cards)
- **Average Delivery Time**: Delivery performance with trend
- **Review Score**: Large display with star rating and subtitle
- **Geographic Reach**: States served count with top performing state

## Key Business Metrics

### Revenue Metrics
- **Total Revenue**: Sum of all delivered orders
- **Revenue Growth**: Year-over-year percentage change
- **Average Order Value (AOV)**: Total revenue ÷ number of orders
- **Revenue per Customer**: Total revenue ÷ unique customers

### Customer Experience Metrics
- **Customer Satisfaction**: Percentage of 4-5 star reviews
- **Average Review Score**: Mean customer rating (1-5 scale)
- **Fast Delivery Rate**: Percentage of orders delivered ≤3 days
- **Average Delivery Time**: Mean days from purchase to delivery

### Operational Metrics
- **Delivery Rate**: Percentage of orders successfully delivered
- **Fulfillment Rate**: Percentage of orders shipped or delivered
- **Cancellation Rate**: Percentage of orders canceled
- **Return Rate**: Percentage of orders returned

## Dashboard Customization

### Adding New KPI Cards

1. **Calculate metric** in dashboard.py:
```python
def create_kpi_row(current_metrics, comparison_metrics, growth_metrics, cx_metrics):
    # Add new column
    col6 = st.columns(6)[5]  # Add 6th column
    with col6:
        st.metric("New Metric", value, delta)
```

2. **Update layout** to accommodate new cards:
```python
col1, col2, col3, col4, col5, col6 = st.columns(6)
```

### Adding New Charts

1. **Create chart function**:
```python
def create_new_chart(data):
    fig = go.Figure()
    # Chart logic here
    return fig
```

2. **Add to grid layout**:
```python
with col3:  # Or create new row
    fig = create_new_chart(filtered_data)
    st.plotly_chart(fig, use_container_width=True)
```

### Styling Customization

The dashboard uses a consistent color scheme:

```python
COLORS = {
    'primary': '#1f77b4',      # Professional blue
    'success': '#2ca02c',      # Growth green  
    'danger': '#d62728',       # Decline red
    'warning': '#ff7f0e',      # Alert orange
    'info': '#17a2b8',         # Information teal
    'neutral': '#6c757d'       # Neutral gray
}
```

### Adding Filters

Extend the header section with additional filters:

```python
with col2:
    selected_year = st.selectbox("Select Year", years_available)
    selected_state = st.selectbox("Select State", states_available)  # New filter
```

## Module Documentation

### data_loader.py

**Core Functions:**
- `load_datasets()`: Load all CSV files from directory
- `clean_and_prepare_data()`: Parse dates and clean data
- `create_sales_dataset()`: Merge tables into analysis-ready dataset
- `filter_data_by_date_range()`: Filter by configurable date ranges
- `add_product_categories()`: Enrich with product information
- `add_customer_geography()`: Add geographic data
- `add_review_data()`: Include customer satisfaction data

### business_metrics.py

**Core Functions:**
- `calculate_revenue_metrics()`: Comprehensive revenue analysis
- `calculate_growth_metrics()`: Period-over-period comparisons
- `calculate_monthly_trends()`: Time series analysis
- `calculate_product_category_metrics()`: Category performance
- `calculate_geographic_metrics()`: Regional analysis
- `calculate_customer_experience_metrics()`: Satisfaction and delivery
- `calculate_operational_metrics()`: Fulfillment and efficiency
- `generate_metrics_summary()`: Complete business overview

## Best Practices

### Performance Optimization
- Use `filter_data_by_date_range()` to reduce dataset size early
- Filter product categories before calculations for faster processing
- Consider sampling large datasets for exploratory analysis

### Data Quality
- Always check for missing values in key fields
- Validate date ranges before analysis
- Use `get_data_summary()` to understand data structure

### Visualization Guidelines
- Use consistent color schemes across all charts
- Include clear titles with date ranges
- Add proper axis labels with units
- Use appropriate chart types for data

## Troubleshooting

### Common Issues

**Dashboard Won't Start**
```bash
# Check if Streamlit is installed
pip show streamlit

# Reinstall dependencies
pip install -r requirements.txt

# Run with verbose output
streamlit run dashboard.py --logger.level debug
```

**Data Loading Errors**
- Verify `ecommerce_data/` folder exists in the same directory
- Check that all 5 CSV files are present
- Ensure CSV files have required columns
- Verify file permissions

**Blank Charts**
- Select different year from dropdown
- Check if data exists for selected time period
- Verify data files contain records for the selected year

**Performance Issues**
- Dashboard may be slow with large datasets (>100K records)
- Consider sampling data for testing
- Close other browser tabs to free up memory

**Browser Compatibility**
- Recommended: Chrome, Firefox, Safari (latest versions)
- Enable JavaScript in browser
- Clear browser cache if issues persist

### Error Handling

The dashboard includes built-in error handling:
- Graceful fallbacks for missing data
- User-friendly error messages
- Automatic data validation
- Caching for improved performance

## Future Enhancements

### Dashboard Features
- **Multi-year Comparisons**: Support for comparing multiple years simultaneously
- **Advanced Filters**: Category, state, and date range filters
- **Export Functionality**: PDF reports and CSV data exports
- **Real-time Updates**: Auto-refresh with live data connections
- **Custom Metrics**: User-defined KPI creation interface

### Visualization Improvements
- **Drill-down Capability**: Click-through from summary to detailed views
- **Animated Charts**: Time-series animations for trend visualization
- **Custom Themes**: Multiple color schemes and branding options
- **Mobile Optimization**: Enhanced responsive design for tablets/phones

### Technical Enhancements
- **Database Integration**: PostgreSQL/MySQL connectivity
- **Performance Optimization**: Lazy loading and data pagination
- **User Authentication**: Multi-user access with role-based permissions
- **API Integration**: External data source connections

## Deployment Options

### Local Development
```bash
streamlit run dashboard.py
```

### Production Deployment

**Streamlit Cloud**:
1. Push to GitHub repository
2. Connect at share.streamlit.io
3. Deploy with automatic updates

**Docker Deployment**:
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py"]
```

**Heroku Deployment**:
Add `Procfile`:
```
web: streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

## Support

For questions or issues with the dashboard:

1. Check the troubleshooting section above
2. Verify data files and directory structure
3. Test with sample data first
4. Check browser console for JavaScript errors

## Version History

- **v2.0**: Streamlit Dashboard Implementation
  - Interactive web interface with Streamlit
  - Professional KPI dashboard with 5 cards
  - 6-chart analytics grid layout  
  - Real-time filtering and calculations
  - Responsive design and styling
  
- **v1.0**: Initial refactored analysis framework
  - Modular architecture implementation
  - Jupyter notebook analysis
  - Professional visualization suite
  - Complete documentation

---

*Transform your e-commerce data into a powerful, interactive dashboard that drives data-driven business decisions.*