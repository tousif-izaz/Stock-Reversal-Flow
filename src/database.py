import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Optional
from config.settings import DATABASE_PATH

class StockDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._ensure_database_exists()
        self._create_tables()
    
    def _ensure_database_exists(self):
        """Create database directory if it doesn't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    symbol TEXT NOT NULL,
                    datetime TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    rsi REAL,
                    sma_20 REAL,
                    pct_change_5d REAL,
                    pct_change_10d REAL,
                    is_oversold BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, datetime, timeframe)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data_updates (
                    symbol TEXT PRIMARY KEY,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def insert_stock_data(self, df: pd.DataFrame):
        """Insert stock data DataFrame into database"""
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql('stock_data', conn, if_exists='replace', index=False)
    
    def get_stock_data(self, symbol: str, timeframe: str = 'daily', limit: Optional[int] = None) -> pd.DataFrame:
        """Retrieve stock data for a specific symbol"""
        query = '''
            SELECT * FROM stock_data 
            WHERE symbol = ? AND timeframe = ?
            ORDER BY datetime DESC
        '''
        if limit:
            query += f' LIMIT {limit}'
            
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=(symbol, timeframe))
    
    def get_all_latest_data(self, timeframe: str = 'daily') -> pd.DataFrame:
        """Get latest data for all symbols"""
        query = '''
            SELECT * FROM stock_data s1
            WHERE s1.timeframe = ? AND s1.datetime = (
                SELECT MAX(s2.datetime) 
                FROM stock_data s2 
                WHERE s2.symbol = s1.symbol AND s2.timeframe = s1.timeframe
            )
            ORDER BY s1.symbol
        '''
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=(timeframe,))
    
    def get_oversold_stocks(self, timeframe: str = 'daily') -> pd.DataFrame:
        """Get stocks that are currently oversold"""
        query = '''
            SELECT * FROM stock_data s1
            WHERE s1.timeframe = ? AND s1.is_oversold = 1 
            AND s1.datetime = (
                SELECT MAX(s2.datetime) 
                FROM stock_data s2 
                WHERE s2.symbol = s1.symbol AND s2.timeframe = s1.timeframe
            )
            ORDER BY s1.rsi ASC
        '''
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=(timeframe,))
    
    def update_last_fetch_time(self, symbol: str):
        """Update the last fetch time for a symbol"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO data_updates (symbol, last_update)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (symbol,))
            conn.commit()
    
    def get_symbols_needing_update(self, hours_threshold: int = 1) -> List[str]:
        """Get symbols that haven't been updated in the specified hours"""
        query = '''
            SELECT w.symbol 
            FROM (SELECT ? as symbol) w
            LEFT JOIN data_updates d ON w.symbol = d.symbol
            WHERE d.last_update IS NULL 
            OR datetime(d.last_update) < datetime('now', '-{} hours')
        '''.format(hours_threshold)
        
        with sqlite3.connect(self.db_path) as conn:
            from config.settings import WATCHLIST
            symbols = []
            for symbol in WATCHLIST:
                result = conn.execute(query, (symbol,)).fetchone()
                if result:
                    symbols.append(symbol)
            return symbols