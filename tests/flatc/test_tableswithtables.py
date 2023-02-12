from hypothesis import given
from hypothesis.strategies import DrawFn, composite, none

from tests import model_from_bytes, model_to_bytes

from .models_tableswithtables import ContainsTable, OptionalTable
from .test_common import common1s


@composite
def contains_tables(draw: DrawFn):
    return ContainsTable(draw(common1s()))


optional_tables = (common1s() | none()).map(OptionalTable)


@given(contains_tables())
def test_contains_tables(inst: ContainsTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(optional_tables)
def test_optional_tables(inst: OptionalTable) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
