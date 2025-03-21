"""Utilities that convert something from or to bytes."""

import sys
from typing import Any

__all__ = [
    'get_size',
]


def get_size(obj: Any, seen: set[int] | None = None) -> int:
    """Return recursively calculated size of object."""
    size = sys.getsizeof(obj)

    if seen is None:
        seen = set()

    obj_id = id(obj)

    if obj_id in seen:
        return 0

    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum(get_size(v, seen) for v in obj.values())
        size += sum(get_size(k, seen) for k in obj)

    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)

    elif hasattr(obj, '__iter__') and not isinstance(
        obj, (str | bytes | bytearray)
    ):
        size += sum(get_size(i, seen) for i in obj)

    return size
