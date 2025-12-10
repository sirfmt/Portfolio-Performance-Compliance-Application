"""
Stock Portfolio Analysis Flask Application
Interactive web app for analyzing stock portfolios
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import json
import warnings
from datetime import datetime, timedelta
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from compliance import ComplianceMonitor

# Suppress yfinance FutureWarning
warnings.filterwarnings('ignore', category=FutureWarning)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize portfolio and compliance monitor
portfolio = None
compliance_monitor = ComplianceMonitor()


class StockPortfolio:
    """Stock portfolio analysis class"""
    
    def __init__(self):
        self.stocks = {}  # {ticker: {'data': Series, 'start': date, 'end': date}}
        self.name = "My Portfolio"
    
    def add_stock(self, ticker, start, end):
        """Fetch stock data and add to portfolio"""
        try:
            ticker = ticker.upper()
            data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
            if data.empty:
                return False, f"No data found for {ticker}."
            
            # Store stock data with metadata
            self.stocks[ticker] = {
                'data': data['Close'].copy(),
                'start_date': start,
                'end_date': end,
                'num_records': len(data)
            }
            return True, f"{ticker} added successfully."
        except Exception as e:
            return False, f"Error adding {ticker}: {str(e)}"
    
    def remove_stock(self, ticker):
        """Remove a stock from portfolio"""
        ticker = ticker.upper()
        if ticker in self.stocks:
            del self.stocks[ticker]
            return True
        return False
    
    def get_stocks(self):
        """Get list of stocks in portfolio"""
        return list(self.stocks.keys())
    
    def get_stock_data(self, ticker):
        """Get raw data for a specific stock"""
        ticker = ticker.upper()
        if ticker in self.stocks:
            return self.stocks[ticker]['data']
        return None
    
    def portfolio_dataframe(self):
        """Combine all stocks into one dataframe"""
        if not self.stocks:
            return None
        
        try:
            # Extract data from all stocks
            data_dict = {}
            for ticker in self.stocks:
                data_dict[ticker] = self.stocks[ticker]['data']
            
            # Create dataframe
            df = pd.concat(data_dict, axis=1)
            df.columns = data_dict.keys()
            
            return df
        except Exception as e:
            print(f"Error creating portfolio dataframe: {e}")
            return None
    
    def portfolio_returns(self):
        """Calculate daily returns of portfolio"""
        df = self.portfolio_dataframe()
        if df is None:
            return None
        
        try:
            returns = df.pct_change().dropna()
            return returns
        except Exception as e:
            print(f"Error calculating returns: {e}")
            return None
    
    def analyze_portfolio(self, weights=None):
        """Compute portfolio performance metrics"""
        returns = self.portfolio_returns()
        if returns is None:
            return None
        
        # Handle single stock case
        if isinstance(returns, pd.Series):
            portfolio_return = returns.mean() * 252
            portfolio_volatility = returns.std() * np.sqrt(252)
        else:
            if weights is None:
                weights = [1/len(returns.columns)] * len(returns.columns)
            else:
                weights = np.array(weights)
            
            portfolio_return = (returns.mean() @ weights) * 252
            portfolio_volatility = (np.sqrt(np.dot(weights, returns.cov().dot(weights)))) * np.sqrt(252)
        
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility != 0 else 0
        
        return {
            'annual_return': float(portfolio_return),
            'annual_volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio)
        }
    
    def get_cumulative_performance(self):
        """Get cumulative performance data"""
        returns = self.portfolio_returns()
        if returns is None:
            return None
        cumulative = (returns + 1).cumprod()
        return cumulative
    
    def get_chart_base64(self):
        """Generate chart and return as base64"""
        if not self.stocks:
            return None
        
        try:
            cumulative = self.get_cumulative_performance()
            if cumulative is None:
                return None
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Handle both Series and DataFrame
            if isinstance(cumulative, pd.Series):
                ax.plot(cumulative.index, cumulative.values, linewidth=2)
            else:
                for column in cumulative.columns:
                    ax.plot(cumulative.index, cumulative[column], label=column, linewidth=2)
                ax.legend(loc='best')
            
            ax.set_title('Portfolio Cumulative Performance', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Growth of $1', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        except Exception as e:
            print(f"Error generating chart: {e}")
            return None
    
    def get_correlation_heatmap_base64(self):
        """Generate correlation heatmap and return as base64"""
        returns = self.portfolio_returns()
        if returns is None:
            return None
        
        # Need at least 2 stocks for correlation
        if isinstance(returns, pd.Series) or len(returns.columns) < 2:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 6))
        correlation = returns.corr()
        
        im = ax.imshow(correlation, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        ax.set_xticks(range(len(correlation.columns)))
        ax.set_yticks(range(len(correlation.columns)))
        ax.set_xticklabels(correlation.columns, rotation=45)
        ax.set_yticklabels(correlation.columns)
        ax.set_title('Stock Correlation Matrix', fontsize=14, fontweight='bold')
        
        # Add correlation values
        for i in range(len(correlation.columns)):
            for j in range(len(correlation.columns)):
                text = ax.text(j, i, f'{correlation.iloc[i, j]:.2f}',
                              ha="center", va="center", color="black", fontsize=10)
        
        plt.colorbar(im, ax=ax)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return image_base64
    
    def get_performance_summary(self):
        """Get summary of current performance"""
        if not self.stocks:
            return None
        
        summary = {}
        for ticker in self.stocks:
            try:
                data = self.stocks[ticker]['data']
                if len(data) > 0:
                    start_price = float(data.iloc[0])
                    end_price = float(data.iloc[-1])
                    returns = ((end_price - start_price) / start_price) * 100
                    summary[ticker] = {
                        'start_price': start_price,
                        'end_price': end_price,
                        'return': returns
                    }
            except Exception as e:
                print(f"Error getting performance for {ticker}: {e}")
        
        return summary if summary else None


# Global portfolio instance
portfolio = StockPortfolio()


# Routes
@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get list of stocks in portfolio"""
    stocks = portfolio.get_stocks()
    return jsonify({'stocks': stocks})


