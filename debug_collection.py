#!/usr/bin/env python3
"""
Debug script to check data collection process
"""

import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

def debug_single_collection():
    """Test collection for a few symbols to see what's happening"""
    from src.data_collector import PolygonDataCollector
    from config.settings import WATCHLIST
    
    collector = PolygonDataCollector()
    
    # Test with first 3 symbols
    test_symbols = WATCHLIST[:3]
    print(f"Testing collection for: {test_symbols}")
    
    for symbol in test_symbols:
        print(f"\n--- Collecting {symbol} ---")
        
        # Test API call first
        df = collector.fetch_daily_data(symbol, days=50)
        if df is None or df.empty:
            print(f"❌ No data fetched from API for {symbol}")
            continue
        else:
            print(f"✅ Fetched {len(df)} records from API for {symbol}")
        
        # Test indicator calculation
        df_with_indicators = collector.calculate_indicators(df)
        if df_with_indicators.empty:
            print(f"❌ Indicator calculation failed for {symbol}")
            continue
        else:
            print(f"✅ Calculated indicators for {symbol}")
        
        # Test database insertion
        try:
            collector.db.insert_stock_data(df_with_indicators)
            collector.db.update_last_fetch_time(symbol)
            print(f"✅ Successfully stored {len(df_with_indicators)} records for {symbol}")
        except Exception as e:
            print(f"❌ Database insertion failed for {symbol}: {e}")
    
    # Check what's in database now
    print("\n--- Database Status After Collection ---")
    import sqlite3
    with sqlite3.connect(collector.db.db_path) as conn:
        cursor = conn.execute('SELECT symbol, COUNT(*) FROM stock_data GROUP BY symbol ORDER BY symbol')
        results = cursor.fetchall()
        for symbol, count in results:
            print(f"  {symbol}: {count} records")

def debug_api_calls():
    """Test individual API calls to see if there are issues"""
    from src.data_collector import PolygonDataCollector
    from config.settings import WATCHLIST
    
    collector = PolygonDataCollector()
    
    print("Testing API calls for individual symbols...")
    
    for symbol in WATCHLIST[:5]:  # Test first 5
        print(f"\nTesting API call for {symbol}...")
        
        try:
            df = collector.fetch_daily_data(symbol, days=10)  # Smaller dataset for testing
            if df is None:
                print(f"  ❌ API call returned None for {symbol}")
            elif df.empty:
                print(f"  ❌ API call returned empty DataFrame for {symbol}")
            else:
                print(f"  ✅ API call successful: {len(df)} records for {symbol}")
                print(f"     Latest record: {df.iloc[-1]['datetime']} - Close: ${df.iloc[-1]['close']:.2f}")
        except Exception as e:
            print(f"  ❌ API call failed for {symbol}: {e}")

def main():
    """Run debug tests"""
    print("Stock Data Collection Debug")
    print("=" * 40)
    
    print("1. Testing individual API calls...")
    debug_api_calls()
    
    print("\n" + "=" * 40)
    print("2. Testing full collection process...")
    debug_single_collection()

if __name__ == "__main__":
    main()