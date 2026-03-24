# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import numpy as np

from utils.data_fetcher import StockDataFetcher
from utils.indicators import TechnicalIndicators, FinancialMetrics
from config.settings import DEFAULT_SYMBOLS, REFRESH_RATE

# Page configuration
st.set_page_config(
    page_title="Real-Time Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .news-item {
        background-color: white;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
        border-left: 3px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = StockDataFetcher()
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'selected_symbols' not in st.session_state:
    st.session_state.selected_symbols = DEFAULT_SYMBOLS[:3]

def create_candlestick_chart(data, symbol, indicators=None):
    """Create candlestick chart with optimized layout and spacing"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,            # Reduced gap between subplots
        row_heights=[0.7, 0.15, 0.15],    # 70% for Price, 15% for Vol, 15% for RSI
        subplot_titles=(f'{symbol} - Price', 'Volume', 'RSI')
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data['Datetime'], open=data['Open'],
            high=data['High'], low=data['Low'],
            close=data['Close'], name='Price'
        ),
        row=1, col=1
    )
    
    # Add indicators if provided
    if indicators:
        if 'SMA_20' in indicators:
            fig.add_trace(go.Scatter(x=data['Datetime'], y=indicators['SMA_20'],
                          name='SMA 20', line=dict(color='orange', width=1.5)), row=1, col=1)
        if 'SMA_50' in indicators:
            fig.add_trace(go.Scatter(x=data['Datetime'], y=indicators['SMA_50'],
                          name='SMA 50', line=dict(color='blue', width=1.5)), row=1, col=1)
        if 'BB_Upper' in indicators:
            fig.add_trace(go.Scatter(x=data['Datetime'], y=indicators['BB_Upper'],
                          name='BB Upper', line=dict(color='rgba(173, 216, 230, 0.4)', dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=data['Datetime'], y=indicators['BB_Lower'],
                          name='BB Lower', line=dict(color='rgba(173, 216, 230, 0.4)', dash='dash'),
                          fill='tonexty', fillcolor='rgba(173, 216, 230, 0.1)'), row=1, col=1)
    
    # Volume bars (using actual colors)
    colors = ['#ef5350' if close < open else '#26a69a' for close, open in zip(data['Close'], data['Open'])]
    fig.add_trace(go.Bar(x=data['Datetime'], y=data['Volume'], name='Volume',
                         marker_color=colors, showlegend=False), row=2, col=1)
    
    # RSI
    if indicators and 'RSI' in indicators:
        fig.add_trace(go.Scatter(x=data['Datetime'], y=indicators['RSI'],
                      name='RSI', line=dict(color='#9c27b0')), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=1, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=1, row=3, col=1)
    
    # Update layout for maximum vertical space
    fig.update_layout(
        template='plotly_dark',
        height=900,                       # Increased height further
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=10, r=10, t=50, b=10) # Minimal side margins
    )
    
    fig.update_xaxes(rangeslider_visible=False) # Removes the bulky slider
    return fig
def display_company_info(info):
    """Display company information in a formatted way"""
    if info:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Company Name", info['name'][:20] + "..." if len(info['name']) > 20 else info['name'])
            st.metric("Sector", info['sector'])
        
        with col2:
            st.metric("Market Cap", f"${info['market_cap']:,.0f}" if isinstance(info['market_cap'], (int, float)) else "N/A")
            st.metric("P/E Ratio", f"{info['pe_ratio']:.2f}" if isinstance(info['pe_ratio'], (int, float)) else "N/A")
        
        with col3:
            st.metric("52-Week High", f"${info['week_52_high']:.2f}" if isinstance(info['week_52_high'], (int, float)) else "N/A")
            st.metric("52-Week Low", f"${info['week_52_low']:.2f}" if isinstance(info['week_52_low'], (int, float)) else "N/A")
        
        with col4:
            st.metric("Volume", f"{info['volume']:,.0f}" if isinstance(info['volume'], (int, float)) else "N/A")
            st.metric("Avg Volume", f"{info['avg_volume']:,.0f}" if isinstance(info['avg_volume'], (int, float)) else "N/A")
    else:
        st.warning("Company information not available")

def main():
    # Header
    st.markdown("<h1 class='main-header'>📈 Real-Time Stock Market Dashboard</h1>", 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Stock selection
        st.subheader("Select Stocks")
        all_symbols = st.text_area(
            "Enter stock symbols (comma-separated)",
            value=', '.join(DEFAULT_SYMBOLS)
        )
        selected_symbols = [s.strip().upper() for s in all_symbols.split(',') if s.strip()]
        
        # Time interval selection
        st.subheader("Chart Settings")
        interval = st.selectbox(
            "Time Interval",
            ['1m', '5m', '15m', '30m', '1h', '1d'],
            index=0
        )
        
        # Technical indicators
        st.subheader("Technical Indicators")
        show_sma = st.checkbox("Show SMA", value=True)
        show_ema = st.checkbox("Show EMA", value=False)
        show_bb = st.checkbox("Show Bollinger Bands", value=True)
        show_rsi = st.checkbox("Show RSI", value=True)
        
        # Auto-refresh
        st.subheader("Auto-Refresh")
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        refresh_rate = st.slider("Refresh Rate (seconds)", 10, 300, REFRESH_RATE)
        
        # Update button
        if st.button("🔄 Update Data", type="primary"):
            st.session_state.last_update = datetime.now()
            st.rerun()
        
        st.info(f"Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # Main content
    if selected_symbols:
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Real-Time Charts", 
            "📈 Technical Analysis", 
            "ℹ️ Company Info",
            "📰 News & Insights"
        ])
        
        with tab1:
            # Fetch real-time data
            with st.spinner("Fetching market data..."):
                data = st.session_state.data_fetcher.get_multiple_stocks(
                    selected_symbols, interval
                )
            
            if data is not None:
                # Current prices and metrics
                st.subheader("📊 Current Market Snapshot")
                latest_prices = data.groupby('Symbol').last().reset_index()
                
                cols = st.columns(len(selected_symbols))
                for i, symbol in enumerate(selected_symbols):
                    with cols[i]:
                        symbol_data = latest_prices[latest_prices['Symbol'] == symbol]
                        if not symbol_data.empty:
                            price = symbol_data['Close'].values[0]
                            change = symbol_data['Close'].values[0] - symbol_data['Open'].values[0]
                            change_pct = (change / symbol_data['Open'].values[0]) * 100
                            
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>{symbol}</h3>
                                <h2>${price:.2f}</h2>
                                <p style='color: {"green" if change >= 0 else "red"}'>
                                    {change:+.2f} ({change_pct:+.2f}%)
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Individual stock charts
                for symbol in selected_symbols:
                    symbol_data = data[data['Symbol'] == symbol].copy()
                    if not symbol_data.empty:
                        # Calculate indicators
                        indicators = {}
                        if show_sma:
                            indicators['SMA_20'] = TechnicalIndicators.calculate_sma(symbol_data, 20)
                            indicators['SMA_50'] = TechnicalIndicators.calculate_sma(symbol_data, 50)
                        if show_ema:
                            indicators['EMA_20'] = TechnicalIndicators.calculate_ema(symbol_data, 20)
                        if show_bb:
                            upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(symbol_data)
                            indicators['BB_Upper'] = upper
                            indicators['BB_Middle'] = middle
                            indicators['BB_Lower'] = lower
                        if show_rsi:
                            indicators['RSI'] = TechnicalIndicators.calculate_rsi(symbol_data)
                        
                        # Create and display chart
                        fig = create_candlestick_chart(symbol_data, symbol, indicators)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Comparison chart
                if len(selected_symbols) > 1:
                    st.subheader("📈 Price Comparison")
                    fig = create_candlestick_chart(data, selected_symbols)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Failed to fetch data. Please check your internet connection and try again.")
        
        with tab2:
            st.subheader("🔧 Technical Analysis Tools")
            
            # Select stock for detailed analysis
            analysis_symbol = st.selectbox(
                "Select Stock for Analysis",
                selected_symbols,
                key="analysis_symbol"
            )
            
            # Fetch historical data for analysis
            with st.spinner("Calculating technical indicators..."):
                hist_data = st.session_state.data_fetcher.get_historical_data(
                    analysis_symbol, period='3mo', interval='1d'
                )
            
            if hist_data is not None:
                # Calculate all indicators
                indicators = TechnicalIndicators.calculate_all_indicators(hist_data)
                
                # Display indicator values
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("RSI (14)", f"{indicators['RSI'].iloc[-1]:.2f}")
                    st.metric("MACD", f"{indicators['MACD'].iloc[-1]:.2f}")
                
                with col2:
                    st.metric("SMA 20", f"${indicators['SMA_20'].iloc[-1]:.2f}")
                    st.metric("SMA 50", f"${indicators['SMA_50'].iloc[-1]:.2f}")
                
                with col3:
                    # Calculate additional metrics
                    daily_return = FinancialMetrics.calculate_daily_return(hist_data)
                    volatility = FinancialMetrics.calculate_volatility(hist_data)
                    sharpe = FinancialMetrics.calculate_sharpe_ratio(hist_data)
                    max_dd = FinancialMetrics.calculate_max_drawdown(hist_data)
                    
                    st.metric("Volatility (20d)", f"{volatility.iloc[-1]:.2f}%")
                    st.metric("Sharpe Ratio", f"{sharpe:.2f}")
                
                # Volume Profile
                st.subheader("Volume Profile")
                volume_profile = TechnicalIndicators.calculate_volume_profile(hist_data)
                fig = px.bar(volume_profile, x='volume', y='price_level',
                           orientation='h', title='Volume Profile (Last 3 Months)')
                st.plotly_chart(fig, use_container_width=True)
                
                # Display raw data
                with st.expander("View Raw Data"):
                    st.dataframe(hist_data.tail(20))
        
        with tab3:
            st.subheader(" Company Information")
            
            for symbol in selected_symbols:
                with st.expander(f"{symbol} - Company Details"):
                    info = st.session_state.data_fetcher.get_company_info(symbol)
                    if info:
                        display_company_info(info)
        
        with tab4:
            st.subheader("Latest Market News")
            
            for symbol in selected_symbols:
                with st.expander(f"{symbol} - Latest News"):
                    news = st.session_state.data_fetcher.get_market_news(symbol)
                    if news:
                        for item in news:
                            st.markdown(f"""
                            <div class='news-item'>
                                <h4>{item.get('title','unitled')}</h4>
                                <p><small>{item.get('publisher', 'Unknown')} - 
                                {datetime.fromtimestamp(item.get('providerPublishTime', time.time())).strftime('%Y-%m-%d %H:%M')}</small></p>
                                <a href="{item.get('link', '#')}" target="_blank">Read more</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(f"No recent news for {symbol}")
        
        # Auto-refresh logic
        if auto_refresh:
            time_since_update = (datetime.now() - st.session_state.last_update).seconds
            if time_since_update >= refresh_rate:
                st.session_state.last_update = datetime.now()
                st.rerun()
    
    else:
        st.warning("Please enter at least one stock symbol in the sidebar.")

if __name__ == "__main__":
    main()