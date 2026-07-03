"""Core domain models for ArthaLab.

The domain layer intentionally contains no file-system, plotting, or network
logic. It defines the financial objects and validation rules shared by the
MVP workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any


class ValidationError(ValueError):
    """Raised when a domain object violates ArthaLab invariants."""


class Frequency(StrEnum):
    """Supported time frequencies."""

    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    DAILY = "daily"


class RebalanceFrequency(StrEnum):
    """Supported rebalancing frequencies."""

    NONE = "none"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"


SUPPORTED_ASSET_CLASSES = {
    "equity",
    "gold",
    "silver",
    "debt",
    "liquid_funds",
    "cash",
}


@dataclass(frozen=True)
class AssetClass:
    """Investable category used for allocation decisions."""

    asset_class_id: str
    name: str
    currency: str = "INR"
    risk_category: str = ""
    liquidity_profile: str = ""
    data_source: str = ""
    benchmark_id: str | None = None
    is_supported: bool = True


@dataclass(frozen=True)
class Asset:
    """Historical return series or proxy used for analysis."""

    asset_id: str
    asset_class_id: str
    name: str
    source: str
    frequency: str
    return_type: str
    start_date: date | None = None
    end_date: date | None = None
    currency: str = "INR"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Holding:
    """Current portfolio holding."""

    holding_id: str
    asset_id: str
    asset_class_id: str
    instrument_name: str
    current_value: float
    allocation_weight: float
    xirr: float | None = None
    as_of_date: date | None = None

    def __post_init__(self) -> None:
        """Validate holding values."""
        if self.current_value < 0:
            raise ValidationError("Holding current_value cannot be negative.")
        if self.allocation_weight < 0:
            raise ValidationError("Holding allocation_weight cannot be negative.")


@dataclass(frozen=True)
class Portfolio:
    """Current holdings or target asset-class allocation."""

    portfolio_id: str
    name: str
    description: str = ""
    base_currency: str = "INR"
    holdings: tuple[Holding, ...] = ()
    target_allocation: dict[str, float] = field(default_factory=dict)
    rebalance_policy_id: str | None = None
    created_from: str = "manual"

    def __post_init__(self) -> None:
        """Validate portfolio allocation."""
        if self.target_allocation:
            validate_weights(self.target_allocation)
            unsupported = set(self.target_allocation) - SUPPORTED_ASSET_CLASSES
            if unsupported:
                raise ValidationError(f"Unsupported asset classes: {sorted(unsupported)}")

    @property
    def initial_value(self) -> float:
        """Total current value represented by holdings."""
        return float(sum(holding.current_value for holding in self.holdings))


@dataclass(frozen=True)
class Goal:
    """Investment objective."""

    goal_id: str
    goal_type: str
    name: str
    start_date: date
    target_date: date
    target_values: tuple[float, ...]
    inflation_rate: float = 0.06
    priority: int | None = None
    funding_context: str = ""

    def __post_init__(self) -> None:
        """Validate goal dates and targets."""
        if self.target_date <= self.start_date:
            raise ValidationError("Goal target_date must be after start_date.")
        if not self.target_values or any(value <= 0 for value in self.target_values):
            raise ValidationError("Goal target_values must be positive.")


@dataclass(frozen=True)
class Cashflow:
    """Contribution or withdrawal schedule item."""

    cashflow_id: str
    amount: float
    date: date
    frequency: Frequency = Frequency.ONE_TIME
    portfolio_id: str | None = None
    allocation_rule: str = "target"
    source: str = "manual"
    end_date: date | None = None


@dataclass(frozen=True)
class RebalancingPolicy:
    """Portfolio rebalancing rule."""

    rebalance_policy_id: str
    frequency: RebalanceFrequency = RebalanceFrequency.ANNUAL
    threshold: float | None = None
    cashflow_rebalance: bool = True
    goal_glidepath: str | None = None


@dataclass(frozen=True)
class AssumptionSet:
    """Reproducibility-critical assumptions."""

    assumption_set_id: str
    inflation_rate: float = 0.06
    risk_free_rate: float = 0.06
    benchmark_id: str = "nifty_tri"
    tax_policy: str = "ignored_phase_1"
    return_frequency: str = "monthly"
    random_seed: int = 42
    simulation_count: int = 1_000
    methodology_version: str = "mvp-1"


@dataclass(frozen=True)
class AnalysisConfig:
    """Validated input for a full analysis run."""

    config_id: str
    version: str
    goal: Goal
    portfolios: tuple[Portfolio, ...]
    cashflows: tuple[Cashflow, ...]
    rebalancing: RebalancingPolicy
    assumptions: AssumptionSet
    data_path: str
    report_outputs: tuple[str, ...] = ("markdown", "csv", "json")
    analysis_modules: tuple[str, ...] = ("backtest", "rolling")


@dataclass(frozen=True)
class Metric:
    """Normalized metric value."""

    run_id: str
    portfolio_id: str
    metric_name: str
    metric_value: float
    unit: str
    methodology_version: str
    period_start: date | None = None
    period_end: date | None = None


@dataclass(frozen=True)
class GoalOutcome:
    """Target-specific success and failure metrics."""

    run_id: str
    portfolio_id: str
    target_value: float
    success_probability: float
    failure_probability: float
    median_outcome: float
    best_outcome: float
    worst_outcome: float
    shortfall_at_risk: float | None = None


@dataclass(frozen=True)
class PortfolioResult:
    """Analysis output for one portfolio."""

    portfolio_id: str
    metrics: dict[str, float]
    goal_outcomes: tuple[GoalOutcome, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class AnalysisResultBundle:
    """Canonical output from an analysis workflow."""

    run_id: str
    created_at: str
    config_hash: str
    data_manifest_id: str
    methodology_version: str
    portfolio_results: tuple[PortfolioResult, ...]
    comparison_table: list[dict[str, Any]]
    goal_results: tuple[GoalOutcome, ...]
    chart_specs: dict[str, Any]
    report_sections: dict[str, str]
    warnings: tuple[str, ...]
    artifact_paths: dict[str, str] = field(default_factory=dict)


def validate_weights(weights: dict[str, float], tolerance: float = 1e-6) -> None:
    """Validate long-only weights that sum to one.

    Parameters
    ----------
    weights:
        Mapping from asset class identifier to decimal weight.
    tolerance:
        Absolute tolerance for the sum-to-one check.

    Raises
    ------
    ValidationError
        If any weight is negative or the total is not one.
    """
    if not weights:
        raise ValidationError("Portfolio target_allocation cannot be empty.")
    if any(weight < 0 for weight in weights.values()):
        raise ValidationError("Portfolio weights must be long-only.")
    total = sum(weights.values())
    if abs(total - 1.0) > tolerance:
        raise ValidationError(f"Portfolio weights must sum to 1.0, got {total:.8f}.")
