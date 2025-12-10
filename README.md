# Stock Portfolio Analyzer - Flask Application

A modern, interactive Flask web application for analyzing stock portfolios with real-time data visualization and performance metrics.

## Features

✨ **Interactive Web Interface**
- Add/remove stocks to your portfolio
- Real-time portfolio metrics and performance tracking
- Beautiful, responsive design

📊 **Advanced Analysis**
- Annualized return calculations
- Portfolio volatility analysis
- Sharpe ratio calculation
- Stock correlation heatmap
- Individual stock performance tracking

📈 **Data Visualization**
- Cumulative performance chart
- Stock correlation matrix
- Historical price data

🔧 **Easy to Use**
- Simple ticker input
- Custom date ranges
- One-click analysis

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Open in browser:**
Navigate to `http://localhost:5000`

## Usage

### Quick Start

1. **Enter Portfolio Name** (optional)
   - Customize your portfolio name
   - Click "Save Name" to update

2. **Add Stocks**
   - Enter ticker symbol (e.g., AAPL, MSFT, GOOGL)
   - Select start and end dates (defaults to last year)
   - Click "Add Stock"

3. **Analyze Portfolio**
   - Click "Analyze Portfolio" button
   - View metrics, charts, and correlations

### Example Workflow

```
1. Add AAPL from 2023-01-01 to 2024-01-01
2. Add MSFT from 2023-01-01 to 2024-01-01
3. Add GOOGL from 2023-01-01 to 2024-01-01
4. Click "Analyze Portfolio"
5. View performance metrics, charts, and correlations
```

## API Endpoints

### GET /api/stocks
Get list of stocks in portfolio

### POST /api/stocks
Add a stock to portfolio
```json
{
  "ticker": "AAPL",
  "start": "2023-01-01",
  "end": "2024-01-01"
}
```

### DELETE /api/stocks/<ticker>
Remove a stock from portfolio

### GET /api/analysis
Get portfolio analysis metrics and summary

### GET /api/chart
Get cumulative performance chart (base64 PNG)

### GET /api/correlation
Get correlation heatmap (base64 PNG)

### GET /api/portfolio-name
Get portfolio name

### POST /api/portfolio-name
Set portfolio name
```json
{
  "name": "My Stocks"
}
```

## Project Structure

```
portfolio-analyzer/
├── app.py                 # Flask application main file
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── style.css         # CSS styling
    └── app.js            # JavaScript functionality
```

## Key Classes and Methods

### StockPortfolio Class

**Methods:**
- `add_stock(ticker, start, end)` - Fetch and add stock data
- `remove_stock(ticker)` - Remove stock from portfolio
- `get_stocks()` - Get list of stocks
- `portfolio_dataframe()` - Get all stocks as DataFrame
- `portfolio_returns()` - Calculate daily returns
- `analyze_portfolio(weights)` - Get portfolio metrics
- `get_cumulative_performance()` - Get cumulative returns
- `get_chart_base64()` - Generate performance chart
- `get_correlation_heatmap_base64()` - Generate correlation heatmap
- `get_performance_summary()` - Get individual stock summary

## Performance Metrics Explained

### Annual Return
The annualized percentage return of your portfolio based on historical data.

### Annual Volatility
The annualized standard deviation of returns - measures portfolio risk.

### Sharpe Ratio
Risk-adjusted return metric. Higher values indicate better risk-adjusted performance.

## Troubleshooting

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Port 5000 already in use"
Modify `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### "No data found for ticker"
- Verify ticker symbol is correct (e.g., AAPL not APPLE)
- Check if ticker is valid on Yahoo Finance
- Ensure dates are within valid range

### Charts not displaying
- Check browser console for errors (F12)
- Ensure at least one stock is added
- Wait for analysis to complete

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Performance Tips

1. **Shorter date ranges** load faster
2. **Fewer stocks** provide quicker analysis
3. Use **modern browsers** for best performance
4. Clear browser cache if charts don't update

## Future Enhancements

- [ ] Portfolio comparison across time periods
- [ ] Buy/sell recommendations
- [ ] Risk tolerance assessment
- [ ] Portfolio optimization
- [ ] Export functionality (PDF, CSV)
- [ ] User accounts and data persistence
- [ ] Advanced technical indicators
- [ ] Backtesting features

## Technical Details

### Data Source
- **Yahoo Finance** - Real-time stock prices and historical data

### Libraries Used
- **Flask** - Web framework
- **yfinance** - Stock data fetching
- **pandas** - Data manipulation
- **numpy** - Numerical calculations
- **matplotlib** - Chart generation

### Frontend
- Vanilla JavaScript (no frameworks)
- CSS Grid for responsive layout
- Base64 encoding for chart display

## License

This project is free to use and modify for personal or educational purposes.

## Support

For issues:
1. Check browser console (F12) for errors
2. Verify internet connection
3. Try clearing browser cache
4. Ensure all dependencies are installed

## Version

1.0.0 - December 2025
