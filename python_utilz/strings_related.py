"""Utilities that convert something from or to string."""

import math
import re
from uuid import UUID

__all__ = [
    'exc_to_str',
    'hsize',
    'htime',
    'human_readable_size',
    'human_readable_time',
    'is_valid_uuid',
    'sep_digits',
]


def exc_to_str(exc: Exception) -> str:
    """Convert exception into readable string."""
    return f'{type(exc).__name__}: {exc}'


UUID_TEMPLATE = re.compile(
    '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
)


def is_valid_uuid(uuid: UUID | str) -> bool:
    """Return True if given object can be considered as UUID."""
    if isinstance(uuid, UUID):
        return True
    return UUID_TEMPLATE.match(uuid) is not None


def human_readable_time(seconds: float) -> str:
    """Format interval as human readable description.

    >>> human_readable_time(46551387)
    '76w 6d 18h 56m 27s'
    >>> human_readable_time(600)
    '10m'
    """
    if seconds < 1:
        return '0s'

    _weeks = 0
    _days = 0
    _hours = 0
    _minutes = 0
    _seconds = 0
    _suffixes = ('w', 'd', 'h', 'm', 's')

    if seconds > 0:
        _minutes, _seconds = divmod(int(round(seconds)), 60)  # noqa: RUF046
        _hours, _minutes = divmod(_minutes, 60)
        _days, _hours = divmod(_hours, 24)
        _weeks, _days = divmod(_days, 7)

    return ' '.join(
        f'{x}{_suffixes[i]}'
        for i, x in enumerate([_weeks, _days, _hours, _minutes, _seconds])
        if x
    )


# alias
htime = human_readable_time

SUFFIXES = {
    'RU': {
        'B': 'Б',
        'kB': 'кБ',
        'MB': 'МБ',
        'GB': 'ГБ',
        'TB': 'ТБ',
        'PB': 'ПБ',
        'EB': 'ЭБ',
        'KiB': 'КиБ',
        'MiB': 'МиБ',
        'GiB': 'ГиБ',
        'TiB': 'ТиБ',
        'PiB': 'ПиБ',
        'EiB': 'ЭиБ',
    },
    'EN': {
        'B': 'B',
        'kB': 'kB',
        'MB': 'MB',
        'GB': 'GB',
        'TB': 'TB',
        'PB': 'PB',
        'EB': 'EB',
        'KiB': 'KiB',
        'MiB': 'MiB',
        'GiB': 'GiB',
        'TiB': 'TiB',
        'PiB': 'PiB',
        'EiB': 'EiB',
    },
}


def human_readable_size(
    total_bytes: float,
    base: int = 1024,
    language: str = 'EN',
) -> str:
    """Convert amount of bytes into human-readable format.

    >>> human_readable_size(1023)
    '1023 B'
    """
    total_bytes = int(total_bytes)

    prefix = ''
    if total_bytes < 0:
        prefix = '-'
        total_bytes = abs(total_bytes)

    if total_bytes < base:
        suffix = SUFFIXES[language]['B']
        return f'{prefix}{int(total_bytes)} {suffix}'

    total_bytes /= base

    if total_bytes < base:
        suffix = SUFFIXES[language]['KiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    total_bytes /= base

    if total_bytes < base:
        suffix = SUFFIXES[language]['MiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    total_bytes /= base

    if total_bytes < base:
        suffix = SUFFIXES[language]['GiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    total_bytes /= base

    if total_bytes < base:
        suffix = SUFFIXES[language]['TiB']
        return f'{prefix}{total_bytes:0.1f} {suffix}'

    suffix = SUFFIXES[language]['EiB']
    return f'{total_bytes / base / base:0.1f} {suffix}'


# alias
hsize = human_readable_size


def sep_digits(number: float | str, precision: int = 2) -> str:
    """Return number as a string with separated thousands.

    >>> sep_digits('12345678')
    '12345678'
    >>> sep_digits(12345678)
    '12 345 678'
    >>> sep_digits(1234.5678)
    '1 234.57'
    >>> sep_digits(1234.5678, precision=4)
    '1 234.5678'
    """
    if isinstance(number, str):
        return number

    if isinstance(number, int):
        return f'{number:,}'.replace(',', ' ')

    if not precision:
        return f'{int(round(number)):,}'.replace(',', ' ')  # noqa: RUF046

    tail = number % 1
    return (
        f'{math.floor(number):,}'.replace(',', ' ')
        + ('{tail:0.' + str(precision) + 'f}').format(tail=tail)[1:]
    )
