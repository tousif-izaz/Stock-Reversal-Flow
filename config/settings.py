import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', 'your_api_key_here')
POLYGON_BASE_URL = 'https://api.polygon.io'

# Database Configuration
DATABASE_PATH = 'data/stocks.db'

# Stock Watchlist (S&P 500 subset for MVP)
WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'JPM', 'JNJ', 'V',
    'PG', 'UNH', 'HD', 'MA', 'BAC',
    'DIS', 'ADBE', 'CRM', 'NFLX', 'PYPL'
]

# Technical Analysis Parameters
RSI_PERIOD = 14
SMA_PERIOD = 20
OVERSOLD_THRESHOLD = 30
OVERBOUGHT_THRESHOLD = 70

# Reversal Detection Parameters
MIN_DECLINE_PERCENT = 10  # Minimum % decline to consider "overextended"
DECLINE_LOOKBACK_DAYS = 10  # Days to look back for decline calculation

# Data Collection Settings
UPDATE_INTERVAL_MINUTES = 60  # How often to fetch new data
MARKET_HOURS_START = 9.5  # 9:30 AM
MARKET_HOURS_END = 16  # 4:00 PM