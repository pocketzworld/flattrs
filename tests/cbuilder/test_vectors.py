from hypothesis import given
from hypothesis.strategies import DrawFn, composite, lists

from flattr import model_to_bytes

from ..flatc.models_vectors import VectorsOfFloats, VectorsOfInts
from ..flatc.test_vectors import (
    float32s,
    float64s,
    int8s,
    int16s,
    int32s,
    int64s,
    vectors_of_bools,
    vectors_of_common1s,
    vectors_of_scalars,
)
from . import builders


@composite
def vectors_of_ints(draw: DrawFn):
    return VectorsOfInts(
        draw(lists(int8s)),
        draw(lists(int16s)),
        draw(lists(int32s)),
        draw(lists(int64s)),
    )


@composite
def vectors_of_floats(draw: DrawFn):
    return VectorsOfFloats(
        draw(lists(float32s)),
        draw(lists(float64s)),
    )


@given(vectors_of_bools(), builders())
def test_vectors_of_bools(inst, builders):
    cbuilder, builder = builders
    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(vectors_of_ints(), builders())
def test_vectors_of_ints(inst, builders):
    cbuilder, builder = builders
    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(vectors_of_floats(), builders())
def test_vectors_of_floats(inst, builders):
    cbuilder, builder = builders
    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(vectors_of_scalars(), builders())
def test_vectors_of_scalars(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(vectors_of_common1s(), builders())
def test_vectors_of_common1s(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)
