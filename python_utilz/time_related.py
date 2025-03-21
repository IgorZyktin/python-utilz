"""Utilities that convert time."""

import datetime

__all__ = [
    'now',
]


def now() -> datetime.datetime:
    """Return current moment in time with timezone."""
    return datetime.datetime.now(tz=datetime.timezone.utc)
