from hypothesis import given

from flattr import model_to_bytes

from ..test_vectors import vectors_of_scalars

from . import builders


@given(vectors_of_scalars(), builders())
def test_vectors_of_scalars(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)
