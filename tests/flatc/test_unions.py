from hypothesis import given
from hypothesis.strategies import booleans, composite, text

from flattr import model_from_bytes, model_to_bytes

from .models_nested import NestedJustAString
from .models_unions import UnionOfNestedTables, UnionOfOptionalTables
from .test_common import common1s


@composite
def unions_of_nested_tables(draw):
    if draw(booleans()):
        inner = draw(common1s())
    else:
        inner = NestedJustAString(draw(text()))
    return UnionOfNestedTables(inner)


@composite
def unions_of_optional_tables(draw):
    if draw(booleans()):
        inner = draw(common1s())
    else:
        if draw(booleans()):
            inner = NestedJustAString(draw(text()))
        else:
            inner = None
    return UnionOfOptionalTables(inner)


@given(unions_of_nested_tables())
def test_unions_of_nested_tables(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(unions_of_optional_tables())
def test_unions_of_optional_tables(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
