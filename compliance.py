"""
Portfolio Compliance Monitoring Engine
Implements basic compliance rules for portfolio management
"""

import pandas as pd
import numpy as np
from datetime import datetime
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance check status"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"


class ComplianceRule:
    """Base class for compliance rules"""
    
    def __init__(self, rule_id, name, description, enabled=True):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.enabled = enabled
    
    def check(self, portfolio_data):
        """Check if portfolio complies with rule. Override in subclasses."""
        raise NotImplementedError
    
    def get_result(self, status, message, details=None):
        """Format compliance check result"""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'status': status.value,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }


class MaxConcentrationRule(ComplianceRule):
    """Ensure no single stock exceeds maximum concentration"""
    
    def __init__(self, max_concentration=0.30, warning_threshold=0.25):
        super().__init__(
            'max_concentration',
            'Maximum Concentration Limit',
            'Ensures no single stock exceeds maximum portfolio weight'
        )
        self.max_concentration = max_concentration
        self.warning_threshold = warning_threshold
    
    def check(self, portfolio_data):
        """Check concentration limits"""
        if not portfolio_data['stocks']:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                'No stocks in portfolio',
                {'stocks_count': 0}
            )
        
        # Calculate weights based on latest prices
        latest_prices = portfolio_data['latest_prices']
        total_value = sum(latest_prices.values())
        
        if total_value == 0:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                'Portfolio has no value',
                {}
            )
        
        weights = {ticker: price / total_value for ticker, price in latest_prices.items()}
        max_weight = max(weights.values())
        max_ticker = max(weights, key=weights.get)
        
        if max_weight > self.max_concentration:
            return self.get_result(
                ComplianceStatus.NON_COMPLIANT,
                f'{max_ticker} exceeds maximum concentration of {self.max_concentration*100:.1f}%',
                {
                    'ticker': max_ticker,
                    'weight': f'{max_weight*100:.2f}%',
                    'limit': f'{self.max_concentration*100:.1f}%',
                    'excess': f'{(max_weight - self.max_concentration)*100:.2f}%'
                }
            )
        elif max_weight > self.warning_threshold:
            return self.get_result(
                ComplianceStatus.WARNING,
                f'{max_ticker} approaching concentration limit of {self.max_concentration*100:.1f}%',
                {
                    'ticker': max_ticker,
                    'weight': f'{max_weight*100:.2f}%',
                    'limit': f'{self.max_concentration*100:.1f}%',
                    'warning_threshold': f'{self.warning_threshold*100:.1f}%'
                }
            )
        else:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                'All holdings within concentration limits',
                {
                    'max_weight': f'{max_weight*100:.2f}%',
                    'limit': f'{self.max_concentration*100:.1f}%'
                }
            )


class MinDiversificationRule(ComplianceRule):
    """Ensure minimum number of holdings for diversification"""
    
    def __init__(self, min_holdings=3, warning_threshold=4):
        super().__init__(
            'min_diversification',
            'Minimum Diversification',
            'Ensures portfolio has minimum number of holdings'
        )
        self.min_holdings = min_holdings
        self.warning_threshold = warning_threshold
    
    def check(self, portfolio_data):
        """Check diversification requirement"""
        num_holdings = len(portfolio_data['stocks'])
        
        if num_holdings < self.min_holdings:
            return self.get_result(
                ComplianceStatus.NON_COMPLIANT,
                f'Portfolio has {num_holdings} holdings, minimum is {self.min_holdings}',
                {
                    'current_holdings': num_holdings,
                    'minimum_required': self.min_holdings,
                    'deficit': self.min_holdings - num_holdings
                }
            )
        elif num_holdings < self.warning_threshold:
            return self.get_result(
                ComplianceStatus.WARNING,
                f'Portfolio has {num_holdings} holdings, recommended minimum is {self.warning_threshold}',
                {
                    'current_holdings': num_holdings,
                    'recommended_minimum': self.warning_threshold,
                    'deficit': self.warning_threshold - num_holdings
                }
            )
        else:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                f'Portfolio well diversified with {num_holdings} holdings',
                {
                    'current_holdings': num_holdings,
                    'minimum_required': self.min_holdings
                }
            )


class VolatilityRule(ComplianceRule):
    """Ensure portfolio volatility stays within limits"""
    
    def __init__(self, max_volatility=0.25, warning_threshold=0.20):
        super().__init__(
            'volatility_limit',
            'Volatility Limit',
            'Ensures portfolio annual volatility does not exceed maximum'
        )
        self.max_volatility = max_volatility
        self.warning_threshold = warning_threshold
    
    def check(self, portfolio_data):
        """Check volatility limits"""
        volatility = portfolio_data.get('annual_volatility', 0)
        
        if volatility > self.max_volatility:
            return self.get_result(
                ComplianceStatus.NON_COMPLIANT,
                f'Portfolio volatility {volatility*100:.2f}% exceeds limit of {self.max_volatility*100:.2f}%',
                {
                    'current_volatility': f'{volatility*100:.2f}%',
                    'limit': f'{self.max_volatility*100:.2f}%',
                    'excess': f'{(volatility - self.max_volatility)*100:.2f}%'
                }
            )
        elif volatility > self.warning_threshold:
            return self.get_result(
                ComplianceStatus.WARNING,
                f'Portfolio volatility {volatility*100:.2f}% approaching limit',
                {
                    'current_volatility': f'{volatility*100:.2f}%',
                    'limit': f'{self.max_volatility*100:.2f}%',
                    'warning_threshold': f'{self.warning_threshold*100:.2f}%'
                }
            )
        else:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                f'Portfolio volatility {volatility*100:.2f}% within limits',
                {
                    'current_volatility': f'{volatility*100:.2f}%',
                    'limit': f'{self.max_volatility*100:.2f}%'
                }
            )


