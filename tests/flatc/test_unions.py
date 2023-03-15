from hypothesis import given
from hypothesis.strategies import DrawFn, booleans, composite, none, sampled_from, text

from tests import model_from_bytes, model_to_bytes

from .models_nested import NestedJustAString
from .models_unions import (
    NumberedUnionTable,
    SingleClassUnionRequiredTable,
    SingleClassUnionTable,
    UnionOfNestedTables,
    UnionOfOptionalTables,
)
from .test_common import all_scalars, all_scalars_with_defaults, common1s


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


@composite
def numbered_union_tables(draw: DrawFn) -> NumberedUnionTable:
    which = draw(sampled_from([0, 1, 2, 3]))
    if which == 0:
        inner = None
    elif which == 1:
        inner = draw(common1s())
    elif which == 2:
        inner = draw(all_scalars())
    else:
        inner = draw(all_scalars_with_defaults())
    return NumberedUnionTable(inner)


@given(unions_of_nested_tables())
def test_unions_of_nested_tables(inst: UnionOfNestedTables) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(unions_of_optional_tables())
def test_unions_of_optional_tables(inst) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(numbered_union_tables())
def test_unions_of_numbered_unions(inst: NumberedUnionTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


single_class_unions = (common1s() | none()).map(SingleClassUnionTable)


@given(single_class_unions)
def test_single_class_unions(inst: SingleClassUnionTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(common1s().map(SingleClassUnionRequiredTable))
def test_single_class_required_unions(inst: SingleClassUnionRequiredTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
