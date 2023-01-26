"""Misc tests for coverage."""
from enum import Enum

from pytest import raises

from flattr import flattrs


def test_unsupported_enums() -> None:
    class TestEnum(str, Enum):
        TEST = "test"

    with raises(TypeError):

        @flattrs
        class Test:
            test: TestEnum

    with raises(TypeError):

        @flattrs
        class Test:
            test: TestEnum | None

    with raises(TypeError):

        @flattrs
        class Test:
            test: list[TestEnum]

    with raises(TypeError):

        @flattrs
        class Test:
            test: list[TestEnum] | None
