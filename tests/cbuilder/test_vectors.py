from hypothesis import given

from flattr import model_to_bytes

from ..test_vectors import vectors_of_scalars, vectors_of_common1s

from . import builders


@given(vectors_of_scalars(), builders())
def test_vectors_of_scalars(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(vectors_of_common1s(), builders())
def test_vectors_of_common1s(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)
