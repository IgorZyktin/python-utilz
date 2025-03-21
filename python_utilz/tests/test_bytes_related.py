"""Tests."""

import pytest

from python_utilz.bytes_related import get_size

SELF_REFERENCE = [1, 2, 3]
SELF_REFERENCE.append(SELF_REFERENCE)


class Demo:
    """Empty class."""

    x: int = 1
    y: str = 2


@pytest.mark.parametrize(
    ('size', 'reference'),
    [
        (0, 24),
        (1, 28),
        (True, 28),
        (27, 28),
        ('test', 53),
        ([], 56),
        ([1, 2, 3], 172),
        ({}, 64),
        ({'key': [1, 2, 3]}, 456),
        (SELF_REFERENCE, 172),
        (Demo(), 152),
    ],
)
def test_get_size(size, reference):
    """Must return correct object size."""
    assert get_size(size) == reference
