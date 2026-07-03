"""End-to-end MVP analysis workflow."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from arthalab.analytics.metrics import (
    annualized_return,
    annualized_volatility,
    calmar_ratio,
    cvar,
    goal_outcome_from_terminal_values,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
    var,
)
from arthalab.config.loader import config_hash, load_analysis_config
from arthalab.data.market_data import load_market_prices, prices_to_returns
from arthalab.domain.models import AnalysisConfig, AnalysisResultBundle, GoalOutcome, PortfolioResult
from arthalab.engines.backtest import run_backtest
from arthalab.engines.rolling import run_rolling_windows
from arthalab.optimization.ranking import rank_portfolios
from arthalab.reporting.writers import write_csv_reports, write_json_report, write_markdown_report

LOGGER = logging.getLogger(__name__)


def run_analysis(
    config_path: str | Path,
    output_root: str | Path = "reports",
    rolling_window_periods: int = 36,
) -> AnalysisResultBundle:
    """Run the complete MVP analysis workflow.

    Parameters
    ----------
    config_path:
        YAML configuration path.
    output_root:
        Root directory for report artifacts.
    rolling_window_periods:
        Number of periods in each rolling window.

    Returns
    -------
    AnalysisResultBundle
        Complete analysis result bundle.
    """
    config = load_analysis_config(config_path)
    run_id = _run_id(config)
    LOGGER.info("analysis_started", extra={"extra": {"run_id": run_id, "config_id": config.config_id}})

    prices = load_market_prices(config.data_path)
    asset_ids = sorted({asset for portfolio in config.portfolios for asset in portfolio.target_allocation})
    returns = prices_to_returns(prices, asset_ids)
    initial_value = _initial_value(config)
    data_manifest_id = _data_manifest(prices)

    portfolio_results: list[PortfolioResult] = []
    comparison_rows: list[dict[str, Any]] = []
    goal_outcomes: list[GoalOutcome] = []
    chart_specs: dict[str, Any] = {"growth": {}, "drawdown": {}, "allocation_drift": {}, "rolling": {}}
    warnings: list[str] = []

    periods_per_year = 12 if config.assumptions.return_frequency == "monthly" else 252
    for portfolio in config.portfolios:
        backtest = run_backtest(portfolio, returns, config.cashflows, config.rebalancing, initial_value)
        path_returns = backtest.values.pct_change().dropna()
        rolling = run_rolling_windows(
            portfolio,
            returns,
            config.cashflows,
            config.rebalancing,
            initial_value,
            window_periods=min(rolling_window_periods, len(returns)),
            periods_per_year=periods_per_year,
            risk_free_rate=config.assumptions.risk_free_rate,
        )
        metrics = _portfolio_metrics(
            backtest.values,
            path_returns,
            periods_per_year,
            config.assumptions.risk_free_rate,
        )
        terminal_values = _terminal_distribution(backtest.values, rolling.windows)
        outcomes = tuple(
            _goal_outcome(run_id, portfolio.portfolio_id, target, terminal_values)
            for target in config.goal.target_values
        )
        goal_outcomes.extend(outcomes)
        portfolio_results.append(PortfolioResult(portfolio.portfolio_id, metrics, outcomes))

        row = _comparison_row(portfolio.portfolio_id, portfolio.name, metrics, outcomes, rolling.windows)
        comparison_rows.append(row)
        chart_specs["growth"][portfolio.portfolio_id] = _series_spec(backtest.values)
        chart_specs["drawdown"][portfolio.portfolio_id] = _series_spec(backtest.drawdowns)
        chart_specs["allocation_drift"][portfolio.portfolio_id] = _frame_spec(backtest.allocation_drift)
        chart_specs["rolling"][portfolio.portfolio_id] = _frame_spec(rolling.windows)

    ranked_rows = rank_portfolios(comparison_rows)
    summary = _summary(ranked_rows)
    bundle = AnalysisResultBundle(
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        config_hash=config_hash(config_path),
        data_manifest_id=data_manifest_id,
        methodology_version=config.assumptions.methodology_version,
        portfolio_results=tuple(portfolio_results),
        comparison_table=ranked_rows,
        goal_results=tuple(goal_outcomes),
        chart_specs=chart_specs,
        report_sections={"summary": summary},
        warnings=tuple(warnings),
    )
    artifact_paths = _write_reports(bundle, config, output_root)
    LOGGER.info("analysis_completed", extra={"extra": {"run_id": run_id, "artifacts": artifact_paths}})
    return replace(bundle, artifact_paths=artifact_paths)


def _portfolio_metrics(
    values: pd.Series,
    returns: pd.Series,
    periods_per_year: int,
    risk_free_rate: float,
) -> dict[str, float]:
    return {
        "terminal_value": float(values.iloc[-1]),
        "cagr": annualized_return(values, periods_per_year),
        "volatility": annualized_volatility(returns, periods_per_year),
        "max_drawdown": max_drawdown(values),
        "sharpe": sharpe_ratio(returns, risk_free_rate, periods_per_year),
        "sortino": sortino_ratio(returns, risk_free_rate, periods_per_year),
        "calmar": calmar_ratio(values, periods_per_year),
        "var_95": var(returns, 0.95),
        "cvar_95": cvar(returns, 0.95),
    }


def _goal_outcome(
    run_id: str,
    portfolio_id: str,
    target: float,
    terminal_values: np.ndarray,
) -> GoalOutcome:
    raw = goal_outcome_from_terminal_values(terminal_values, target)
    return GoalOutcome(
        run_id=run_id,
        portfolio_id=portfolio_id,
        target_value=target,
        success_probability=raw["success_probability"],
        failure_probability=raw["failure_probability"],
        median_outcome=raw["median_outcome"],
        best_outcome=raw["best_outcome"],
        worst_outcome=raw["worst_outcome"],
        shortfall_at_risk=raw["shortfall_at_risk"],
    )


def _comparison_row(
    portfolio_id: str,
    name: str,
    metrics: dict[str, float],
    outcomes: tuple[GoalOutcome, ...],
    rolling_windows: pd.DataFrame,
) -> dict[str, Any]:
    success_probabilities = [item.success_probability for item in outcomes]
    failure_probabilities = [item.failure_probability for item in outcomes]
    row: dict[str, Any] = {
        "portfolio_id": portfolio_id,
        "name": name,
        "terminal_value": metrics["terminal_value"],
        "median_terminal_value": float(np.median([item.median_outcome for item in outcomes])),
        "min_success_probability": min(success_probabilities),
        "max_failure_probability": max(failure_probabilities),
        "max_drawdown": metrics["max_drawdown"],
        "cagr": metrics["cagr"],
        "volatility": metrics["volatility"],
        "sharpe": metrics["sharpe"],
        "sortino": metrics["sortino"],
        "calmar": metrics["calmar"],
    }
    if not rolling_windows.empty:
        row["worst_rolling_terminal_value"] = float(rolling_windows["terminal_value"].min())
        row["worst_rolling_drawdown"] = float(rolling_windows["max_drawdown"].min())
    return row


def _terminal_distribution(values: pd.Series, rolling_windows: pd.DataFrame) -> np.ndarray:
    terminals = [float(values.iloc[-1])]
    if not rolling_windows.empty:
        terminals.extend(float(item) for item in rolling_windows["terminal_value"].to_numpy())
    return np.asarray(terminals, dtype=float)


def _initial_value(config: AnalysisConfig) -> float:
    holding_value = sum(holding.current_value for portfolio in config.portfolios for holding in portfolio.holdings)
    if holding_value > 0:
        return float(holding_value)
    return 1_000_000.0


def _run_id(config: AnalysisConfig) -> str:
    text = f"{config.config_id}:{config.version}:{config.assumptions.methodology_version}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _data_manifest(prices: pd.DataFrame) -> str:
    payload = "|".join(
        [
            str(prices["date"].min()),
            str(prices["date"].max()),
            ",".join(sorted(prices["asset_id"].unique())),
            str(len(prices)),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def _series_spec(series: pd.Series) -> list[dict[str, Any]]:
    return [{"date": index.date().isoformat(), "value": float(value)} for index, value in series.items()]


def _frame_spec(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in frame.iterrows():
        item = {column: _scalar(value) for column, value in row.items()}
        if isinstance(index, pd.Timestamp):
            item["date"] = index.date().isoformat()
        rows.append(item)
    return rows


def _scalar(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def _summary(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No portfolios were evaluated."
    best = rows[0]
    return (
        f"Top-ranked scenario is {best['name']} based on goal probability, "
        f"failure probability, drawdown control, and risk-adjusted metrics."
    )


def _write_reports(
    bundle: AnalysisResultBundle,
    config: AnalysisConfig,
    output_root: str | Path,
) -> dict[str, str]:
    root = Path(output_root)
    artifacts: dict[str, str] = {}
    if "markdown" in config.report_outputs:
        artifacts["markdown"] = str(write_markdown_report(bundle, config, root / "markdown"))
    if "csv" in config.report_outputs:
        artifacts.update({f"csv_{key}": str(value) for key, value in write_csv_reports(bundle, root / "csv").items()})
    if "json" in config.report_outputs:
        artifacts["json"] = str(write_json_report(bundle, root / "json"))
    return artifacts
