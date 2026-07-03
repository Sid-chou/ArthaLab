# ArthaLab — Project Specification

## Vision

Build an institutional-grade quantitative portfolio analysis and optimization engine for Indian investors.

The framework should help investors make **evidence-based asset allocation decisions** using historical data, statistical analysis, and portfolio optimization techniques.

The system does **not** attempt to predict future market returns.

---

# Primary Objective

Determine which portfolio allocation provides the highest probability of achieving an investment goal while minimizing downside risk.

The optimizer should prioritize:

- Goal Achievement Probability
- Risk-adjusted Returns
- Capital Preservation
- Drawdown Control

rather than maximizing CAGR alone.

---

# First Use Case

Goal

Wedding Corpus

Target Date

December 2030

The framework should later support:

- Retirement
- Child Education
- House Purchase
- Emergency Fund
- Financial Independence

---

# Functional Requirements

The system shall support:

## Portfolio Inputs

- Current Portfolio
- Asset Allocation
- Fund Information
- Current Value
- XIRR

## Cashflows

- SIPs
- Lump Sum Investments
- Withdrawals

## Timeline

- Investment Start Date
- Goal Date

## Goals

Support multiple target values including:

- ₹7L
- ₹8L
- ₹9L
- ₹10L
- Custom Targets

---

# Supported Asset Classes

Current

- Equity
- Gold
- Silver
- Debt
- Liquid Funds
- Cash

Future

- REITs
- International Equity
- ETFs
- Bonds
- Bitcoin

---

# Analysis Modules

The framework should support:

- Historical Backtesting
- Rolling Window Analysis
- Bootstrap Simulation
- Monte Carlo Simulation
- Efficient Frontier Optimization
- Correlation Analysis
- Sensitivity Analysis
- Scenario Analysis

---

# Risk Metrics

- CAGR
- XIRR
- Volatility
- Maximum Drawdown
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Value at Risk (VaR)
- Conditional VaR (CVaR)
- Downside Deviation
- Sequence Risk
- Inflation-adjusted Return

---

# Goal Metrics

Calculate:

- Probability of reaching each target corpus
- Failure Probability
- Median Outcome
- Best Outcome
- Worst Outcome

---

# Data Requirements

Historical data should be stored locally.

Supported sources may include:

- NSE
- Nifty Indices
- AMFI
- RBI
- MCX
- World Gold Council

No live API calls should occur during analysis.

---

# Outputs

Generate:

Charts

- Portfolio Growth
- Allocation Drift
- Efficient Frontier
- Monte Carlo Fan Chart
- Rolling Returns
- Rolling Sharpe
- Drawdown
- Correlation Matrix

Reports

- Markdown
- PDF
- CSV
- JSON

---

# Non-Functional Requirements

The system should be:

- Modular
- Offline-first
- Deterministic
- Extensible
- Reproducible
- Testable
- Configuration-driven

---

# Success Criteria

The project is considered successful if it can:

- Compare multiple portfolio allocations
- Estimate goal achievement probability
- Quantify downside risk
- Recommend allocations using quantitative evidence
- Produce reproducible research outputs

---

# Default Assumptions

Inflation Rate: 6%

Target Goal:
Wedding corpus (December 2030)

Monthly SIP:
₹5,000

Lump Sums:
₹80,000 (Year 1)
₹80,000 (Year 2)

Benchmark:
Nifty TRI

Risk-Free Rate:
6%

Rebalancing:
Annual

Taxes:
Ignored in Phase 1

# Out of Scope

ArthaLab does **not**:

- Predict future returns
- Recommend specific mutual funds
- Provide financial advice
- Guarantee investment outcomes