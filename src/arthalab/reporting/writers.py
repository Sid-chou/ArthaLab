"""Markdown, CSV, and JSON report writers."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from arthalab.domain.models import AnalysisConfig, AnalysisResultBundle


def write_markdown_report(
    bundle: AnalysisResultBundle,
    config: AnalysisConfig,
    output_dir: str | Path,
) -> Path:
    """Write a Markdown research report.

    Parameters
    ----------
    bundle:
        Analysis result bundle.
    config:
        Analysis configuration.
    output_dir:
        Destination directory.

    Returns
    -------
    pathlib.Path
        Written report path.
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    report_path = path / f"{bundle.run_id}.md"
    comparison = pd.DataFrame(bundle.comparison_table)
    lines = [
        f"# ArthaLab Report: {config.goal.name}",
        "",
        "## Summary",
        bundle.report_sections.get("summary", ""),
        "",
        "## Goal",
        f"- Target date: {config.goal.target_date.isoformat()}",
        f"- Targets: {', '.join(f'INR {value:,.0f}' for value in config.goal.target_values)}",
        f"- Funding context: {config.goal.funding_context}",
        "",
        "## Portfolio Ranking",
        _markdown_table(comparison) if not comparison.empty else "No comparison rows.",
        "",
        "## Methodology",
        "Historical backtests and rolling windows use local data only. Results are research evidence, not financial advice.",
        "",
        "## Reproducibility",
        f"- Run ID: {bundle.run_id}",
        f"- Config hash: {bundle.config_hash}",
        f"- Data manifest: {bundle.data_manifest_id}",
        f"- Methodology version: {bundle.methodology_version}",
        "",
        "## Warnings",
    ]
    lines.extend(f"- {warning}" for warning in bundle.warnings)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def write_csv_reports(bundle: AnalysisResultBundle, output_dir: str | Path) -> dict[str, Path]:
    """Write normalized CSV reports."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}
    comparison_path = path / f"{bundle.run_id}_comparison.csv"
    pd.DataFrame(bundle.comparison_table).to_csv(comparison_path, index=False)
    outputs["comparison"] = comparison_path

    goal_path = path / f"{bundle.run_id}_goal_outcomes.csv"
    pd.DataFrame([asdict(item) for item in bundle.goal_results]).to_csv(goal_path, index=False)
    outputs["goal_outcomes"] = goal_path
    return outputs


def write_json_report(bundle: AnalysisResultBundle, output_dir: str | Path) -> Path:
    """Write the full result bundle as JSON."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    report_path = path / f"{bundle.run_id}.json"
    report_path.write_text(json.dumps(_jsonable(bundle), indent=2, sort_keys=True), encoding="utf-8")
    return report_path


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _markdown_table(frame: pd.DataFrame) -> str:
    """Render a Markdown table without optional pandas dependencies."""
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        values = [_format_markdown_value(row[column]) for column in frame.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _format_markdown_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
