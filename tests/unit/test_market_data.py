"""Market data tests."""

from pathlib import Path

from arthalab.data.market_data import load_market_prices, prices_to_returns


def test_load_prices_and_build_returns() -> None:
    """Fixture prices should convert to a non-empty return matrix."""
    prices = load_market_prices(Path("tests/fixtures/market_prices.csv"))
    returns = prices_to_returns(prices, ["equity", "gold", "silver", "debt"])
    assert set(returns.columns) == {"equity", "gold", "silver", "debt"}
    assert not returns.empty
