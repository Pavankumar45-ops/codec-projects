# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (you can get free API keys from these services)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', 'demo')

# Default settings
DEFAULT_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
DEFAULT_INTERVAL = '1m'
REFRESH_RATE = 60  # seconds

# Technical indicators settings
INDICATORS = ['SMA', 'EMA', 'RSI', 'MACD', 'Bollinger Bands']