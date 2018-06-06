from hypothesis import given

from flattr import model_to_bytes

from ..test_common import all_scalars, all_scalars_with_defaults

from . import builders


@given(all_scalars(), builders())
def test_all_scalars(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(all_scalars_with_defaults(), builders())
def test_all_scalars_with_defaults(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)
