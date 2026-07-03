"""Structured logging helpers for ArthaLab."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format log records as compact JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record.

        Parameters
        ----------
        record:
            Standard Python log record.

        Returns
        -------
        str
            JSON encoded log line.
        """
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra", None)
        if isinstance(extra, Mapping):
            payload.update(extra)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, sort_keys=True)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging with JSON output.

    Parameters
    ----------
    level:
        Root logging level.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
