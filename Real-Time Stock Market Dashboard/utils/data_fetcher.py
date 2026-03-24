# utils/data_fetcher.py
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
from config.settings import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY

class StockDataFetcher:
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    def get_realtime_data(self, symbol, interval='1m', period='1d'):
        """
        Fetch real-time stock data using yfinance
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Fetch data based on interval
            if interval == '1m':
                data = ticker.history(period='1d', interval='1m')
            elif interval == '5m':
                data = ticker.history(period='5d', interval='5m')
            else:
                data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
                
            # Reset index to have datetime as column
            data = data.reset_index()
            
            # Add symbol column
            data['Symbol'] = symbol
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols, interval='1m'):
        """
        Fetch data for multiple stocks
        """
        all_data = []
        for symbol in symbols:
            data = self.get_realtime_data(symbol, interval)
            if data is not None:
                all_data.append(data)
            time.sleep(1)  # Rate limiting
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return None
    
    def get_company_info(self, symbol):
        """
        Get company information and fundamentals
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract relevant information
            company_info = {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'week_52_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                'week_52_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'volume': info.get('volume', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A')
            }
            
            return company_info
            
        except Exception as e:
            print(f"Error fetching company info for {symbol}: {e}")
            return None
    
    def get_market_news(self, symbol=None):
        """
        Fetch latest news for a stock or general market news
        """
        try:
            if symbol:
                ticker = yf.Ticker(symbol)
                news = ticker.news
            else:
                # For general market news, you might want to use a news API
                # Using yfinance for top stories
                ticker = yf.Ticker('^GSPC')  # S&P 500 as proxy
                news = ticker.news
            
            return news[:10]  # Return top 10 news items
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def get_historical_data(self, symbol, period='1mo', interval='1d'):
        """
        Fetch historical data for longer-term analysis
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            data = data.reset_index()
            data['Symbol'] = symbol
            return data
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None