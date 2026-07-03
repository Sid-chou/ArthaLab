"""Offline market data loading utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class MarketDataError(ValueError):
    """Raised when local market data is invalid."""


REQUIRED_COLUMNS = {
    "date",
    "asset_id",
    "value",
    "currency",
    "source",
    "return_type",
    "quality_flag",
}


def load_market_prices(path: str | Path) -> pd.DataFrame:
    """Load and validate local market price data.

    Parameters
    ----------
    path:
        CSV path containing the market price dataset.

    Returns
    -------
    pandas.DataFrame
        Validated price data sorted by asset and date.
    """
    csv_path = Path(path)
    if not csv_path.exists():
        raise MarketDataError(f"Market data file does not exist: {csv_path}")
    data = pd.read_csv(csv_path, parse_dates=["date"])
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise MarketDataError(f"Market data missing columns: {sorted(missing)}")
    if data[["date", "asset_id"]].duplicated().any():
        raise MarketDataError("Market data contains duplicate date/asset_id rows.")
    if (data["value"] <= 0).any():
        raise MarketDataError("Market data values must be positive.")
    if data["date"].isna().any():
        raise MarketDataError("Market data contains invalid dates.")
    return data.sort_values(["asset_id", "date"]).reset_index(drop=True)


def prices_to_returns(
    prices: pd.DataFrame,
    asset_ids: list[str],
    alignment_policy: str = "inner",
) -> pd.DataFrame:
    """Convert long-form price data into an asset return matrix.

    Parameters
    ----------
    prices:
        Validated long-form price data.
    asset_ids:
        Required asset identifiers.
    alignment_policy:
        Date alignment policy. The MVP supports ``"inner"`` and ``"ffill"``.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by date with asset return columns.
    """
    missing_assets = set(asset_ids) - set(prices["asset_id"].unique())
    if missing_assets:
        raise MarketDataError(f"Missing market data for assets: {sorted(missing_assets)}")
    filtered = prices[prices["asset_id"].isin(asset_ids)]
    wide = filtered.pivot(index="date", columns="asset_id", values="value").sort_index()
    if alignment_policy == "inner":
        wide = wide.dropna()
    elif alignment_policy == "ffill":
        wide = wide.ffill().dropna()
    else:
        raise MarketDataError(f"Unsupported alignment_policy: {alignment_policy}")
    returns = wide.pct_change().dropna()
    if returns.empty:
        raise MarketDataError("Return matrix is empty after pct_change.")
    return returns
