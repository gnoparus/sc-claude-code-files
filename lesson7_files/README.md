# E-commerce Business Analytics Framework

## Overview

This refactored analysis framework provides a comprehensive, configurable solution for analyzing e-commerce business performance. The framework transforms raw transactional data into actionable business insights through standardized metrics, professional visualizations, and reusable code modules.

## Key Features

- **Configurable Analysis Periods**: Easily adjust date ranges and comparison periods
- **Modular Architecture**: Separate modules for data loading and business metrics
- **Professional Visualizations**: Business-oriented charts with consistent styling
- **Comprehensive Metrics**: Revenue, growth, customer experience, and operational KPIs
- **Clean Documentation**: Well-structured notebook with clear business context
- **Reusable Code**: Functions that can be applied to future datasets

## Project Structure

```
├── EDA_Refactored.ipynb          # Main analysis notebook
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

### 2. Configure Analysis Period

Edit the configuration section in `EDA_Refactored.ipynb`:

```python
ANALYSIS_CONFIG = {
    'current_year': 2023,        # Year to analyze
    'comparison_year': 2022,     # Comparison year
    'current_start_month': 1,    # Start month (1-12)
    'current_end_month': 12,     # End month (1-12)
    'data_path': 'ecommerce_data'
}
```

### 3. Run Analysis

Open `EDA_Refactored.ipynb` in Jupyter and run all cells to generate the complete analysis.

## Data Requirements

The framework expects five CSV files in the specified data directory:

| File | Required Columns | Description |
|------|------------------|-------------|
| `orders_dataset.csv` | order_id, customer_id, order_status, order_purchase_timestamp | Order information and status |
| `order_items_dataset.csv` | order_id, product_id, price, freight_value | Individual items and pricing |
| `products_dataset.csv` | product_id, product_category_name | Product catalog and categories |
| `customers_dataset.csv` | customer_id, customer_state, customer_city | Customer geographic information |
| `order_reviews_dataset.csv` | order_id, review_score, review_creation_date | Customer satisfaction data |

## Analysis Sections

### 1. Revenue Analysis
- Total revenue and growth metrics
- Monthly revenue trends and seasonality
- Average order value (AOV) analysis
- Revenue distribution and percentiles

### 2. Product Category Performance
- Category-wise revenue breakdown
- Performance metrics (AOV, items per order)
- Market share analysis
- Category satisfaction scores

### 3. Geographic Market Analysis
- State-wise revenue distribution
- Geographic performance metrics
- Market concentration analysis
- Interactive geographic visualizations

### 4. Customer Experience Analysis
- Review score distribution and trends
- Delivery performance metrics
- Satisfaction vs delivery speed correlation
- Customer experience KPIs

### 5. Operational Performance
- Order fulfillment rates
- Delivery success metrics
- Cancellation and return rates
- Operational efficiency indicators

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

## Customization Guide

### Changing Analysis Period

To analyze a different time period, modify the configuration:

```python
# Example: Analyze Q4 2023 vs Q4 2022
ANALYSIS_CONFIG = {
    'current_year': 2023,
    'comparison_year': 2022,
    'current_start_month': 10,   # October
    'current_end_month': 12,     # December
    'data_path': 'ecommerce_data'
}
```

### Adding New Metrics

1. **Add calculation function** to `business_metrics.py`:
```python
def calculate_custom_metric(sales_df):
    # Your calculation logic here
    return metric_value
```

2. **Call function** in the notebook:
```python
custom_result = calculate_custom_metric(current_period_df)
```

### Extending Visualizations

Use the established color scheme for consistency:

```python
BUSINESS_COLORS = {
    'primary': '#1f77b4',      # Professional blue
    'success': '#2ca02c',      # Growth green  
    'warning': '#ff7f0e',      # Alert orange
    'danger': '#d62728',       # Decline red
    'info': '#17a2b8',         # Information teal
    'neutral': '#6c757d'       # Neutral gray
}
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

**Missing Data Errors**
```python
# Check data availability
summary = get_data_summary(sales_df)
print(summary['missing_values'])
```

**Empty Results**
- Verify date ranges match available data
- Check order status filters (delivered vs all orders)
- Confirm geographic data availability

**Performance Issues**
- Filter datasets early in the process
- Use date range filtering before heavy calculations
- Consider reducing visualization complexity for large datasets

### Error Handling

The framework includes built-in error handling:
- Missing geographic data gracefully handled
- Empty DataFrames managed with informative messages
- Date parsing errors caught and reported

## Future Enhancements

### Potential Additions
- Customer cohort analysis
- Seasonal decomposition
- Predictive analytics
- A/B testing framework
- Real-time dashboard integration

### Scalability Considerations
- Database connectivity for larger datasets
- Parallel processing for complex calculations
- Caching mechanisms for repeated analyses
- Automated report generation

## Support

For questions or issues with the analysis framework:

1. Check the troubleshooting section above
2. Review module documentation and function docstrings
3. Verify data format requirements
4. Test with smaller date ranges if performance issues occur

## Version History

- **v1.0**: Initial refactored analysis framework
  - Modular architecture implementation
  - Configurable analysis periods
  - Professional visualization suite
  - Comprehensive business metrics
  - Complete documentation

---

*This framework transforms complex e-commerce data into clear, actionable business insights that support data-driven decision making.*