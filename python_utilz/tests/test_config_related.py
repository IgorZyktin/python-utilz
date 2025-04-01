"""Tests."""

from dataclasses import dataclass
from typing import Annotated
from typing import Any
from unittest import mock
from unittest.mock import patch

import pytest

from python_utilz.config_related import BaseConfig
from python_utilz.config_related import ConfigValidationError
from python_utilz.config_related import SecretStr
from python_utilz.config_related import from_env
from python_utilz.config_related import looks_like_boolean


def test_base_config_easy():
    """Must create config instance from env vars."""

    # arrange
    @dataclass
    class EasyConfig(BaseConfig):
        variable_1: int
        variable_2: str
        variable_3: bool = False

    # act
    with patch.dict(
        'os.environ',
        EASYCONFIG__VARIABLE_1='1',
        EASYCONFIG__VARIABLE_2='string',
    ):
        config = from_env(EasyConfig)

    # assert
    assert config.variable_1 == 1
    assert config.variable_2 == 'string'
    assert not config.variable_3


def test_base_config_skipped_unset():
    """Must fail to create because we have unset parameter."""
    # arrange
    output = mock.Mock()

    @dataclass
    class BadConfig(BaseConfig):
        _variable_0: int
        variable_1: int
        variable_2: str
        variable_3: bool = False

    # act
    with (
        patch.dict(
            'os.environ',
            BADCONFIG__VARIABLE_1='1',
            BADCONFIG__VARIABLE_2='string',
        ),
        pytest.raises(SystemExit),
    ):
        from_env(BadConfig, _output=output)

    # assert
    output.assert_has_calls(
        [
            mock.call(
                "Field '_variable_0' is supposed to have a default value"
            ),
        ]
    )


def test_base_config_skipped():
    """Must create config with skipped env variables."""
    # arrange
    output = mock.Mock()

    @dataclass
    class EasyConfig(BaseConfig):
        variable_1: int
        variable_2: str
        _variable_3: int = 0
        _variable_4: str = 'a'

    # act
    with patch.dict(
        'os.environ',
        EASYCONFIG__VARIABLE_1='1',
        EASYCONFIG__VARIABLE_2='string',
    ):
        config = from_env(EasyConfig, _output=output)

    # assert
    assert config.variable_1 == 1
    assert config.variable_2 == 'string'
    assert config._variable_3 == 0
    assert config._variable_4 == 'a'


def test_base_config_medium():
    """Must create config instance from env vars."""

    # arrange
    @dataclass
    class MediumConfig(BaseConfig):
        variable_1: Annotated[int, int]
        variable_2: Annotated[str, str.title]
        variable_3: Annotated[bool, looks_like_boolean]

    # act
    with patch.dict(
        'os.environ',
        MEDIUMCONFIG__VARIABLE_1='1',
        MEDIUMCONFIG__VARIABLE_2='string',
        MEDIUMCONFIG__VARIABLE_3='true',
    ):
        config = from_env(MediumConfig)

    # assert
    assert config.variable_1 == 1
    assert config.variable_2 == 'String'
    assert config.variable_3


def test_base_config_hard():
    """Must create config instance from env vars."""
    # arrange

    @dataclass
    class Database(BaseConfig):
        url: str
        timeout: int

    @dataclass
    class Email(BaseConfig):
        email: str
        retries: bool = False

    @dataclass
    class HardConfig(BaseConfig):
        variable_1: int
        email: Email
        database: Database

    # act
    with patch.dict(
        'os.environ',
        HARDCONFIG__VARIABLE_1='1',
        HARDCONFIG__EMAIL__EMAIL='john@snow.com',
        HARDCONFIG__DATABASE__URL='https://site.com',
        HARDCONFIG__DATABASE__TIMEOUT='1',
    ):
        config = from_env(HardConfig)

    # assert
    assert config.variable_1 == 1
    assert config.email.email == 'john@snow.com'
    assert config.database.url == 'https://site.com'
    assert config.database.timeout == 1


def test_base_config_union():
    """Must raise an exception."""
    # arrange
    output = mock.Mock()

    @dataclass
    class BadConfig(BaseConfig):
        variable_1: int | None
        variable_2: str

    # act + assert
    with pytest.raises(SystemExit):
        from_env(BadConfig, _output=output)

    output.assert_has_calls(
        [
            mock.call(
                'Config values are not supposed to be '
                'of Union type: variable_1: int | None'
            ),
            mock.call(
                "Environment variable 'BADCONFIG__VARIABLE_2' is not set"
            ),
        ]
    )


def test_secret_str_len():
    """Must use magic method of the object."""
    # arrange
    reference = 'hello world'

    # act
    target = SecretStr(reference)

    # assert
    assert len(reference) == len(target)


def test_secret_str_test_1():
    """Must use magic method of the object."""
    # arrange
    reference = 'hello world'

    # act
    target = SecretStr(reference)

    # assert
    assert str(target) == repr(target) != reference


def test_secret_str_test_2():
    """Must use magic method of the object."""
    # arrange
    reference = 'hello world'

    # act
    target = SecretStr(reference)

    # assert
    assert set(str(target)) == {'*'}


def test_secret_str_get():
    """Must use magic method of the object."""
    # arrange
    reference = 'hello world'

    # act
    target = SecretStr(reference)

    # assert
    assert target != reference
    assert target.get_secret_value() == reference


def test_base_config_wrong_type():
    """Must raise an exception."""
    # arrange
    output = mock.Mock()

    @dataclass
    class BadConfig(BaseConfig):
        variable_1: Annotated[str, int] = 'test'

    # act
    with pytest.raises(SystemExit):
        from_env(BadConfig, _output=output)

    # assert
    output.assert_has_calls(
        [
            mock.call(
                "Failed to convert 'variable_1' to type 'str', "
                'got ValueError: invalid literal for'
                " int() with base 10: 'test'"
            ),
        ]
    )


def test_base_config_wrong_logic():
    """Must raise an exception."""
    # arrange
    output = mock.Mock()

    def bigger_than_one(value: Any) -> Any:
        """Raise if we've got wrong value."""
        if int(value) <= 1:
            msg = 'Not bigger'
            raise ConfigValidationError(msg)

    @dataclass
    class BadConfig(BaseConfig):
        variable_1: Annotated[str, bigger_than_one]

    # act + assert
    with (
        patch.dict(
            'os.environ',
            BADCONFIG__VARIABLE_1='1',
        ),
        pytest.raises(ConfigValidationError, match='Not bigger'),
    ):
        from_env(BadConfig, _output=output)
