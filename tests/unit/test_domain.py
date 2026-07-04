"""Domain model tests."""

import pytest

from arthalab.domain.models import Portfolio, ValidationError


def test_portfolio_rejects_weights_that_do_not_sum_to_one() -> None:
    """Portfolio allocation must sum to one."""
    with pytest.raises(ValidationError):
        Portfolio("bad", "Bad", target_allocation={"equity": 0.7, "gold": 0.2})


def test_portfolio_rejects_unsupported_asset_class() -> None:
    """Unsupported asset classes are not allowed in Phase 1."""
    with pytest.raises(ValidationError):
        Portfolio("bad", "Bad", target_allocation={"equity": 0.8, "bitcoin": 0.2})
