import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from src.database import StockDatabase
from src.data_collector import PolygonDataCollector
from config.settings import WATCHLIST, OVERSOLD_THRESHOLD, MIN_DECLINE_PERCENT

# Page configuration
st.set_page_config(
    page_title="Stock Reversal Flow Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_stock_data(symbol: str, limit: int = 100):
    """Load stock data from database with caching"""
    try:
        db = StockDatabase()
        data = db.get_stock_data(symbol, limit=limit)
        if not data.empty:
            st.write(f"Debug: Loaded {len(data)} records for {symbol}")
        else:
            st.write(f"Debug: No data found for {symbol} in database")
        return data
    except Exception as e:
        st.error(f"Error loading data for {symbol}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_oversold_stocks():
    """Load oversold stocks with caching"""
    try:
        db = StockDatabase()
        data = db.get_oversold_stocks()
        st.write(f"Debug: Found {len(data)} oversold stocks")
        return data
    except Exception as e:
        st.error(f"Error loading oversold stocks: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_all_latest_data():
    """Load latest data for all stocks"""
    try:
        db = StockDatabase()
        data = db.get_all_latest_data()
        st.write(f"Debug: Loaded latest data for {len(data)} stocks")
        return data
    except Exception as e:
        st.error(f"Error loading all latest data: {str(e)}")
        return pd.DataFrame()

def create_candlestick_chart(df: pd.DataFrame, symbol: str):
    """Create candlestick chart with indicators"""
    if df.empty:
        st.warning(f"No data available for {symbol}")
        return
    
    # Sort by datetime
    df = df.sort_values('datetime')
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=[f'{symbol} Price Chart', 'RSI'],
        row_heights=[0.7, 0.3]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol,
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )
    
    # SMA line
    if 'sma_20' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['sma_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
    
    # RSI chart
    if 'rsi' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # RSI threshold lines
        fig.add_hline(y=OVERSOLD_THRESHOLD, line_dash="dash", line_color="red", 
                     annotation_text=f"Oversold ({OVERSOLD_THRESHOLD})", row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="green", 
                     annotation_text="Overbought (70)", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Technical Analysis",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        showlegend=True,
        template="plotly_white"
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    
    return fig

def display_stock_metrics(df: pd.DataFrame):
    """Display key metrics for a stock"""
    if df.empty:
        return
    
    latest = df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Price", f"${latest['close']:.2f}")
    
    with col2:
        if pd.notna(latest.get('pct_change_5d')):
            st.metric("5-Day Change", f"{latest['pct_change_5d']:.2f}%")
    
    with col3:
        if pd.notna(latest.get('pct_change_10d')):
            st.metric("10-Day Change", f"{latest['pct_change_10d']:.2f}%")
    
    with col4:
        if pd.notna(latest.get('rsi')):
            rsi_color = "red" if latest['rsi'] < OVERSOLD_THRESHOLD else "normal"
            st.metric("RSI", f"{latest['rsi']:.1f}")

def check_database_status():
    """Check if database has any data"""
    try:
        import sqlite3
        db = StockDatabase()
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM stock_data")
            total_records = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(DISTINCT symbol) FROM stock_data") 
            unique_symbols = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT symbol, COUNT(*) as records FROM stock_data GROUP BY symbol LIMIT 10")
            sample_data = cursor.fetchall()
            
            return {
                'total_records': total_records,
                'unique_symbols': unique_symbols,
                'sample_data': sample_data,
                'db_path': db.db_path
            }
    except Exception as e:
        return {'error': str(e)}

def main():
    """Main dashboard function"""
    st.title("📈 Stock Reversal Flow Dashboard")
    st.markdown("Monitor overextended stocks and potential reversal opportunities")
    
    # Database status check
    with st.expander("🔍 Database Status (Debug)", expanded=False):
        status = check_database_status()
        if 'error' in status:
            st.error(f"Database Error: {status['error']}")
        else:
            st.write(f"**Database Path:** {status['db_path']}")
            st.write(f"**Total Records:** {status['total_records']}")
            st.write(f"**Unique Symbols:** {status['unique_symbols']}")
            if status['sample_data']:
                st.write("**Sample Data:**")
                for symbol, count in status['sample_data']:
                    st.write(f"- {symbol}: {count} records")
    
    # Sidebar
    st.sidebar.header("Controls")
    
    # Data refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        collector = PolygonDataCollector()
        with st.spinner("Updating data..."):
            results = collector.update_stale_data(hours_threshold=1)
            if results:
                st.sidebar.success(f"Updated {len(results)} symbols")
            else:
                st.sidebar.info("Data is up to date")
    
    # Stock selector
    selected_symbol = st.sidebar.selectbox(
        "Select Stock",
        options=WATCHLIST,
        index=0
    )
    
    # Filters
    st.sidebar.subheader("Filters")
    show_oversold_only = st.sidebar.checkbox("Show Oversold Stocks Only", value=False)
    min_decline = st.sidebar.slider("Min Decline %", min_value=5, max_value=30, value=MIN_DECLINE_PERCENT)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Individual Stock", "🎯 Oversold Stocks", "📈 Market Overview"])
    
    with tab1:
        st.header(f"Analysis for {selected_symbol}")
        
        # Load and display data
        df = load_stock_data(selected_symbol)
        
        if not df.empty:
            # Display metrics
            display_stock_metrics(df)
            
            # Display chart
            fig = create_candlestick_chart(df, selected_symbol)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Show latest signals
            latest = df.iloc[-1]
            if latest.get('is_oversold', 0):
                st.success("🎯 **REVERSAL OPPORTUNITY DETECTED**")
                st.write(f"RSI: {latest['rsi']:.1f} | 10-Day Decline: {latest['pct_change_10d']:.1f}%")
        else:
            st.warning(f"No data available for {selected_symbol}. Please refresh data first.")
    
    with tab2:
        st.header("🎯 Oversold Stocks")
        
        oversold_df = load_oversold_stocks()
        
        if not oversold_df.empty:
            st.write(f"Found {len(oversold_df)} oversold stocks:")
            
            # Create summary table
            display_df = oversold_df[['symbol', 'close', 'rsi', 'pct_change_5d', 'pct_change_10d']].copy()
            display_df.columns = ['Symbol', 'Price', 'RSI', '5D Change %', '10D Change %']
            
            # Format the dataframe
            display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
            display_df['RSI'] = display_df['RSI'].apply(lambda x: f"{x:.1f}")
            display_df['5D Change %'] = display_df['5D Change %'].apply(lambda x: f"{x:.1f}%")
            display_df['10D Change %'] = display_df['10D Change %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Quick charts for top oversold stocks
            if len(oversold_df) > 0:
                st.subheader("Quick Charts - Top Oversold Stocks")
                
                for i, row in oversold_df.head(3).iterrows():
                    symbol = row['symbol']
                    st.write(f"**{symbol}** - RSI: {row['rsi']:.1f}")
                    
                    symbol_df = load_stock_data(symbol, limit=50)
                    if not symbol_df.empty:
                        fig = create_candlestick_chart(symbol_df, symbol)
                        if fig:
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No oversold stocks detected at the moment.")
    
    with tab3:
        st.header("📈 Market Overview")
        
        all_data = load_all_latest_data()
        
        if not all_data.empty:
            # Market summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                oversold_count = len(all_data[all_data['is_oversold'] == 1])
                st.metric("Oversold Stocks", oversold_count)
            
            with col2:
                avg_rsi = all_data['rsi'].mean()
                st.metric("Average RSI", f"{avg_rsi:.1f}")
            
            with col3:
                declining_count = len(all_data[all_data['pct_change_10d'] < -5])
                st.metric("Declining Stocks (>5%)", declining_count)
            
            with col4:
                avg_decline = all_data['pct_change_10d'].mean()
                st.metric("Avg 10D Change", f"{avg_decline:.1f}%")
            
            # RSI distribution chart
            st.subheader("RSI Distribution")
            fig = px.histogram(all_data, x='rsi', nbins=20, title="RSI Distribution Across Watchlist")
            fig.add_vline(x=OVERSOLD_THRESHOLD, line_dash="dash", line_color="red", 
                         annotation_text=f"Oversold ({OVERSOLD_THRESHOLD})")
            fig.add_vline(x=70, line_dash="dash", line_color="green", 
                         annotation_text="Overbought (70)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance scatter plot
            st.subheader("Performance vs RSI")
            fig = px.scatter(all_data, x='rsi', y='pct_change_10d', 
                           hover_data=['symbol'], 
                           title="10-Day Performance vs RSI")
            fig.add_hline(y=-MIN_DECLINE_PERCENT, line_dash="dash", line_color="red")
            fig.add_vline(x=OVERSOLD_THRESHOLD, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No market data available. Please refresh data first.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Data provided by Polygon.io. This is for educational purposes only and not financial advice.*")

if __name__ == "__main__":
    main()