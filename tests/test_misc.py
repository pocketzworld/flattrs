"""Misc tests for coverage."""
from enum import Enum

from attrs import define
from pytest import raises

from flattrs import dumps, make_dumps, make_loads

from .flattrs.models.common import Common1


def test_unsupported_enums() -> None:
    """Unsupported enums throw errors."""

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


def test_make_fns() -> None:
    """flattrs.make_* work properly."""
    dumps = make_dumps(Common1)
    loads = make_loads(Common1)
    assert loads(dumps(i := Common1("id", 1, 2))) == i
