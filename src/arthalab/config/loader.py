"""YAML configuration loader for ArthaLab."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from arthalab.domain.models import (
    AnalysisConfig,
    AssumptionSet,
    Cashflow,
    Frequency,
    Goal,
    Holding,
    Portfolio,
    RebalanceFrequency,
    RebalancingPolicy,
)


def load_analysis_config(path: str | Path) -> AnalysisConfig:
    """Load an analysis configuration from YAML.

    Parameters
    ----------
    path:
        YAML file path.

    Returns
    -------
    AnalysisConfig
        Validated analysis configuration.
    """
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ValueError("Config file must contain a mapping.")
    return parse_analysis_config(raw, base_dir=config_path.parent)


def parse_analysis_config(raw: dict[str, Any], base_dir: Path | None = None) -> AnalysisConfig:
    """Parse a raw mapping into an analysis config.

    Parameters
    ----------
    raw:
        Raw configuration mapping.
    base_dir:
        Directory used to resolve relative data paths.

    Returns
    -------
    AnalysisConfig
        Validated domain configuration.
    """
    goal_raw = raw["goal"]
    assumptions_raw = raw.get("assumptions", {})
    rebalancing_raw = raw.get("rebalancing", {})
    data_path = str(raw["data_path"])
    if base_dir is not None and not Path(data_path).is_absolute():
        data_path = str((base_dir / data_path).resolve())

    holdings = tuple(_parse_holding(item) for item in raw.get("current_holdings", []))
    portfolios = tuple(_parse_portfolio(item, holdings) for item in raw["portfolios"])
    return AnalysisConfig(
        config_id=str(raw.get("config_id", _config_id(raw))),
        version=str(raw.get("version", "1")),
        goal=Goal(
            goal_id=str(goal_raw["goal_id"]),
            goal_type=str(goal_raw["goal_type"]),
            name=str(goal_raw["name"]),
            start_date=_date(goal_raw["start_date"]),
            target_date=_date(goal_raw["target_date"]),
            target_values=tuple(float(value) for value in goal_raw["target_values"]),
            inflation_rate=float(goal_raw.get("inflation_rate", assumptions_raw.get("inflation_rate", 0.06))),
            priority=goal_raw.get("priority"),
            funding_context=str(goal_raw.get("funding_context", "")),
        ),
        portfolios=portfolios,
        cashflows=tuple(_parse_cashflow(item) for item in raw.get("cashflows", [])),
        rebalancing=RebalancingPolicy(
            rebalance_policy_id=str(rebalancing_raw.get("rebalance_policy_id", "default")),
            frequency=RebalanceFrequency(str(rebalancing_raw.get("frequency", "annual"))),
            threshold=_optional_float(rebalancing_raw.get("threshold")),
            cashflow_rebalance=bool(rebalancing_raw.get("cashflow_rebalance", True)),
            goal_glidepath=rebalancing_raw.get("goal_glidepath"),
        ),
        assumptions=AssumptionSet(
            assumption_set_id=str(assumptions_raw.get("assumption_set_id", "default")),
            inflation_rate=float(assumptions_raw.get("inflation_rate", 0.06)),
            risk_free_rate=float(assumptions_raw.get("risk_free_rate", 0.06)),
            benchmark_id=str(assumptions_raw.get("benchmark_id", "nifty_tri")),
            tax_policy=str(assumptions_raw.get("tax_policy", "ignored_phase_1")),
            return_frequency=str(assumptions_raw.get("return_frequency", "monthly")),
            random_seed=int(assumptions_raw.get("random_seed", 42)),
            simulation_count=int(assumptions_raw.get("simulation_count", 1_000)),
            methodology_version=str(assumptions_raw.get("methodology_version", "mvp-1")),
        ),
        data_path=data_path,
        report_outputs=tuple(raw.get("report_outputs", ["markdown", "csv", "json"])),
        analysis_modules=tuple(raw.get("analysis_modules", ["backtest", "rolling"])),
    )


def config_hash(path: str | Path) -> str:
    """Return a stable SHA-256 hash for a config file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _parse_holding(raw: dict[str, Any]) -> Holding:
    return Holding(
        holding_id=str(raw["holding_id"]),
        asset_id=str(raw["asset_id"]),
        asset_class_id=str(raw["asset_class_id"]),
        instrument_name=str(raw["instrument_name"]),
        current_value=float(raw.get("current_value", 0.0)),
        allocation_weight=float(raw["allocation_weight"]),
        xirr=_optional_float(raw.get("xirr")),
        as_of_date=_optional_date(raw.get("as_of_date")),
    )


def _parse_portfolio(raw: dict[str, Any], holdings: tuple[Holding, ...]) -> Portfolio:
    portfolio_holdings = holdings if raw.get("use_current_holdings", False) else ()
    return Portfolio(
        portfolio_id=str(raw["portfolio_id"]),
        name=str(raw["name"]),
        description=str(raw.get("description", "")),
        base_currency=str(raw.get("base_currency", "INR")),
        holdings=portfolio_holdings,
        target_allocation={str(key): float(value) for key, value in raw["target_allocation"].items()},
        rebalance_policy_id=raw.get("rebalance_policy_id"),
        created_from=str(raw.get("created_from", "config")),
    )


def _parse_cashflow(raw: dict[str, Any]) -> Cashflow:
    return Cashflow(
        cashflow_id=str(raw["cashflow_id"]),
        amount=float(raw["amount"]),
        date=_date(raw["date"]),
        frequency=Frequency(str(raw.get("frequency", "one_time"))),
        portfolio_id=raw.get("portfolio_id"),
        allocation_rule=str(raw.get("allocation_rule", "target")),
        source=str(raw.get("source", "manual")),
        end_date=_optional_date(raw.get("end_date")),
    )


def _date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _optional_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    return _date(value)


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _config_id(raw: dict[str, Any]) -> str:
    text = yaml.safe_dump(raw, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
