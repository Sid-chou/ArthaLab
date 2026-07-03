"""Cashflow-aware historical backtest engine."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from arthalab.analytics.metrics import drawdown_series
from arthalab.domain.models import Cashflow, Portfolio, RebalanceFrequency, RebalancingPolicy
from arthalab.engines.cashflows import expand_cashflows


@dataclass(frozen=True)
class BacktestResult:
    """Historical backtest output."""

    portfolio_id: str
    values: pd.Series
    asset_values: pd.DataFrame
    allocation_drift: pd.DataFrame
    drawdowns: pd.Series
    cashflows: pd.Series


def run_backtest(
    portfolio: Portfolio,
    returns: pd.DataFrame,
    cashflows: tuple[Cashflow, ...],
    rebalancing: RebalancingPolicy,
    initial_value: float,
) -> BacktestResult:
    """Run a cashflow-aware historical backtest.

    Parameters
    ----------
    portfolio:
        Target portfolio allocation.
    returns:
        Periodic return matrix indexed by date.
    cashflows:
        Cashflow schedule.
    rebalancing:
        Rebalancing policy.
    initial_value:
        Starting portfolio value.

    Returns
    -------
    BacktestResult
        Value path, asset-level values, drift, drawdowns, and applied cashflows.
    """
    weights = pd.Series(portfolio.target_allocation, dtype=float)
    missing = set(weights.index) - set(returns.columns)
    if missing:
        raise ValueError(f"Return matrix missing portfolio assets: {sorted(missing)}")
    aligned_returns = returns.loc[:, list(weights.index)].copy()
    flow_series = expand_cashflows(cashflows, aligned_returns.index)

    asset_values = pd.DataFrame(index=aligned_returns.index, columns=weights.index, dtype=float)
    current = weights * float(initial_value)
    last_rebalance_year: int | None = None

    for idx, timestamp in enumerate(aligned_returns.index):
        if idx > 0:
            current = current * (1.0 + aligned_returns.iloc[idx])

        flow = float(flow_series.loc[timestamp])
        if flow != 0.0:
            if rebalancing.cashflow_rebalance:
                current = current + weights * flow
            else:
                current.iloc[0] += flow

        if _should_rebalance(timestamp, rebalancing.frequency, last_rebalance_year):
            total = float(current.sum())
            if total > 0:
                current = weights * total
            last_rebalance_year = timestamp.year

        asset_values.loc[timestamp] = current

    values = asset_values.sum(axis=1)
    drift = asset_values.div(values.replace(0, pd.NA), axis=0).fillna(0.0)
    return BacktestResult(
        portfolio_id=portfolio.portfolio_id,
        values=values,
        asset_values=asset_values,
        allocation_drift=drift,
        drawdowns=drawdown_series(values),
        cashflows=flow_series,
    )


def _should_rebalance(
    timestamp: pd.Timestamp,
    frequency: RebalanceFrequency,
    last_rebalance_year: int | None,
) -> bool:
    if frequency == RebalanceFrequency.NONE:
        return False
    if frequency == RebalanceFrequency.ANNUAL:
        return timestamp.month == 12 and last_rebalance_year != timestamp.year
    if frequency == RebalanceFrequency.MONTHLY:
        return True
    if frequency == RebalanceFrequency.QUARTERLY:
        return timestamp.month in {3, 6, 9, 12}
    if frequency == RebalanceFrequency.SEMIANNUAL:
        return timestamp.month in {6, 12}
    return False
