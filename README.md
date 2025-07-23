# 📈 Stock Reversal Flow Dashboard

A Python-based stock dashboard that identifies overextended stocks and potential reversal opportunities using technical analysis. Built for day traders and swing traders looking for oversold conditions in the market.

## 🎯 Features

- **Real-time Stock Analysis**: Monitor 20 popular stocks from the S&P 500
- **Technical Indicators**: RSI, SMA, percentage changes over multiple timeframes
- **Reversal Detection**: Automatically identifies oversold stocks (RSI < 30) with significant declines
- **Interactive Dashboard**: Clean, web-based interface built with Streamlit
- **Historical Data**: 100 days of historical data for backtesting patterns
- **Market Overview**: Portfolio-wide metrics and visualizations

## 🏗️ Architecture

```
Polygon API → Data Collector → SQLite Database → Streamlit Dashboard
```

- **Data Source**: Polygon.io Free Tier (delayed/historical data)
- **Backend**: Python with pandas, TA-Lib for technical analysis
- **Database**: SQLite for local storage
- **Frontend**: Streamlit with Plotly charts
- **Analysis**: RSI, SMA crossovers, percentage decline detection

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Polygon.io API key (free tier available)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Stock-Reversal-Flow
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Polygon API key
   ```

4. **Collect initial data**:
   ```bash
   python collect_data.py
   ```

5. **Launch dashboard**:
   ```bash
   python run_dashboard.py
   ```

The dashboard will open at `http://localhost:8501`

## 📊 Dashboard Features

### Individual Stock Analysis
- Candlestick charts with SMA overlay
- RSI indicator with oversold/overbought levels
- Key metrics: current price, 5-day/10-day changes
- Reversal opportunity alerts

### Oversold Stocks
- List of stocks meeting reversal criteria
- Quick charts for top candidates
- Sortable by RSI and decline percentage

### Market Overview
- Portfolio-wide statistics
- RSI distribution histogram
- Performance vs RSI scatter plot
- Market sentiment indicators

## ⚙️ Configuration

Edit `config/settings.py` to customize:

- **Watchlist**: Modify `WATCHLIST` to track different stocks
- **RSI Settings**: Adjust `RSI_PERIOD` and `OVERSOLD_THRESHOLD`
- **Decline Thresholds**: Change `MIN_DECLINE_PERCENT` and `DECLINE_LOOKBACK_DAYS`
- **Update Frequency**: Modify `UPDATE_INTERVAL_MINUTES`

## 📁 Project Structure

```
Stock-Reversal-Flow/
├── src/
│   ├── data_collector.py    # Polygon API integration & indicators
│   ├── database.py          # SQLite operations
│   └── dashboard.py         # Streamlit dashboard
├── config/
│   └── settings.py          # Configuration parameters
├── data/
│   └── stocks.db           # SQLite database (created automatically)
├── collect_data.py         # Data collection script
├── run_dashboard.py        # Dashboard launcher
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## 🔄 Data Collection

The system collects:
- **OHLCV Data**: Open, High, Low, Close, Volume
- **Technical Indicators**: RSI (14-period), SMA (20-period)
- **Performance Metrics**: 5-day and 10-day percentage changes
- **Signals**: Oversold conditions and reversal opportunities

Data is updated with rate limiting (5 calls/minute) to respect Polygon's free tier limits.

## 📈 Trading Strategy

The dashboard identifies potential reversal opportunities based on:

1. **Oversold RSI**: RSI below 30 (configurable)
2. **Significant Decline**: Price dropped >10% over 10 days (configurable)
3. **Volume Confirmation**: Available in raw data for manual analysis

**Disclaimer**: This tool is for educational purposes only. Always do your own research and consider risk management before making trading decisions.

## 🛠️ Development

### Adding New Indicators
1. Modify `data_collector.py` → `calculate_indicators()` method
2. Update database schema in `database.py` if needed
3. Add visualization in `dashboard.py`

### Adding New Stocks
1. Update `WATCHLIST` in `config/settings.py`
2. Run `python collect_data.py` to fetch new data

### Extending Timeframes
1. Modify `fetch_daily_data()` in `data_collector.py`
2. Add 4-hour data collection methods
3. Update dashboard filters

## 📋 TODO / Future Enhancements

- [ ] Add 4-hour timeframe analysis
- [ ] Implement pattern recognition (head & shoulders, double bottoms)
- [ ] Add email/SMS alerts for reversal signals
- [ ] Include volume analysis and anomaly detection
- [ ] Add backtesting capabilities
- [ ] Implement screener for custom criteria
- [ ] Add more technical indicators (MACD, Bollinger Bands)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-indicator`)
3. Commit changes (`git commit -am 'Add new indicator'`)
4. Push to branch (`git push origin feature/new-indicator`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Polygon.io** for providing free stock market data
- **Streamlit** for the amazing dashboard framework
- **TA-Lib** for technical analysis indicators
- **Plotly** for interactive charting capabilities