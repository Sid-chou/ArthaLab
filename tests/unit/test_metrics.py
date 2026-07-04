"""Analytics tests."""

import numpy as np
import pandas as pd
import pytest

from arthalab.analytics.metrics import goal_outcome_from_terminal_values, max_drawdown


def test_max_drawdown() -> None:
    """Maximum drawdown should measure loss from peak."""
    values = pd.Series([100.0, 120.0, 90.0, 110.0])
    assert max_drawdown(values) == -0.25


def test_goal_outcome_from_terminal_values() -> None:
    """Goal outcome should calculate success and failure probabilities."""
    outcome = goal_outcome_from_terminal_values(np.array([90.0, 110.0, 130.0]), 100.0)
    assert outcome["success_probability"] == pytest.approx(2 / 3)
    assert outcome["failure_probability"] == pytest.approx(1 / 3)
