#!/usr/bin/env python3
"""
Data Collection Script for Stock Reversal Flow
Run this script to collect stock data from Polygon API
"""

import sys
import os
from pathlib import Path

def main():
    # Ensure we're in the project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add src directory to Python path
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  Error: .env file not found!")
        print("Please copy .env.example to .env and add your Polygon API key")
        print("You can get a free API key at: https://polygon.io/")
        return
    
    # Import and run data collector
    try:
        from data_collector import main as run_collector
        print("📈 Starting Stock Data Collection...")
        print("🔄 This may take a few minutes due to API rate limiting...")
        print()
        
        run_collector()
        
        print("\n✅ Data collection complete!")
        print("🚀 You can now run the dashboard: python run_dashboard.py")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error during data collection: {e}")

if __name__ == "__main__":
    main()