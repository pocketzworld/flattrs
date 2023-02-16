from hypothesis import given
from hypothesis.strategies import none, text

from flattr import dumps, loads

from .models.nested.nested_trivial import NestedJustAString
from .models.tableswithtables import (
    NumberedUnionTable,
    UnionOfNestedTables,
    UnionOfOptionalTables,
)
from .test_common import all_scalars, all_scalars_with_defaults, common1s

unions_of_nested_tables = (common1s | text().map(NestedJustAString)).map(
    UnionOfNestedTables
)
unions_of_optional_tables = (common1s | none()).map(UnionOfOptionalTables)
numbered_union_tables = (
    none() | common1s | all_scalars() | all_scalars_with_defaults()
).map(NumberedUnionTable)


@given(unions_of_nested_tables)
def test_unions_of_nested_tables(inst: UnionOfNestedTables) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(unions_of_optional_tables)
def test_unions_of_optional_tables(inst: UnionOfOptionalTables) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(numbered_union_tables)
def test_unions_of_numbered_unions(inst: NumberedUnionTable) -> None:
    assert inst == loads(dumps(inst), inst.__class__)
