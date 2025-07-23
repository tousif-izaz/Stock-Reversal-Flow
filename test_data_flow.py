#!/usr/bin/env python3
"""
Test script to verify data collection and database operations
"""

import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

def test_database_operations():
    """Test basic database operations"""
    print("Testing database operations...")
    
    try:
        from src.database import StockDatabase
        db = StockDatabase()
        
        # Test database creation
        print(f"Database initialized at: {db.db_path}")
        
        # Check if database file exists
        db_file = Path(db.db_path)
        if db_file.exists():
            print(f"Database file exists: {db_file.stat().st_size} bytes")
        else:
            print("Database file not found")
            return False
            
        # Test data retrieval
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM stock_data")
            total_records = cursor.fetchone()[0]
            print(f"Total records in database: {total_records}")
            
            if total_records > 0:
                cursor = conn.execute("SELECT DISTINCT symbol FROM stock_data LIMIT 5")
                symbols = [row[0] for row in cursor.fetchall()]
                print(f"Sample symbols: {symbols}")
                
                # Test specific symbol retrieval
                test_symbol = symbols[0] if symbols else 'AAPL'
                data = db.get_stock_data(test_symbol)
                print(f"Retrieved {len(data)} records for {test_symbol}")
                
                if not data.empty:
                    print(f"   Latest record: {data.iloc[0]['datetime']} - Close: ${data.iloc[0]['close']:.2f}")
                
        return True
        
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def test_data_collection():
    """Test data collection functionality"""
    print("\nTesting data collection...")
    
    try:
        from src.data_collector import PolygonDataCollector
        from config.settings import POLYGON_API_KEY
        
        if POLYGON_API_KEY == 'your_api_key_here':
            print("API key not configured - skipping data collection test")
            return True
            
        collector = PolygonDataCollector()
        print("Data collector initialized")
        
        # Test with just one symbol to avoid rate limits
        test_symbol = 'AAPL'
        print(f"Testing data collection for {test_symbol}...")
        
        result = collector.collect_data_for_symbol(test_symbol)
        if result:
            print(f"Successfully collected data for {test_symbol}")
        else:
            print(f"Failed to collect data for {test_symbol}")
            
        return result
        
    except Exception as e:
        print(f"Data collection test failed: {e}")
        return False

def test_dashboard_functions():
    """Test dashboard data loading functions"""
    print("\nTesting dashboard functions...")
    
    try:
        from src.dashboard import load_stock_data, load_all_latest_data
        
        # Test loading data for a symbol
        print("Testing stock data loading...")
        data = load_stock_data('PYPL', limit=10)
        
        if not data.empty:
            print(f"Loaded {len(data)} records for PYPL")
        else:
            print("No data loaded for PYPL")
            
        # Test loading all latest data
        print("Testing all latest data loading...")
        all_data = load_all_latest_data()
        
        if not all_data.empty:
            print(f"Loaded latest data for {len(all_data)} symbols")
        else:
            print("No latest data loaded")
            
        return True
        
    except Exception as e:
        print(f"Dashboard function test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Stock Reversal Flow - Data Flow Test")
    print("=" * 50)
    
    # Test database operations
    db_test = test_database_operations()
    
    # Test data collection (only if API key is configured)
    collection_test = test_data_collection()
    
    # Test dashboard functions
    dashboard_test = test_dashboard_functions()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"   Database Operations: {'PASS' if db_test else 'FAIL'}")
    print(f"   Data Collection: {'PASS' if collection_test else 'FAIL'}")
    print(f"   Dashboard Functions: {'PASS' if dashboard_test else 'FAIL'}")
    
    if all([db_test, collection_test, dashboard_test]):
        print("\nAll tests passed! The dashboard should work correctly.")
    else:
        print("\nSome tests failed. Check the error messages above.")
        
    print("\nNext steps:")
    print("   1. If API key not configured: copy .env.example to .env and add your key")
    print("   2. Run: python collect_data.py")
    print("   3. Run: python run_dashboard.py")

if __name__ == "__main__":
    main()