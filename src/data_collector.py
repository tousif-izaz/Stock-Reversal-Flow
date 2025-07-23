import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import ta
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from config.settings import (
    POLYGON_API_KEY, POLYGON_BASE_URL, WATCHLIST,
    RSI_PERIOD, SMA_PERIOD, OVERSOLD_THRESHOLD,
    MIN_DECLINE_PERCENT, DECLINE_LOOKBACK_DAYS
)
from src.database import StockDatabase

class PolygonDataCollector:
    def __init__(self):
        self.api_key = POLYGON_API_KEY
        self.base_url = POLYGON_BASE_URL
        self.db = StockDatabase()
        self.rate_limit_delay = 12  # 5 calls per minute = 12 seconds between calls
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with error handling and rate limiting"""
        params['apikey'] = self.api_key
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params)
            time.sleep(self.rate_limit_delay)  # Rate limiting
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error for {endpoint}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Request failed for {endpoint}: {str(e)}")
            return None
    
    def fetch_daily_data(self, symbol: str, days: int = 100) -> Optional[pd.DataFrame]:
        """Fetch daily OHLCV data for a symbol"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        endpoint = f"/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        params = {'adjusted': 'true', 'sort': 'asc'}
        
        data = self._make_request(endpoint, params)
        if not data or 'results' not in data:
            return None
        
        df = pd.DataFrame(data['results'])
        if df.empty:
            return None
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['t'], unit='ms')
        df['symbol'] = symbol
        df['timeframe'] = 'daily'
        
        # Rename columns to match our schema
        df = df.rename(columns={
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume'
        })
        
        # Select and order columns
        df = df[['symbol', 'datetime', 'timeframe', 'open', 'high', 'low', 'close', 'volume']]
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the data"""
        if df.empty or len(df) < max(RSI_PERIOD, SMA_PERIOD):
            return df
        
        # Sort by datetime to ensure proper calculation
        df = df.sort_values('datetime').copy()
        
        # Calculate RSI
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'], 
            window=RSI_PERIOD
        ).rsi()
        
        # Calculate SMA
        df['sma_20'] = ta.trend.SMAIndicator(
            close=df['close'], 
            window=SMA_PERIOD
        ).sma_indicator()
        
        # Calculate percentage changes
        df['pct_change_5d'] = df['close'].pct_change(periods=5) * 100
        df['pct_change_10d'] = df['close'].pct_change(periods=DECLINE_LOOKBACK_DAYS) * 100
        
        # Mark oversold conditions
        df['is_oversold'] = (
            (df['rsi'] < OVERSOLD_THRESHOLD) & 
            (df['pct_change_10d'] < -MIN_DECLINE_PERCENT)
        ).astype(int)
        
        return df
    
    def collect_data_for_symbol(self, symbol: str) -> bool:
        """Collect and process data for a single symbol"""
        print(f"Collecting data for {symbol}...")
        
        # Fetch raw data
        df = self.fetch_daily_data(symbol)
        if df is None or df.empty:
            print(f"No data retrieved for {symbol}")
            return False
        
        # Calculate indicators
        df = self.calculate_indicators(df)
        
        # Store in database
        try:
            self.db.insert_stock_data(df)
            self.db.update_last_fetch_time(symbol)
            print(f"Successfully stored {len(df)} records for {symbol}")
            return True
        except Exception as e:
            print(f"Error storing data for {symbol}: {str(e)}")
            return False
    
    def collect_all_data(self, symbols: Optional[List[str]] = None) -> Dict[str, bool]:
        """Collect data for all symbols in watchlist"""
        if symbols is None:
            symbols = WATCHLIST
        
        results = {}
        for symbol in symbols:
            results[symbol] = self.collect_data_for_symbol(symbol)
            
        return results
    
    def update_stale_data(self, hours_threshold: int = 1) -> Dict[str, bool]:
        """Update data for symbols that haven't been updated recently"""
        symbols_needing_update = self.db.get_symbols_needing_update(hours_threshold)
        
        if not symbols_needing_update:
            print("All data is up to date")
            return {}
        
        print(f"Updating {len(symbols_needing_update)} symbols: {symbols_needing_update}")
        return self.collect_all_data(symbols_needing_update)

def main():
    """Main function for running data collection"""
    collector = PolygonDataCollector()
    
    # Check if API key is configured
    if collector.api_key == 'your_api_key_here':
        print("Please configure your Polygon API key in the .env file")
        return
    
    # Collect data for all symbols
    results = collector.collect_all_data()
    
    # Print summary
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    print(f"\nData collection complete: {successful}/{total} symbols successful")
    
    if successful < total:
        failed_symbols = [symbol for symbol, success in results.items() if not success]
        print(f"Failed symbols: {failed_symbols}")

if __name__ == "__main__":
    main()