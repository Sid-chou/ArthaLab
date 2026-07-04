"""Backtest engine tests."""

from datetime import date

import pandas as pd

from arthalab.domain.models import Cashflow, Portfolio, RebalancingPolicy
from arthalab.engines.backtest import run_backtest


def test_backtest_applies_cashflow_to_target_weights() -> None:
    """Cashflows should be allocated according to target weights."""
    dates = pd.date_range("2024-01-31", periods=3, freq="M")
    returns = pd.DataFrame({"equity": [0.0, 0.1, 0.0], "debt": [0.0, 0.0, 0.0]}, index=dates)
    portfolio = Portfolio("p", "P", target_allocation={"equity": 0.5, "debt": 0.5})
    cashflows = (Cashflow("c", 100.0, date(2024, 2, 15)),)
    result = run_backtest(portfolio, returns, cashflows, RebalancingPolicy("r"), 100.0)
    assert result.values.iloc[-1] > 200.0
    assert result.cashflows.sum() == 100.0
