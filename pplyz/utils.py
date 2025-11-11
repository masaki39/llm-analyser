"""Shared utility helpers for logging and retry logic."""

from __future__ import annotations

from typing import Sequence


def format_error_message(error: Exception | str, limit: int = 400) -> str:
    """Trim error output to avoid flooding logs with large payloads."""
    message = str(error).strip()
    if len(message) > limit:
        message = message[:limit] + "... (truncated)"
    if not message and isinstance(error, Exception):
        return error.__class__.__name__
    return message


def max_retry_attempts(schedule: Sequence[float]) -> int:
    """Return total attempts including the initial try."""
    return len(schedule) + 1
