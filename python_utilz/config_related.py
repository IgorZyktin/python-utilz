"""Simple config class, when you do no need full size pydantic."""

from collections.abc import Callable
from dataclasses import MISSING
from dataclasses import Field
from dataclasses import dataclass
from dataclasses import fields
import os
import sys
import types
from typing import Annotated
from typing import Any
from typing import TypeVar
from typing import get_args
from typing import get_origin

from python_utilz.strings_related import exc_to_str

__all__ = [
    'BaseConfig',
    'ConfigValidationError',
    'EnvAlias',
    'SecretStr',
    'from_env',
    'looks_like_boolean',
]


@dataclass
class BaseConfig:
    """Configuration base class."""


class ConfigValidationError(Exception):
    """Failed to cast attribute to expected type."""


class SecretStr:
    """String that does not show its value."""

    def __init__(self, secret_value: str) -> None:
        """Initialize instance."""
        self._secret_value = secret_value

    def get_secret_value(self) -> str:
        """Return secret value."""
        return self._secret_value

    def __len__(self) -> int:
        """Return number of symbols."""
        return len(self._secret_value)

    def __str__(self) -> str:
        """Return string representation."""
        return '**********' if self.get_secret_value() else ''

    def __repr__(self) -> str:
        """Return string representation."""
        return self.__str__()


class EnvAlias:
    """Alternative name or names of environment variable for a field.

    Alias is expected to be the rightmost element in Annotated hint.
    """

    def __init__(self, *names: str) -> None:
        """Initialize instance."""
        self.names = names

    def __call__(self, value: str | None) -> str | None:
        """Do nothing, juts return."""
        return value

    def find_matching(self, env_name: str) -> tuple[str | None, str | None]:
        """Try getting value via another name."""
        for name in self.names:
            value = os.environ.get(name)

            if value is not None:
                return value, None

        variables = ', '.join(map(repr, (env_name, *self.names)))
        return (
            None,
            f'None of expected environment variables are set: {variables}',
        )


T_co = TypeVar('T_co', bound=BaseConfig, covariant=True)


def looks_like_boolean(value: str) -> bool:
    """Return True if value looks like boolean."""
    return value.lower() == 'true'


def _is_excluded(field: Field, field_exclude_prefix: str) -> bool:
    """Return true if this field is excluded from env vars."""
    return bool(
        field_exclude_prefix and field.name.startswith(field_exclude_prefix)
    )


def _has_no_default(field: Field) -> str | None:
    """Return error message if field expects a value."""
    if field.default is MISSING:
        return f'Field {field.name!r} is supposed to have a default value'
    return None


def _is_union(field: Field) -> str | None:
    """Return error message if field is a Union type."""
    if isinstance(field.type, types.UnionType):
        return (
            f'Config values are not supposed '
            f'to be of Union type: {field.name}: {field.type}'
        )
    return None


def from_env(  # noqa: C901, PLR0912, PLR0915
    model_type: type[T_co],
    *,
    env_prefix: str = '',
    env_separator: str = '__',
    field_exclude_prefix: str = '_',
    output: Callable = print,
    _prefixes: tuple[str, ...] | None = None,
    _terminate: Callable = lambda: sys.exit(1),
) -> T_co:
    """Build instance from environment variables."""
    errors: list[str] = []
    attributes: dict[str, Any] = {}

    if _prefixes is None:
        env_prefix = env_prefix or model_type.__name__.upper()
        _prefixes = _prefixes or (env_prefix, env_separator)

    for field in fields(model_type):
        if _is_excluded(field, field_exclude_prefix):
            msg = _has_no_default(field)
            if msg:
                errors.append(msg)
            continue

        msg = _is_union(field)
        if msg:
            errors.append(msg)
            continue

        if get_origin(field.type) is Annotated:
            expected_type, *casting_callables = get_args(field.type)
        else:
            expected_type = field.type
            casting_callables = [field.type]

        if issubclass(expected_type, BaseConfig):
            value = from_env(
                model_type=expected_type,
                env_prefix='',
                field_exclude_prefix=field_exclude_prefix,
                output=output,
                _prefixes=(*_prefixes, field.name.upper(), env_separator),
                _terminate=_terminate,
            )
            casting_callables.pop()

        else:
            prefix = ''.join(_prefixes)
            env_name = f'{prefix}{field.name}'.upper()
            value = os.environ.get(env_name)

            if value is None and field.default is not MISSING:
                # using default without data casting
                value = field.default
                casting_callables = []

            if value is None and isinstance(casting_callables[-1], EnvAlias):
                value, msg = casting_callables[-1].find_matching(env_name)

                if msg:
                    errors.append(msg)
                    continue

            if value is None:
                msg = f'Environment variable {env_name!r} is not set'
                errors.append(msg)
                continue

        final_value = value
        for _callable in casting_callables:
            try:
                final_value = _callable(final_value)
            except ConfigValidationError as exc:
                errors.append(str(exc))
                break
            except Exception as exc:
                msg = (
                    f'Failed to convert {field.name!r} '
                    f'to type {expected_type.__name__!r}, '
                    f'got {exc_to_str(exc)}'
                )
                errors.append(msg)
                break

        attributes[field.name] = final_value

    if errors:
        for error in errors:
            output(error)
        _terminate()

    return model_type(**attributes)
