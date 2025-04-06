"""Simple config class, when you do no need full size pydantic."""

from collections.abc import Callable
from dataclasses import MISSING
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


T_co = TypeVar('T_co', bound=BaseConfig, covariant=True)


def looks_like_boolean(value: str) -> bool:
    """Return True if value looks like boolean."""
    return value.lower() == 'true'


def from_env(  # noqa: C901, PLR0912
    model_type: type[T_co],
    *,
    env_prefix: str = '',
    env_separator: str = '__',
    field_exclude_prefix: str = '_',
    output: Callable = print,
    _prefixes: tuple[str, ...] | None = None,
) -> T_co:
    """Build instance from environment variables."""
    errors: list[str] = []
    attributes: dict[str, Any] = {}

    if _prefixes is None:
        env_prefix = env_prefix or model_type.__name__.upper()
        _prefixes = _prefixes or (env_prefix, env_separator)

    for field in fields(model_type):
        if field_exclude_prefix and field.name.startswith(
            field_exclude_prefix
        ):
            if field.default is MISSING:
                msg = (
                    f'Field {field.name!r} is supposed to have a default value'
                )
                errors.append(msg)
            continue

        check_nested = True
        if get_origin(field.type) is Annotated:
            expected_type, *casting_callables = get_args(field.type)
        elif isinstance(field.type, types.UnionType):
            msg = (
                f'Config values are not supposed '
                f'to be of Union type: {field.name}: {field.type}'
            )
            errors.append(msg)
            continue
        else:
            expected_type = field.type
            casting_callables = [field.type]

        if check_nested and issubclass(expected_type, BaseConfig):
            value = from_env(
                model_type=expected_type,
                env_prefix='',
                field_exclude_prefix=field_exclude_prefix,
                output=output,
                _prefixes=(*_prefixes, field.name.upper(), env_separator),
            )
            casting_callables.pop()

        else:
            prefix = ''.join(_prefixes)
            env_name = f'{prefix}{field.name}'.upper()
            default = None if field.default is MISSING else field.default
            value = os.environ.get(env_name, default)

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
        sys.exit(1)

    return model_type(**attributes)
