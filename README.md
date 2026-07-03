# ArthaLab

> An institutional-style portfolio research and optimization framework for Indian investors.

## Overview

Indian investors often build portfolios based on intuition, recent market performance, or popular opinions. This project aims to replace opinion-driven investing with a reproducible, data-driven portfolio research framework.

The system analyzes different portfolio allocations using historical market data, statistical methods, quantitative finance techniques, and portfolio optimization algorithms.

Rather than answering:

> "Which mutual fund gives the highest return?"

this project answers:

> "Which asset allocation provides the highest probability of achieving a financial goal while minimizing unnecessary risk?"

The first implementation focuses on optimizing a wedding investment corpus with a target date of **December 2030**, but the framework is designed to support any long-term financial goal.

---

# Objectives

The project evaluates portfolios using multiple quantitative techniques instead of relying solely on CAGR or historical returns.

The framework will:

- Compare multiple portfolio allocations
- Simulate different market conditions
- Measure downside risk
- Estimate probability of achieving financial goals
- Evaluate historical robustness
- Recommend evidence-based asset allocations

---

# Features

## Historical Analysis

- Historical Backtesting
- Rolling Return Analysis
- Rolling CAGR
- Drawdown Analysis
- Portfolio Growth Simulation

---

## Quantitative Analysis

- Bootstrap Simulation
- Monte Carlo Simulation
- Efficient Frontier Optimization
- Correlation Analysis
- Sensitivity Analysis
- Scenario Analysis

---

## Portfolio Analytics

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
- Sequence of Returns Risk

---

## Goal-Based Investing

Instead of maximizing returns alone, the optimizer evaluates portfolios based on:

- Probability of Goal Achievement
- Risk-adjusted Returns
- Capital Preservation
- Drawdown Control
- Long-term Stability

---

# Supported Asset Classes

Current Version

- Equity
- Gold
- Silver
- Liquid Funds
- Debt Funds

Planned

- REITs
- International Equity
- ETFs
- Bonds
- Cash Allocation

---

# Current Use Case

The initial research focuses on optimizing a portfolio for:

- Goal: Wedding Corpus
- Target Date: December 2030
- Monthly SIP
- Periodic Lump Sum Investments
- Multiple Asset Allocation Strategies
- Historical Market Analysis

The framework itself is generic and can later support:

- Retirement Planning
- Child Education
- Home Purchase
- Financial Independence
- Emergency Funds

---

# Research Methodology

The optimizer does not rely on a single forecasting technique.

Instead, it combines multiple approaches:

- Historical Backtesting
- Rolling Window Analysis
- Bootstrap Sampling
- Monte Carlo Simulation
- Efficient Frontier Analysis
- Historical Stress Testing
- Portfolio Optimization

The objective is to evaluate portfolio robustness under different market environments rather than optimize for a single historical period.

---

# Technology Stack

## Language

- Python

## Libraries

- pandas
- NumPy
- SciPy
- matplotlib
- Plotly
- statsmodels
- cvxpy
- PyPortfolioOpt (optional)

---

# Project Structure

```
portfolio-optimizer/

│

├── docs/

│   ├── PROJECT_OVERVIEW.md

│   ├── DEVELOPMENT_ROADMAP.md

│   ├── TECH_SPEC.md

│   ├── ASSUMPTIONS.md

│   ├── RESEARCH_NOTES.md

│   └── CHANGELOG.md

│

├── data/

├── notebooks/

├── src/

├── reports/

└── tests/
```

---

# Development Roadmap

## Phase 1 (MVP)

- Historical Data Ingestion
- Portfolio Simulator
- Historical Backtesting
- Rolling Returns
- Growth Charts
- Markdown Report

---

## Phase 2

- Monte Carlo Simulation
- Bootstrap Simulation
- Efficient Frontier
- Risk Metrics
- Portfolio Comparison
- Rebalancing Engine

---

## Phase 3

- Streamlit Dashboard
- Portfolio Optimizer
- Decision Engine
- Scenario Builder
- PDF Report Generator
- Tax Module

---

# Guiding Principles

- Decisions must be data-driven.
- Every recommendation should be reproducible.
- Asset allocation is more important than fund selection.
- Risk matters as much as return.
- Historical performance should never be treated as a guarantee of future performance.
- Every assumption must be documented.

---

# Project Status

Current Status:

**Planning & Research Phase**

The architecture, methodology, and research framework are being designed before implementation begins.

---

# Disclaimer

This project is intended for educational and research purposes only.

It is **not** financial advice and should not be interpreted as a recommendation to buy or sell any financial product.

Portfolio decisions should always consider an investor's financial circumstances, investment horizon, and risk tolerance.