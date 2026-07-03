"""Cashflow schedule expansion."""

from __future__ import annotations

from datetime import date

import pandas as pd

from arthalab.domain.models import Cashflow, Frequency


def expand_cashflows(cashflows: tuple[Cashflow, ...], dates: pd.DatetimeIndex) -> pd.Series:
    """Expand scheduled cashflows onto an analysis date index.

    Parameters
    ----------
    cashflows:
        Cashflow schedule items.
    dates:
        Analysis dates. Cashflows are applied on the first analysis date on or
        after the scheduled date.

    Returns
    -------
    pandas.Series
        Cashflow amounts indexed by analysis date.
    """
    expanded = pd.Series(0.0, index=dates)
    for cashflow in cashflows:
        for scheduled_date in _scheduled_dates(cashflow, dates[-1].date()):
            target_date = _first_on_or_after(dates, scheduled_date)
            if target_date is not None:
                expanded.loc[target_date] += cashflow.amount
    return expanded


def _scheduled_dates(cashflow: Cashflow, max_date: date) -> list[date]:
    if cashflow.frequency == Frequency.ONE_TIME:
        return [cashflow.date]
    end = min(cashflow.end_date or max_date, max_date)
    if cashflow.frequency == Frequency.MONTHLY:
        freq = "M"
    elif cashflow.frequency == Frequency.QUARTERLY:
        freq = "Q"
    elif cashflow.frequency == Frequency.ANNUAL:
        freq = "A"
    else:
        raise ValueError(f"Unsupported cashflow frequency: {cashflow.frequency}")
    return [item.date() for item in pd.date_range(cashflow.date, end, freq=freq)]


def _first_on_or_after(dates: pd.DatetimeIndex, scheduled_date: date) -> pd.Timestamp | None:
    timestamp = pd.Timestamp(scheduled_date)
    eligible = dates[dates >= timestamp]
    if eligible.empty:
        return None
    return eligible[0]
