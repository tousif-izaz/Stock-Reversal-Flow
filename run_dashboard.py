#!/usr/bin/env python3
"""
Stock Reversal Flow Dashboard Launcher
Run this script to start the Streamlit dashboard
"""

import subprocess
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
        print("⚠️  Warning: .env file not found!")
        print("Please copy .env.example to .env and add your Polygon API key")
        print("You can get a free API key at: https://polygon.io/")
        print()
    
    # Launch Streamlit dashboard
    dashboard_path = src_path / "dashboard.py"
    
    print("🚀 Launching Stock Reversal Flow Dashboard...")
    print("📊 Dashboard will open in your default browser")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thanks for using Stock Reversal Flow!")
    except FileNotFoundError:
        print("❌ Error: Streamlit not found. Please install dependencies:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()