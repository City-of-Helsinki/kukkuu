import enum
from enum import auto

import graphene
import pytest

from common.utils import is_enum_value, safe_test_and_get_enum_value


class _TestEnum(enum.Enum):
    TEST = "test_1"
    TEST_2 = 2


class _TestGrapheneEnum(graphene.Enum):
    FIRST_ENUM_NAME = "FIRST_ENUM_VALUE"
    ENUM_NAME_1 = "ENUM_VALUE_1"
    ENUM_NAME_2 = "ENUM_VALUE_2"
    LAST_ENUM_NAME = "LAST_ENUM_VALUE"


class _TestGrapheneEnumAuto(graphene.Enum):
    _123 = auto()
    test = auto()


@pytest.mark.parametrize(
    "value",
    [
        _TestEnum.TEST,
        _TestEnum.TEST_2,
        _TestGrapheneEnum.FIRST_ENUM_NAME,
        _TestGrapheneEnum.ENUM_NAME_1,
        _TestGrapheneEnum.ENUM_NAME_2,
        _TestGrapheneEnum.LAST_ENUM_NAME,
        _TestGrapheneEnumAuto._123,
        _TestGrapheneEnumAuto.test,
    ],
)
def test_is_enum_value_true(value):
    assert is_enum_value(value) is True


@pytest.mark.parametrize(
    "value",
    [
        None,
        0,
        1,
        2,
        "0",
        "1",
        "2",
        "FIRST_ENUM_VALUE",
        "ENUM_VALUE_1",
        "ENUM_VALUE_2",
        "LAST_ENUM_VALUE",
    ],
)
def test_is_enum_value_false(value):
    assert is_enum_value(value) is False


@pytest.mark.parametrize(
    "input",
    [
        None,
        0,
        1,
        2,
        "0",
        "1",
        "2",
        "FIRST_ENUM_VALUE",
        "ENUM_VALUE_1",
        "ENUM_VALUE_2",
        "LAST_ENUM_VALUE",
        {1, 2, 3, "test", 2},
        (1, 2, 3, "test", 2),
        [1, 2, 3, "test", 2],
        (1, [2, {3: {4, (11, (12,), 13, None, "test")}}]),
    ],
)
def test_safe_test_and_get_enum_value_unchanged(input):
    assert safe_test_and_get_enum_value(input) == input


@pytest.mark.parametrize(
    "input,expected_output",
    [
        (_TestEnum.TEST, "test_1"),
        (_TestEnum.TEST_2, 2),
        (_TestGrapheneEnum.FIRST_ENUM_NAME, "FIRST_ENUM_VALUE"),
        (_TestGrapheneEnum.ENUM_NAME_1, "ENUM_VALUE_1"),
        (_TestGrapheneEnum.ENUM_NAME_2, "ENUM_VALUE_2"),
        (_TestGrapheneEnum.LAST_ENUM_NAME, "LAST_ENUM_VALUE"),
        (_TestGrapheneEnumAuto._123, 1),
        (_TestGrapheneEnumAuto.test, 2),
    ],
)
def test_safe_test_and_get_enum_value_changed(input, expected_output):
    assert safe_test_and_get_enum_value(input) == expected_output
