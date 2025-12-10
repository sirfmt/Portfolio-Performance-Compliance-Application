# Portfolio Compliance Monitoring Engine

## Overview

The Portfolio Compliance Monitoring Engine is a comprehensive rule-based system that automatically validates your stock portfolio against predefined compliance rules. It helps ensure your portfolio adheres to investment policies and risk management guidelines.

## Features

### Basic Compliance Rules

The engine comes with 6 fundamental compliance rules:

#### 1. **Maximum Concentration Limit**
- **Rule ID**: `max_concentration`
- **Purpose**: Ensures no single stock dominates the portfolio
- **Parameters**:
  - Maximum concentration: 30% (default)
  - Warning threshold: 25% (default)
- **Why it matters**: Concentration risk is a major portfolio risk factor. High concentration in a single security exposes the portfolio to significant downside if that security underperforms.

#### 2. **Minimum Diversification**
- **Rule ID**: `min_diversification`
- **Purpose**: Ensures the portfolio has adequate holdings for diversification
- **Parameters**:
  - Minimum holdings: 3 (default)
  - Recommended minimum: 4 (default)
- **Why it matters**: A well-diversified portfolio reduces unsystematic risk. With too few holdings, you miss diversification benefits.

#### 3. **Volatility Limit**
- **Rule ID**: `volatility_limit`
- **Purpose**: Keeps portfolio volatility within acceptable bounds
- **Parameters**:
  - Maximum volatility: 25% annual (default)
  - Warning threshold: 20% annual (default)
- **Why it matters**: Portfolio volatility directly affects your risk exposure. Excessive volatility can lead to unacceptable drawdowns.

#### 4. **Minimum Sharpe Ratio**
- **Rule ID**: `sharpe_ratio`
- **Purpose**: Ensures portfolio maintains acceptable risk-adjusted returns
- **Parameters**:
  - Minimum Sharpe ratio: 0.5 (default)
  - Recommended minimum: 1.0 (default)
- **Why it matters**: The Sharpe ratio measures excess return per unit of risk. A higher ratio indicates better risk-adjusted performance.

#### 5. **Correlation Diversification**
- **Rule ID**: `correlation_limit`
- **Purpose**: Ensures stocks in the portfolio are not too highly correlated
- **Parameters**:
  - Maximum average correlation: 0.7 (default)
  - Warning threshold: 0.6 (default)
- **Why it matters**: Highly correlated stocks move together and don't provide true diversification benefits.

#### 6. **Minimum Cash Reserve**
- **Rule ID**: `cash_position`
- **Purpose**: Ensures portfolio maintains minimum cash for rebalancing and opportunities
- **Parameters**:
  - Minimum cash: 5% (default)
  - Recommended minimum: 10% (default)
- **Why it matters**: Cash reserves provide flexibility for rebalancing, emergency withdrawals, and taking advantage of market opportunities.

## Compliance Status Levels

Each compliance check returns one of three status levels:

### ✅ Compliant
The portfolio meets all requirements for this rule. No action needed.

### ⚠️ Warning
The portfolio is approaching a limit but hasn't breached it. Consider making adjustments.

### ❌ Non-Compliant
The portfolio violates the compliance rule. Immediate corrective action is needed.

## API Endpoints

### Check All Compliance Rules
```
GET /api/compliance/check
```
Runs all compliance checks and returns detailed results for each rule.

**Response**:
```json
{
  "overall_status": "warning|compliant|non_compliant",
  "total_rules": 6,
  "compliant": 4,
  "warnings": 1,
  "non_compliant": 1,
  "checks": [
    {
      "rule_id": "max_concentration",
      "name": "Maximum Concentration Limit",
      "status": "non_compliant",
      "message": "AAPL exceeds maximum concentration of 30.0%",
      "details": {
        "ticker": "AAPL",
        "weight": "35.50%",
        "limit": "30.0%",
        "excess": "5.50%"
      }
    }
    // ... more checks
  ]
}
```

### Get Compliance Summary
```
GET /api/compliance/summary
```
Returns a high-level compliance overview without detailed checks.

**Response**:
```json
{
  "overall_status": "warning",
  "compliance_score": "83.3%",
  "compliant_rules": 5,
  "warning_rules": 1,
  "non_compliant_rules": 0,
  "total_rules": 6
}
```

### Get Active Rules
```
GET /api/compliance/rules
```
Lists all active compliance rules with their parameters.

**Response**:
```json
{
  "total_rules": 6,
  "rules": [
    {
      "id": "max_concentration",
      "name": "Maximum Concentration Limit",
      "description": "Ensures no single stock exceeds maximum portfolio weight"
    }
    // ... more rules
  ]
}
```

