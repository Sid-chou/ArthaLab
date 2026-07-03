# ArthaLab

> An institutional-style portfolio research and optimization framework for Indian investors.

## Overview

ArthaLab is a Python-based quantitative portfolio research framework focused on **goal-based investing** rather than return chasing.

Instead of asking:

> Which mutual fund gives the highest return?

ArthaLab answers:

> Which portfolio allocation gives the highest probability of achieving a financial goal while minimizing downside risk?

The first implementation focuses on building a wedding corpus by **December 2030**, but the framework is designed to support any long-term investment goal.

---

## Key Features

### Portfolio Analysis

- Historical Backtesting
- Rolling Window Analysis
- Portfolio Growth Simulation
- Drawdown Analysis

### Quantitative Research

- Monte Carlo Simulation
- Bootstrap Simulation
- Efficient Frontier Optimization
- Correlation & Sensitivity Analysis
- Historical Stress Testing

### Portfolio Analytics

- CAGR & XIRR
- Volatility
- Maximum Drawdown
- Sharpe / Sortino / Calmar Ratios
- VaR & CVaR
- Sequence of Returns Risk

### Goal-Based Investing

- Goal Probability Estimation
- Portfolio Comparison
- Risk-adjusted Allocation Evaluation
- Evidence-based Decision Support

---

## Technology

- Python
- pandas
- NumPy
- SciPy
- statsmodels
- cvxpy
- PyPortfolioOpt
- Plotly
- Matplotlib

---

## Repository Structure

```
ArthaLab/

docs/
src/
tests/
data/
reports/
notebooks/
```

---

## Current Status

🚧 Planning & Architecture Phase

Current work focuses on:

- System Architecture
- Data Pipeline Design
- Quantitative Research Engine
- Portfolio Optimization Framework

---

## Documentation

Detailed documentation can be found in:

- docs/PROJECT_SPEC.md
- docs/RESEARCH_NOTES.md
- docs/ARCHITECTURE.md (coming soon)

---
## Development Roadmap

### Phase 1 (MVP)
- Historical data ingestion
- Portfolio abstraction
- Cashflow engine
- Historical backtesting
- Rolling returns
- Growth & drawdown charts
- Markdown reports

### Phase 2
- Monte Carlo
- Bootstrap
- Risk metrics
- Efficient Frontier
- Portfolio comparison
- Rebalancing engine

### Phase 3
- Dashboard
- Portfolio optimizer
- Tax module
- Scenario builder
- PDF reports
- CLI / Streamlit

## Disclaimer

This project is intended for educational and research purposes only.

It is **not** financial advice.