"""Goal-aware scenario ranking."""

from __future__ import annotations

from typing import Any


def rank_portfolios(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank portfolio comparison rows by MVP objective priority.

    Parameters
    ----------
    rows:
        Comparison rows containing goal and risk metrics.

    Returns
    -------
    list[dict[str, Any]]
        Rows with one-based ``rank`` assigned.
    """
    ranked = sorted(
        rows,
        key=lambda row: (
            -float(row.get("min_success_probability", 0.0)),
            float(row.get("max_failure_probability", 1.0)),
            abs(float(row.get("max_drawdown", 0.0))),
            -float(row.get("median_terminal_value", 0.0)),
            -float(row.get("sharpe", 0.0)),
            -float(row.get("cagr", 0.0)),
        ),
    )
    return [dict(row, rank=index + 1) for index, row in enumerate(ranked)]
