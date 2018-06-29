from hypothesis import given
from hypothesis.strategies import booleans, composite, lists
from flattr import model_from_bytes, model_to_bytes

from .models_vectors import VectorsOfScalars, VectorOfCommon1
from .strats import (
    uint8s,
    uint16s,
    uint32s,
    uint64s,
    int8s,
    int16s,
    int32s,
    int64s,
    float32s,
    float64s,
)
from .test_common import common1s


@composite
def vectors_of_scalars(draw):
    return VectorsOfScalars(
        draw(lists(booleans())),
        draw(lists(uint8s)),
        draw(lists(uint16s)),
        draw(lists(uint32s)),
        draw(lists(uint64s)),
        draw(lists(int8s)),
        draw(lists(int16s)),
        draw(lists(int32s)),
        draw(lists(int64s)),
        draw(lists(float32s)),
        draw(lists(float64s)),
    )


@composite
def vectors_of_common1s(draw):
    return VectorOfCommon1(draw(lists(common1s())))


@given(vectors_of_scalars())
def test_vectors_of_scalars_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(vectors_of_common1s())
def test_vectors_of_common1s_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
