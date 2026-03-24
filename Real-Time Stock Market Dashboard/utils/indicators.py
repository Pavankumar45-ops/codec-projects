# utils/indicators.py
import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_sma(data, window=20):
        """Simple Moving Average"""
        return data['Close'].rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(data, window=20):
        """Exponential Moving Average"""
        return data['Close'].ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data, window=14):
        """Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """MACD (Moving Average Convergence Divergence)"""
        exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data, window=20, num_std=2):
        """Bollinger Bands"""
        sma = data['Close'].rolling(window=window).mean()
        std = data['Close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_volume_profile(data, bins=10):
        """Volume Profile / Market Profile"""
        price_range = np.linspace(data['Low'].min(), data['High'].max(), bins)
        volume_profile = []
        
        for i in range(len(price_range)-1):
            mask = (data['Close'] >= price_range[i]) & (data['Close'] < price_range[i+1])
            volume = data.loc[mask, 'Volume'].sum()
            volume_profile.append({
                'price_level': (price_range[i] + price_range[i+1]) / 2,
                'volume': volume
            })
        
        return pd.DataFrame(volume_profile)
    
    @staticmethod
    def calculate_all_indicators(data):
        """Calculate all technical indicators"""
        indicators = {}
        
        # Moving Averages
        indicators['SMA_20'] = TechnicalIndicators.calculate_sma(data, 20)
        indicators['SMA_50'] = TechnicalIndicators.calculate_sma(data, 50)
        indicators['EMA_20'] = TechnicalIndicators.calculate_ema(data, 20)
        
        # RSI
        indicators['RSI'] = TechnicalIndicators.calculate_rsi(data)
        
        # MACD
        macd, signal, hist = TechnicalIndicators.calculate_macd(data)
        indicators['MACD'] = macd
        indicators['MACD_Signal'] = signal
        indicators['MACD_Histogram'] = hist
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(data)
        indicators['BB_Upper'] = upper
        indicators['BB_Middle'] = middle
        indicators['BB_Lower'] = lower
        
        return indicators

class FinancialMetrics:
    @staticmethod
    def calculate_daily_return(data):
        """Calculate daily returns"""
        return data['Close'].pct_change() * 100
    
    @staticmethod
    def calculate_volatility(data, window=20):
        """Calculate rolling volatility"""
        returns = FinancialMetrics.calculate_daily_return(data)
        return returns.rolling(window=window).std()
    
    @staticmethod
    def calculate_sharpe_ratio(data, risk_free_rate=0.02):
        """Calculate Sharpe Ratio"""
        returns = FinancialMetrics.calculate_daily_return(data) / 100
        excess_returns = returns - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std()
        return sharpe_ratio
    
    @staticmethod
    def calculate_max_drawdown(data):
        """Calculate Maximum Drawdown"""
        cumulative_returns = (1 + FinancialMetrics.calculate_daily_return(data)/100).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max * 100
        return drawdown.min()