## Using the Web Interface

### Compliance Monitor Panel

Located in the results section after running portfolio analysis:

1. **Compliance Score**: Visual indicator showing your portfolio's compliance percentage
2. **Compliance Statistics**: Shows counts of compliant, warning, and non-compliant rules
3. **Detailed Checks**: Click on any rule to see detailed information about why it passed or failed

### Color Coding

- **Green**: Compliant ✅
- **Orange**: Warning ⚠️
- **Red**: Non-Compliant ❌

## Customizing Compliance Rules

### Python API Usage

```python
from compliance import ComplianceMonitor, MaxConcentrationRule, ComplianceRule

# Create monitor
monitor = ComplianceMonitor()

# Adjust existing rule parameters
monitor.rules[0].max_concentration = 0.25  # Stricter limit

# Add custom rule
class MyCustomRule(ComplianceRule):
    def __init__(self):
        super().__init__(
            'my_rule',
            'My Custom Rule',
            'Custom compliance check'
        )
    
    def check(self, portfolio_data):
        # Implement your check logic
        pass

monitor.add_rule(MyCustomRule())

# Remove a rule
monitor.remove_rule('cash_position')

# Run compliance check
result = monitor.check_compliance(portfolio)
```

## Best Practices

### When Rules Trigger Warnings

1. **Concentration Warning**: Consider adding stocks from different sectors or reducing the overweight position
2. **Volatility Warning**: Evaluate if your risk tolerance aligns with portfolio composition
3. **Sharpe Ratio Warning**: Review underperforming holdings
4. **Correlation Warning**: Consider adding uncorrelated assets (different sectors, asset classes)

### When Rules Are Non-Compliant

1. **Act Immediately**: Non-compliance indicates policy violations
2. **Rebalance**: Adjust positions to bring portfolio back into compliance
3. **Document**: Track why violations occurred for future policy adjustments
4. **Review Policy**: Determine if policy limits are still appropriate

## Understanding the Details

Each compliance check provides detailed information:

- **Current Value**: The actual metric value
- **Limit**: The maximum/minimum allowed
- **Threshold**: Warning level (if applicable)
- **Excess/Deficit**: How far over/under the limit

Example details:
```
Current Volatility: 22.50%
Limit: 25.00%
Warning Threshold: 20.00%
Status: ⚠️ Warning
```

## Integration with Analysis

Compliance monitoring is automatically triggered when you:

1. Click "Analyze Portfolio"
2. Add or remove stocks
3. Load a saved portfolio

Results are displayed immediately in the compliance section of the results panel.

## Technical Implementation

The compliance engine consists of:

1. **compliance.py**: Core rules and monitoring logic
2. **app.py**: Flask API endpoints
3. **JavaScript**: Frontend display and interaction
4. **CSS**: Styling and visual feedback

### Architecture

```
ComplianceMonitor
├── Rule 1: MaxConcentrationRule
├── Rule 2: MinDiversificationRule
├── Rule 3: VolatilityRule
├── Rule 4: SharpeRatioRule
├── Rule 5: CorrelationRule
└── Rule 6: CashPositionRule
```

Each rule independently evaluates the portfolio and returns compliance status with details.

## Troubleshooting

### "Insufficient data for correlation check"
- **Cause**: Portfolio has fewer than 2 stocks
- **Solution**: Add at least one more stock to portfolio

### Compliance scores change between analyses
- **Cause**: Stock prices change, affecting weights and returns
- **Solution**: This is normal; re-analyze after portfolio changes

### All rules show compliant but portfolio seems risky
- **Cause**: Compliance rules are minimum standards, not optimization
- **Solution**: Consider adjusting rule parameters to be more restrictive

## Future Enhancements

Potential compliance rules for future versions:

- Sector concentration limits
- Debt-to-equity ratio limits
- ESG score requirements
- Liquidity requirements
- Currency exposure limits
- Option exposure limits
- Backtesting compliance over time
- Regulatory requirement checks (e.g., UCITS)

## References

- [Sharpe Ratio](https://en.wikipedia.org/wiki/Sharpe_ratio) - Risk-adjusted return metric
- [Portfolio Concentration](https://en.wikipedia.org/wiki/Herfindahl_index) - Concentration risk
- [Correlation Matrix](https://en.wikipedia.org/wiki/Correlation_and_dependence) - Diversification analysis
- [Portfolio Volatility](https://en.wikipedia.org/wiki/Volatility_(finance)) - Risk measurement

