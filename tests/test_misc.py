"""Misc tests for coverage."""
from enum import Enum

from attrs import define
from pytest import raises

from flattrs import dumps


def test_unsupported_enums() -> None:
    class TestEnum(str, Enum):
        TEST = "test"

    with raises(TypeError):

        @define
        class Test:
            test: TestEnum

        dumps(Test(TestEnum.TEST))

    with raises(TypeError):

        @define
        class Test:
            test: TestEnum | None

        dumps(Test(TestEnum.TEST))

    with raises(TypeError):

        @define
        class Test:
            test: list[TestEnum]

        dumps(Test([TestEnum.TEST]))

    with raises(TypeError):

        @define
        class Test:
            test: list[TestEnum] | None

        dumps(Test(TestEnum.TEST))
