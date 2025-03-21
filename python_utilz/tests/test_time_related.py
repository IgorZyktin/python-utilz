"""Tests."""

from python_utilz.time_related import now


def test_now():
    """Must return datetime with UTC timestamp."""
    assert now().tzname() == 'UTC'
