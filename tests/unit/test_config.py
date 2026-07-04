"""Configuration tests."""

from pathlib import Path

from arthalab.config.loader import load_analysis_config


def test_load_analysis_config() -> None:
    """YAML config should load into validated domain objects."""
    config = load_analysis_config(Path("configs/wedding_mvp.yaml"))
    assert config.goal.goal_id == "wedding_2030"
    assert len(config.portfolios) == 3
    assert config.portfolios[0].target_allocation["gold"] == 0.30
