from hypothesis import given
from hypothesis.strategies import composite

from flattr import model_from_bytes, model_to_bytes

from .models_tableswithtables import ContainsTable
from .test_common import common1s


@composite
def contains_tables(draw):
    return ContainsTable(draw(common1s()))


@given(contains_tables())
def test_contains_tables(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