class SharpeRatioRule(ComplianceRule):
    """Ensure minimum Sharpe ratio for risk-adjusted returns"""
    
    def __init__(self, min_sharpe_ratio=0.5, warning_threshold=1.0):
        super().__init__(
            'sharpe_ratio',
            'Minimum Sharpe Ratio',
            'Ensures portfolio maintains acceptable risk-adjusted returns'
        )
        self.min_sharpe_ratio = min_sharpe_ratio
        self.warning_threshold = warning_threshold
    
    def check(self, portfolio_data):
        """Check Sharpe ratio requirement"""
        sharpe_ratio = portfolio_data.get('sharpe_ratio', 0)
        
        if sharpe_ratio < self.min_sharpe_ratio:
            return self.get_result(
                ComplianceStatus.NON_COMPLIANT,
                f'Sharpe ratio {sharpe_ratio:.3f} below minimum of {self.min_sharpe_ratio:.3f}',
                {
                    'current_sharpe': f'{sharpe_ratio:.3f}',
                    'minimum': f'{self.min_sharpe_ratio:.3f}',
                    'deficit': f'{(self.min_sharpe_ratio - sharpe_ratio):.3f}'
                }
            )
        elif sharpe_ratio < self.warning_threshold:
            return self.get_result(
                ComplianceStatus.WARNING,
                f'Sharpe ratio {sharpe_ratio:.3f} below recommended {self.warning_threshold:.3f}',
                {
                    'current_sharpe': f'{sharpe_ratio:.3f}',
                    'recommended': f'{self.warning_threshold:.3f}',
                    'deficit': f'{(self.warning_threshold - sharpe_ratio):.3f}'
                }
            )
        else:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                f'Sharpe ratio {sharpe_ratio:.3f} exceeds minimum requirement',
                {
                    'current_sharpe': f'{sharpe_ratio:.3f}',
                    'minimum': f'{self.min_sharpe_ratio:.3f}'
                }
            )


class CorrelationRule(ComplianceRule):
    """Ensure portfolio has adequate diversification through correlation analysis"""
    
    def __init__(self, max_avg_correlation=0.7, warning_threshold=0.6):
        super().__init__(
            'correlation_limit',
            'Correlation Diversification',
            'Ensures portfolio stocks are not too highly correlated'
        )
        self.max_avg_correlation = max_avg_correlation
        self.warning_threshold = warning_threshold
    
    def check(self, portfolio_data):
        """Check correlation levels"""
        correlation = portfolio_data.get('avg_correlation', None)
        
        if correlation is None:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                'Insufficient data for correlation check (need at least 2 stocks)',
                {'stocks_in_portfolio': len(portfolio_data['stocks'])}
            )
        
        if correlation > self.max_avg_correlation:
            return self.get_result(
                ComplianceStatus.NON_COMPLIANT,
                f'Average correlation {correlation:.2f} exceeds limit of {self.max_avg_correlation:.2f}',
                {
                    'avg_correlation': f'{correlation:.2f}',
                    'limit': f'{self.max_avg_correlation:.2f}',
                    'excess': f'{(correlation - self.max_avg_correlation):.2f}'
                }
            )
        elif correlation > self.warning_threshold:
            return self.get_result(
                ComplianceStatus.WARNING,
                f'Average correlation {correlation:.2f} approaching limit',
                {
                    'avg_correlation': f'{correlation:.2f}',
                    'limit': f'{self.max_avg_correlation:.2f}',
                    'warning_threshold': f'{self.warning_threshold:.2f}'
                }
            )
        else:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                f'Portfolio stocks adequately diversified with correlation {correlation:.2f}',
                {
                    'avg_correlation': f'{correlation:.2f}',
                    'limit': f'{self.max_avg_correlation:.2f}'
                }
            )


