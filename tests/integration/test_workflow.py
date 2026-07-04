"""End-to-end workflow tests."""

from pathlib import Path

from arthalab.workflows import run_analysis


def test_run_analysis_writes_artifacts(tmp_path: Path) -> None:
    """The MVP workflow should write Markdown, CSV, and JSON artifacts."""
    bundle = run_analysis("configs/wedding_mvp.yaml", output_root=tmp_path, rolling_window_periods=12)
    assert len(bundle.comparison_table) == 3
    assert bundle.comparison_table[0]["rank"] == 1
    assert Path(bundle.artifact_paths["markdown"]).exists()
    assert Path(bundle.artifact_paths["csv_comparison"]).exists()
    assert Path(bundle.artifact_paths["json"]).exists()
