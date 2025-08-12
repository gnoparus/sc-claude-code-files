Convert `@EDA_Refactored.ipynb` into a professional Streamlit dashboard with this exact layout:

## Layout Structure
- **Header**: Title + date range filter (applies globally)
    - Title: left
    - Date range filter: right
- **KPI Row**: 5 cards (Total Revenue, Monthly Growth, Average Order Value, Total Orders, Customer Satisfaction)
    - Trend indicators for Total Revenue, Average Order Value, Total Orders, and Customer Satisfaction
    - Use red for negative trends and green for positive trends
- **Charts Grid**: 2x3 layout (6 charts total)
  - **Row 1:**
    - Revenue trend line chart with comparison:
        - solid line for the current period
        - dashed line for the previous period
        - Add grid lines for easier reading
        - Y-axis formatting - show values as $300K instead of $300,000
    - Top 10 categories bar chart sorted descending:
        - Use blue gradient (light shade for lower values)
        - Format values as $300K and $2M  
    - Revenue by state: US choropleth map color-coded by revenue amount:
        - Use blue gradient
  - **Row 2:**
    - Customer satisfaction vs delivery time scatter plot:
        - x-axis: Delivery time buckets (1-3 days, 4-7 days, 8-14 days, 15+ days)
        - y-axis: Average review score
        - Color points by order volume
    - Monthly seasonal revenue pattern line chart:
        - Show current year vs previous year comparison
        - Highlight peak and low seasons
        - Add trend indicators
    - Customer segmentation bubble chart:
        - x-axis: Order frequency (number of orders)
        - y-axis: Customer lifetime value
        - Bubble size: Number of customers in segment
        - Color by satisfaction score
- **Bottom Row**: 3 cards 
   - Average delivery time with trend indicator
   - Review Score:
   	- Large number with stars (★★★★☆)
   	- Subtitle: "Average Review Score"
   - Geographic reach:
        - Number of states served
        - Top performing state with revenue

## Key Requirements
- Use Plotly for all charts
- Filter updates all charts correctly
- Professional styling with trend arrows/colors
- Do not use icons
- Use uniform card heights for each row
- Show two decimal places for each trend indicator
- Include requirements.txt and README.md

## Additional Chart Specifications

### Enhanced Features from Notebook Analysis:
1. **Customer Segmentation Analysis:**
   - High-value, Medium-value, Low-value customer segments
   - Show spending patterns and retention opportunities
   - Display customer lifetime value distribution

2. **Operational Performance Indicators:**
   - Order fulfillment rate (96.9%)
   - Delivery success rate (93.9%) 
   - Cancellation rate (1.4%)

3. **Market Opportunity Insights:**
   - Category growth potential analysis
   - Geographic expansion opportunities
   - Seasonal revenue patterns with peak/low identification

4. **Advanced Filtering Options:**
   - Date range picker (default: current year)
   - State selector for geographic filtering
   - Product category multiselect
   - Customer segment filter

5. **Interactive Features:**
   - Hover tooltips with detailed metrics
   - Click-through functionality from charts to drill down
   - Export functionality for charts and data

6. **Color Coding Standards:**
   - Revenue/Growth: Blues (#1f77b4)
   - Positive trends: Green (#2ca02c)
   - Negative trends: Red (#d62728)
   - Warning/Attention: Orange (#ff7f0e)
   - Neutral: Gray (#6c757d)

7. **Performance Metrics to Display:**
   - Year-over-year growth rates
   - Monthly trend indicators
   - Customer acquisition cost trends
   - Average order value changes
   - Geographic market penetration rates
