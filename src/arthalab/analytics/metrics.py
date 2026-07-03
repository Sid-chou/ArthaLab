"""Deterministic portfolio analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def drawdown_series(values: pd.Series) -> pd.Series:
    """Calculate drawdown from a portfolio value path.

    Parameters
    ----------
    values:
        Portfolio value path indexed by date.

    Returns
    -------
    pandas.Series
        Drawdown series where zero is the high-water mark and negative values
        are percentage losses from peak.
    """
    if values.empty:
        return values.copy()
    peaks = values.cummax()
    return values / peaks - 1.0


def max_drawdown(values: pd.Series) -> float:
    """Return maximum drawdown for a value path."""
    if values.empty:
        return 0.0
    return float(drawdown_series(values).min())


def annualized_return(values: pd.Series, periods_per_year: int = 12) -> float:
    """Calculate annualized return from a portfolio value path."""
    if len(values) < 2 or values.iloc[0] <= 0:
        return 0.0
    years = (len(values) - 1) / periods_per_year
    if years <= 0:
        return 0.0
    return float((values.iloc[-1] / values.iloc[0]) ** (1.0 / years) - 1.0)


def annualized_volatility(returns: pd.Series, periods_per_year: int = 12) -> float:
    """Calculate annualized volatility from periodic returns."""
    if len(returns) < 2:
        return 0.0
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def downside_deviation(
    returns: pd.Series,
    minimum_acceptable_return: float = 0.0,
    periods_per_year: int = 12,
) -> float:
    """Calculate annualized downside deviation."""
    downside = returns[returns < minimum_acceptable_return] - minimum_acceptable_return
    if downside.empty:
        return 0.0
    return float(np.sqrt(np.mean(np.square(downside))) * np.sqrt(periods_per_year))


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 12,
) -> float:
    """Calculate annualized Sharpe ratio."""
    volatility = annualized_volatility(returns, periods_per_year)
    if volatility == 0:
        return 0.0
    excess_annual_return = float(returns.mean() * periods_per_year - risk_free_rate)
    return excess_annual_return / volatility


def sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 12,
) -> float:
    """Calculate annualized Sortino ratio."""
    downside = downside_deviation(returns, risk_free_rate / periods_per_year, periods_per_year)
    if downside == 0:
        return 0.0
    excess_annual_return = float(returns.mean() * periods_per_year - risk_free_rate)
    return excess_annual_return / downside


def calmar_ratio(values: pd.Series, periods_per_year: int = 12) -> float:
    """Calculate Calmar ratio."""
    drawdown = abs(max_drawdown(values))
    if drawdown == 0:
        return 0.0
    return annualized_return(values, periods_per_year) / drawdown


def var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical value at risk as a positive loss number."""
    if returns.empty:
        return 0.0
    return float(max(0.0, -np.quantile(returns.to_numpy(), 1.0 - confidence)))


def cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical conditional value at risk as a positive loss number."""
    if returns.empty:
        return 0.0
    threshold = np.quantile(returns.to_numpy(), 1.0 - confidence)
    tail = returns[returns <= threshold]
    if tail.empty:
        return 0.0
    return float(max(0.0, -tail.mean()))


def goal_outcome_from_terminal_values(
    terminal_values: np.ndarray,
    target_value: float,
) -> dict[str, float]:
    """Summarize goal outcomes for a target value.

    Parameters
    ----------
    terminal_values:
        Array of terminal portfolio values.
    target_value:
        Goal corpus target.

    Returns
    -------
    dict[str, float]
        Goal outcome metrics.
    """
    if terminal_values.size == 0:
        raise ValueError("terminal_values cannot be empty.")
    success = terminal_values >= target_value
    shortfalls = np.maximum(target_value - terminal_values, 0.0)
    return {
        "success_probability": float(success.mean()),
        "failure_probability": float(1.0 - success.mean()),
        "median_outcome": float(np.median(terminal_values)),
        "best_outcome": float(np.quantile(terminal_values, 0.95)),
        "worst_outcome": float(np.quantile(terminal_values, 0.05)),
        "shortfall_at_risk": float(np.quantile(shortfalls, 0.95)),
    }
