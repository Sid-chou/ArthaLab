"""Rolling-window analysis engine."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from arthalab.analytics.metrics import annualized_return, annualized_volatility, max_drawdown, sharpe_ratio
from arthalab.domain.models import Cashflow, Portfolio, RebalancingPolicy
from arthalab.engines.backtest import run_backtest


@dataclass(frozen=True)
class RollingResult:
    """Rolling-window result for one portfolio."""

    portfolio_id: str
    windows: pd.DataFrame


def run_rolling_windows(
    portfolio: Portfolio,
    returns: pd.DataFrame,
    cashflows: tuple[Cashflow, ...],
    rebalancing: RebalancingPolicy,
    initial_value: float,
    window_periods: int = 36,
    periods_per_year: int = 12,
    risk_free_rate: float = 0.0,
) -> RollingResult:
    """Run rolling-window portfolio analysis.

    Parameters
    ----------
    portfolio:
        Portfolio to evaluate.
    returns:
        Return matrix.
    cashflows:
        Cashflow schedule.
    rebalancing:
        Rebalancing policy.
    initial_value:
        Starting value in each rolling window.
    window_periods:
        Number of periods per window.
    periods_per_year:
        Return periods per year.
    risk_free_rate:
        Annual risk-free rate.

    Returns
    -------
    RollingResult
        Rolling metrics by start and end date.
    """
    rows: list[dict[str, object]] = []
    if len(returns) < window_periods:
        return RollingResult(portfolio.portfolio_id, pd.DataFrame(rows))

    for start in range(0, len(returns) - window_periods + 1):
        window = returns.iloc[start : start + window_periods]
        result = run_backtest(portfolio, window, cashflows, rebalancing, initial_value)
        path_returns = result.values.pct_change().dropna()
        rows.append(
            {
                "start_date": window.index[0],
                "end_date": window.index[-1],
                "cagr": annualized_return(result.values, periods_per_year),
                "volatility": annualized_volatility(path_returns, periods_per_year),
                "sharpe": sharpe_ratio(path_returns, risk_free_rate, periods_per_year),
                "max_drawdown": max_drawdown(result.values),
                "terminal_value": float(result.values.iloc[-1]),
            }
        )
    return RollingResult(portfolio.portfolio_id, pd.DataFrame(rows))