@app.route('/api/stocks', methods=['POST'])
def add_stock():
    """Add a stock to portfolio"""
    data = request.json
    ticker = data.get('ticker', '').upper()
    start = data.get('start', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    end = data.get('end', datetime.now().strftime('%Y-%m-%d'))
    
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400
    
    success, message = portfolio.add_stock(ticker, start, end)
    
    if success:
        return jsonify({'message': message, 'stocks': portfolio.get_stocks()}), 201
    else:
        return jsonify({'error': message}), 400


@app.route('/api/stocks/<ticker>', methods=['DELETE'])
def remove_stock(ticker):
    """Remove a stock from portfolio"""
    if portfolio.remove_stock(ticker.upper()):
        return jsonify({'message': f'{ticker} removed', 'stocks': portfolio.get_stocks()})
    else:
        return jsonify({'error': 'Stock not found'}), 404


@app.route('/api/analysis', methods=['GET'])
def analyze():
    """Analyze portfolio"""
    weights_str = request.args.get('weights', None)
    weights = None
    
    if weights_str:
        try:
            weights = json.loads(weights_str)
        except:
            pass
    
    analysis = portfolio.analyze_portfolio(weights)
    
    if analysis is None:
        return jsonify({'error': 'Portfolio is empty'}), 400
    
    summary = portfolio.get_performance_summary()
    
    return jsonify({
        'analysis': analysis,
        'summary': summary
    })


@app.route('/api/chart', methods=['GET'])
def get_chart():
    """Get portfolio performance chart"""
    chart_base64 = portfolio.get_chart_base64()
    
    if chart_base64 is None:
        return jsonify({'error': 'No data to display'}), 400
    
    return jsonify({'chart': f'data:image/png;base64,{chart_base64}'})


@app.route('/api/correlation', methods=['GET'])
def get_correlation():
    """Get correlation heatmap"""
    heatmap_base64 = portfolio.get_correlation_heatmap_base64()
    
    if heatmap_base64 is None:
        return jsonify({'error': 'Need at least 2 stocks for correlation'}), 400
    
    return jsonify({'heatmap': f'data:image/png;base64,{heatmap_base64}'})


@app.route('/api/portfolio-name', methods=['GET', 'POST'])
def portfolio_name():
    """Get or set portfolio name"""
    if request.method == 'POST':
        data = request.json
        portfolio.name = data.get('name', 'My Portfolio')
        return jsonify({'name': portfolio.name})
    else:
        return jsonify({'name': portfolio.name})


@app.route('/api/data', methods=['GET'])
def get_data():
    """Get portfolio dataframe as JSON"""
    df = portfolio.portfolio_dataframe()
    
    if df is None:
        return jsonify({'error': 'Portfolio is empty'}), 400
    
    data = {
        'dates': df.index.strftime('%Y-%m-%d').tolist(),
        'stocks': {}
    }
    
    for column in df.columns:
        data['stocks'][column] = df[column].astype(float).tolist()
    
    return jsonify(data)


@app.route('/api/data')
def get_portfolio_data():
    """Get raw portfolio data"""
    if not portfolio.stocks:
        return jsonify({'data': {}, 'error': 'No stocks in portfolio'})
    
    data = portfolio.portfolio_dataframe()
    if data is None:
        return jsonify({'data': {}, 'error': 'Error retrieving data'})
    
    return jsonify({
        'data': data.to_dict(),
        'stocks': portfolio.get_stocks()
    })


# Compliance Monitoring Endpoints
@app.route('/api/compliance/check', methods=['GET'])
def check_compliance():
    """Run compliance checks on portfolio"""
    try:
        if not portfolio.stocks:
            return jsonify({
                'overall_status': 'compliant',
                'message': 'Portfolio is empty',
                'checks': []
            })
        
        compliance_result = compliance_monitor.check_compliance(portfolio)
        return jsonify(compliance_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compliance/rules', methods=['GET'])
def get_compliance_rules():
    """Get list of active compliance rules"""
    try:
        rules = compliance_monitor.get_rules()
        return jsonify({
            'total_rules': len(rules),
            'rules': rules
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compliance/summary', methods=['GET'])
def get_compliance_summary():
    """Get compliance summary without detailed checks"""
    try:
        if not portfolio.stocks:
            return jsonify({
                'status': 'empty',
                'message': 'Portfolio has no holdings'
            })
        
        result = compliance_monitor.check_compliance(portfolio)
        
        return jsonify({
            'overall_status': result['overall_status'],
            'compliance_score': f"{((result['compliant'] / result['total_rules']) * 100):.1f}%",
            'compliant_rules': result['compliant'],
            'warning_rules': result['warnings'],
            'non_compliant_rules': result['non_compliant'],
            'total_rules': result['total_rules']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)