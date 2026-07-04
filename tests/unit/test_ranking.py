"""Ranking tests."""

from arthalab.optimization.ranking import rank_portfolios


def test_rank_portfolios_prioritizes_goal_probability() -> None:
    """Goal success probability should dominate CAGR."""
    rows = [
        {"portfolio_id": "a", "min_success_probability": 0.7, "max_failure_probability": 0.3, "max_drawdown": -0.2, "cagr": 0.2},
        {"portfolio_id": "b", "min_success_probability": 0.9, "max_failure_probability": 0.1, "max_drawdown": -0.3, "cagr": 0.1},
    ]
    ranked = rank_portfolios(rows)
    assert ranked[0]["portfolio_id"] == "b"
    assert ranked[0]["rank"] == 1