class CashPositionRule(ComplianceRule):
    """Ensure minimum cash reserve in portfolio"""
    
    def __init__(self, min_cash_percentage=0.05, warning_threshold=0.10):
        super().__init__(
            'cash_position',
            'Minimum Cash Reserve',
            'Ensures portfolio maintains minimum cash for rebalancing'
        )
        self.min_cash_percentage = min_cash_percentage
        self.warning_threshold = warning_threshold
    
    def check(self, portfolio_data):
        """Check cash reserve requirement"""
        cash_percentage = portfolio_data.get('cash_percentage', 0)
        
        if cash_percentage < self.min_cash_percentage:
            return self.get_result(
                ComplianceStatus.NON_COMPLIANT,
                f'Cash position {cash_percentage*100:.2f}% below minimum of {self.min_cash_percentage*100:.2f}%',
                {
                    'current_cash': f'{cash_percentage*100:.2f}%',
                    'minimum': f'{self.min_cash_percentage*100:.2f}%',
                    'required_increase': f'{(self.min_cash_percentage - cash_percentage)*100:.2f}%'
                }
            )
        elif cash_percentage < self.warning_threshold:
            return self.get_result(
                ComplianceStatus.WARNING,
                f'Cash position {cash_percentage*100:.2f}% below recommended {self.warning_threshold*100:.2f}%',
                {
                    'current_cash': f'{cash_percentage*100:.2f}%',
                    'recommended': f'{self.warning_threshold*100:.2f}%',
                    'recommended_increase': f'{(self.warning_threshold - cash_percentage)*100:.2f}%'
                }
            )
        else:
            return self.get_result(
                ComplianceStatus.COMPLIANT,
                f'Cash position {cash_percentage*100:.2f}% within acceptable range',
                {
                    'current_cash': f'{cash_percentage*100:.2f}%',
                    'minimum': f'{self.min_cash_percentage*100:.2f}%'
                }
            )


class ComplianceMonitor:
    """Main compliance monitoring engine"""
    
    def __init__(self):
        """Initialize with default compliance rules"""
        self.rules = []
        self.add_default_rules()
    
    def add_default_rules(self):
        """Add standard compliance rules"""
        self.rules = [
            MaxConcentrationRule(max_concentration=0.30, warning_threshold=0.25),
            MinDiversificationRule(min_holdings=3, warning_threshold=4),
            VolatilityRule(max_volatility=0.25, warning_threshold=0.20),
            SharpeRatioRule(min_sharpe_ratio=0.5, warning_threshold=1.0),
            CorrelationRule(max_avg_correlation=0.7, warning_threshold=0.6),
            CashPositionRule(min_cash_percentage=0.05, warning_threshold=0.10)
        ]
    
    def add_rule(self, rule):
        """Add a custom compliance rule"""
        if isinstance(rule, ComplianceRule):
            self.rules.append(rule)
            return True
        return False
    
    def remove_rule(self, rule_id):
        """Remove a rule by ID"""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
    
    def get_rules(self):
        """Get all active rules"""
        return [{'id': r.rule_id, 'name': r.name, 'description': r.description, 'enabled': r.enabled} 
                for r in self.rules]
    
    def check_compliance(self, portfolio):
        """Run all compliance checks on portfolio"""
        if not portfolio.stocks:
            return {
                'overall_status': 'compliant',
                'total_rules': len(self.rules),
                'compliant': len(self.rules),
                'warnings': 0,
                'non_compliant': 0,
                'checks': [],
                'timestamp': datetime.now().isoformat()
            }
        
        # Prepare portfolio data
        portfolio_data = self._prepare_portfolio_data(portfolio)
        
        # Run all compliance checks
        results = []
        compliant_count = 0
        warning_count = 0
        non_compliant_count = 0
        
        for rule in self.rules:
            if rule.enabled:
                check_result = rule.check(portfolio_data)
                results.append(check_result)
                
                status = check_result['status']
                if status == 'compliant':
                    compliant_count += 1
                elif status == 'warning':
                    warning_count += 1
                else:
                    non_compliant_count += 1
        
        # Determine overall status
        if non_compliant_count > 0:
            overall_status = 'non_compliant'
        elif warning_count > 0:
            overall_status = 'warning'
        else:
            overall_status = 'compliant'
        
        return {
            'overall_status': overall_status,
            'total_rules': len(self.rules),
            'compliant': compliant_count,
            'warnings': warning_count,
            'non_compliant': non_compliant_count,
            'checks': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _prepare_portfolio_data(self, portfolio):
        """Prepare portfolio data for compliance checks"""
        returns = portfolio.portfolio_returns()
        analysis = portfolio.analyze_portfolio()
        
        # Calculate latest prices (using last value in each stock's data)
        latest_prices = {}
        for ticker in portfolio.stocks:
            data = portfolio.stocks[ticker]['data']
            latest_prices[ticker] = float(data.iloc[-1]) if len(data) > 0 else 0
        
        # Calculate average correlation
        avg_correlation = None
        if returns is not None and not isinstance(returns, pd.Series) and len(returns.columns) > 1:
            correlation_matrix = returns.corr()
            # Get upper triangle values (excluding diagonal)
            upper_triangle = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)]
            avg_correlation = float(np.mean(upper_triangle))
        
        portfolio_data = {
            'stocks': portfolio.stocks,
            'latest_prices': latest_prices,
            'annual_return': analysis['annual_return'] if analysis else 0,
            'annual_volatility': analysis['annual_volatility'] if analysis else 0,
            'sharpe_ratio': analysis['sharpe_ratio'] if analysis else 0,
            'avg_correlation': avg_correlation,
            'cash_percentage': 0.0  # Default, can be updated if cash is tracked
        }
        
        return portfolio_data
