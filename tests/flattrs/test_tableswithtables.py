from hypothesis import given
from hypothesis.strategies import DrawFn, booleans, composite, none

from flattr import dumps, loads

from .models.tableswithtables import ContainsTable, OptionalTable
from .test_common import common1s

contains_tables = common1s.map(ContainsTable)


optional_tables = (common1s | none()).map(OptionalTable)


@given(contains_tables)
def test_contains_tables(inst: ContainsTable) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(optional_tables)
def test_optional_tables(inst: OptionalTable) -> None:
    assert inst == loads(dumps(inst), inst.__class__)
