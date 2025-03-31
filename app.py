import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from io import StringIO

# Set page configuration
st.set_page_config(
    page_title="Stock Data Visualizer",
    page_icon="📈",
    layout="wide"
)

# App title and description
st.title("📈 Stock Data Visualizer")
st.markdown("This app allows you to visualize stock data from Yahoo Finance and download key financial information.")

# Input section
with st.container():
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Stock symbol input with default value
        stock_symbol = st.text_input("Enter stock symbol", "AAPL").upper()
    
    with col2:
        # Time period selection
        period_options = {
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "Year to Date": "ytd",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y",
            "Max": "max"
        }
        selected_period = st.selectbox("Select time period", list(period_options.keys()))
        period = period_options[selected_period]
    
    with col3:
        # Interval selection
        interval_options = {
            "1 Day": "1d",
            "1 Week": "1wk",
            "1 Month": "1mo"
        }
        selected_interval = st.selectbox("Select interval", list(interval_options.keys()))
        interval = interval_options[selected_interval]

# Function to download data as CSV
def get_csv_download_link(df, filename):
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV File</a>'
    return href

# Fetch data and display
try:
    # Show loading message
    with st.spinner(f"Fetching data for {stock_symbol}..."):
        # Get ticker info
        ticker = yf.Ticker(stock_symbol)
        
        # Check if ticker exists
        try:
            info = ticker.info
            if not info or 'regularMarketPrice' not in info:
                st.error(f"Could not find data for symbol: {stock_symbol}. Please check the symbol and try again.")
                st.stop()
        except Exception as e:
            st.error(f"Error: {stock_symbol} is not a valid stock symbol. Please check and try again.")
            st.stop()
        
        # Get historical data
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            st.error(f"No historical data available for {stock_symbol} with the selected time period and interval.")
            st.stop()
            
        # Current stock information
        current_price = info.get('regularMarketPrice', 'N/A')
        previous_close = info.get('regularMarketPreviousClose', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap = f"${market_cap:,}"
        
        company_name = info.get('longName', stock_symbol)
        
        # Calculate price change and percentage
        if current_price != 'N/A' and previous_close != 'N/A':
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close) * 100
            change_color = "green" if price_change >= 0 else "red"
            change_icon = "▲" if price_change >= 0 else "▼"
        else:
            price_change = 'N/A'
            price_change_percent = 'N/A'
            change_color = "gray"
            change_icon = ""
    
    # Display company information in a header
    st.header(f"{company_name} ({stock_symbol})")
    
    # Display current stock information in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Price", f"${current_price:,.2f}" if current_price != 'N/A' else 'N/A')
    
    with col2:
        if price_change != 'N/A':
            st.metric("Change", f"${price_change:,.2f}", f"{price_change_percent:.2f}%")
        else:
            st.metric("Change", "N/A", "N/A")
    
    with col3:
        st.metric("Previous Close", f"${previous_close:,.2f}" if previous_close != 'N/A' else 'N/A')
    
    with col4:
        st.metric("Market Cap", market_cap)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Price Chart", "Financial Data", "Company Info"])
    
    with tab1:
        st.subheader("Stock Price History")
        
        # Create Plotly figure for stock price
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x = hist_data.index,
            open = hist_data['Open'],
            high = hist_data['High'],
            low = hist_data['Low'],
            close = hist_data['Close'],
            name = 'Price'
        ))
        
        # Add volume as a bar chart at the bottom with low opacity
        fig.add_trace(go.Bar(
            x = hist_data.index,
            y = hist_data['Volume'],
            name = 'Volume',
            marker_color = 'rgba(0, 0, 255, 0.3)',
            opacity = 0.4,
            yaxis = 'y2'
        ))
        
        # Customize layout
        fig.update_layout(
            title = f"{company_name} Stock Price and Volume",
            xaxis_title = "Date",
            yaxis_title = "Price ($)",
            yaxis2 = dict(
                title ="Volume",
                overlaying = "y",
                side = "right",
                showgrid = False
            ),
            xaxis_rangeslider_visible = False,
            height = 600,
            legend = dict(
                orientation = "h",
                yanchor = "bottom",
                y = 1.02,
                xanchor = "right",
                x = 1
            )
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width = True)
        
        # Add moving averages to a separate chart
        st.subheader("Moving Averages")
        
        # Calculate moving averages
        ma_periods = [20, 50, 200]
        for period in ma_periods:
            if len(hist_data) >= period:
                hist_data[f'MA{period}'] = hist_data['Close'].rolling(window=period).mean()
        
        # Plot moving averages
        ma_fig = go.Figure()
        
        # Add closing price
        ma_fig.add_trace(go.Scatter(
            x = hist_data.index,
            y = hist_data['Close'],
            mode = 'lines',
            name = 'Close Price',
            line = dict(color = 'orange', width = 2.5)
        ))
        
        # Add moving averages
        colors = ['blue', 'green', 'red']
        for i, period in enumerate(ma_periods):
            if f'MA{period}' in hist_data.columns:
                ma_fig.add_trace(go.Scatter(
                    x = hist_data.index,
                    y = hist_data[f'MA{period}'],
                    mode = 'lines',
                    name = f'{period}-day MA',
                    line = dict(color=colors[i % len(colors)], width=1.5)
                ))
        
        ma_fig.update_layout(
            title="Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(ma_fig, use_container_width=True)
        
    with tab2:
        st.subheader("Key Financial Data")
        
        # Create datasets for financial tables
        valuation_metrics = pd.DataFrame({
            'Metric': [
                'Market Cap', 'Enterprise Value', 'Trailing P/E', 'Forward P/E',
                'PEG Ratio', 'Price/Sales', 'Price/Book', 'Enterprise Value/Revenue',
                'Enterprise Value/EBITDA'
            ],
            'Value': [
                info.get('marketCap', 'N/A'),
                info.get('enterpriseValue', 'N/A'),
                info.get('trailingPE', 'N/A'),
                info.get('forwardPE', 'N/A'),
                info.get('pegRatio', 'N/A'),
                info.get('priceToSalesTrailing12Months', 'N/A'),
                info.get('priceToBook', 'N/A'),
                info.get('enterpriseToRevenue', 'N/A'),
                info.get('enterpriseToEbitda', 'N/A')
            ]
        })
        
        financial_metrics = pd.DataFrame({
            'Metric': [
                'Revenue (TTM)', 'Revenue Growth', 'Gross Profit', 'EBITDA',
                'Net Income', 'Profit Margin', 'Operating Margin', 'Return on Assets',
                'Return on Equity', 'Free Cash Flow'
            ],
            'Value': [
                info.get('totalRevenue', 'N/A'),
                info.get('revenueGrowth', 'N/A'),
                info.get('grossProfit', 'N/A'),
                info.get('ebitda', 'N/A'),
                info.get('netIncomeToCommon', 'N/A'),
                info.get('profitMargins', 'N/A'),
                info.get('operatingMargins', 'N/A'),
                info.get('returnOnAssets', 'N/A'),
                info.get('returnOnEquity', 'N/A'),
                info.get('freeCashflow', 'N/A')
            ]
        })
        
        # Format numbers in the dataframes
        for df in [valuation_metrics, financial_metrics]:
            for i, val in enumerate(df['Value']):
                if isinstance(val, (int, float)) and val != 'N/A':
                    if 'Margin' in df['Metric'][i] or 'Growth' in df['Metric'][i] or 'Return' in df['Metric'][i] or 'Ratio' in df['Metric'][i]:
                        df.loc[i, 'Value'] = f"{val:.2%}" if val != 'N/A' else 'N/A'
                    elif 'Market Cap' in df['Metric'][i] or 'Enterprise Value' in df['Metric'][i] or 'Revenue' in df['Metric'][i] or 'Profit' in df['Metric'][i] or 'EBITDA' in df['Metric'][i] or 'Income' in df['Metric'][i] or 'Cash Flow' in df['Metric'][i]:
                        if val >= 1e9:
                            df.loc[i, 'Value'] = f"${val/1e9:.2f}B"
                        elif val >= 1e6:
                            df.loc[i, 'Value'] = f"${val/1e6:.2f}M"
                        else:
                            df.loc[i, 'Value'] = f"${val:,.2f}"
                    else:
                        df.loc[i, 'Value'] = f"{val:.2f}" if val != 'N/A' else 'N/A'
        
        # Display tables side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Valuation Metrics")
            st.dataframe(valuation_metrics, use_container_width = True)
            st.markdown(get_csv_download_link(valuation_metrics, f"{stock_symbol}_valuation_metrics"), unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Financial Metrics")
            st.dataframe(financial_metrics, use_container_width = True)
            st.markdown(get_csv_download_link(financial_metrics, f"{stock_symbol}_financial_metrics"), unsafe_allow_html=True)
        
        # Historical data table
        st.markdown("#### Historical Stock Data")
        # Create a copy of historical data with formatted columns
        hist_display = hist_data.copy()
        
        # Round values for better display
        for col in ['Open', 'High', 'Low', 'Close']:
            hist_display[col] = hist_display[col].round(2)
        
        # Format volume
        hist_display['Volume'] = hist_display['Volume'].apply(lambda x: f"{x:,}")
        
        # Display the table
        st.dataframe(hist_display, use_container_width = True)
        st.markdown(get_csv_download_link(hist_data, f"{stock_symbol}_historical_data"), unsafe_allow_html = True)
    
    with tab3:
        st.subheader("Company Information")
        
        # Create columns for company details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Business Summary")
            business_summary = info.get('longBusinessSummary', 'No business summary available.')
            st.write(business_summary)
            
            st.markdown("#### Industry Information")
            industry_info = {
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Full Time Employees': info.get('fullTimeEmployees', 'N/A'),
                'Country': info.get('country', 'N/A'),
                'Website': info.get('website', 'N/A')
            }
            
            for key, value in industry_info.items():
                if key == 'Website' and value != 'N/A':
                    st.markdown(f"**{key}:** [{value}]({value})")
                else:
                    st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("#### Key Executive Officers")
            
            # Try to get company officers
            try:
                company_officers = ticker.get_company_officers()
                if company_officers and len(company_officers) > 0:
                    for officer in company_officers[:5]:  # Limit to top 5 officers
                        st.markdown(f"**{officer.get('name', 'N/A')}**")
                        st.markdown(f"Title: {officer.get('title', 'N/A')}")
                        st.markdown(f"Age: {officer.get('age', 'N/A')}")
                        st.markdown("---")
                else:
                    st.write("No officer information available.")
            except:
                st.write("Officer information could not be retrieved.")
            
            st.markdown("#### Additional Information")
            additional_info = {
                'Market': info.get('market', 'N/A').upper(),
                'Exchange': info.get('exchange', 'N/A'),
                'Currency': info.get('currency', 'N/A'),
                'Quote Type': info.get('quoteType', 'N/A')
            }
            
            for key, value in additional_info.items():
                st.markdown(f"**{key}:** {value}")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.write("Please check the stock symbol and try again.")

# Add footer
st.markdown("---")
st.markdown("Data provided by Yahoo Finance. This app is for informational purposes only and does not constitute financial advice.")
st.markdown("""Made By Neptunes_Bounty in his spare time. Please take the time to leave some feedback.

Connect with me on:
[![GitHub](https://img.shields.io/badge/GitHub-%2312100E.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Neptunes-Bounty/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/keerthi-raagav-76b19b359/)
[![LeetCode](https://img.shields.io/badge/LeetCode-%23FFA116.svg?style=for-the-badge&logo=leetcode&logoColor=white)](https://leetcode.com/u/Neptunes_Bounty/)
""", unsafe_allow_html = True)

