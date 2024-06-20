from enum import auto

import graphene
import pytest

from common.utils import graphene_enum_values


class TestGrapheneEnum(graphene.Enum):
    FIRST_ENUM_NAME = "FIRST_ENUM_VALUE"
    ENUM_NAME_1 = "ENUM_VALUE_1"
    ENUM_NAME_2 = "ENUM_VALUE_2"
    LAST_ENUM_NAME = "LAST_ENUM_VALUE"


class TestGrapheneEnumAuto(graphene.Enum):
    _123 = auto()
    test = auto()


@pytest.mark.parametrize(
    "enum_class,expected_values",
    [
        (
            TestGrapheneEnum,
            ["FIRST_ENUM_VALUE", "ENUM_VALUE_1", "ENUM_VALUE_2", "LAST_ENUM_VALUE"],
        ),
        (TestGrapheneEnumAuto, [1, 2]),
    ],
)
def test_graphene_enum_values(enum_class, expected_values):
    assert graphene_enum_values(enum_class) == expected_values
