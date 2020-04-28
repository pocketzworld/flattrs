"""Test serialization and deserialization of common tables."""
from hypothesis import given
from hypothesis.strategies import booleans, composite, text

from flattr import model_from_bytes, model_to_bytes

from .models_common import Common1, AllScalars, AllScalarsWithDefaults
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


@composite
def common1s(draw):
    return Common1(draw(text()), draw(uint8s), draw(int32s))


@composite
def all_scalars(draw):
    return AllScalars(
        draw(booleans()),
        draw(uint8s),
        draw(uint16s),
        draw(uint32s),
        draw(uint64s),
        draw(int8s),
        draw(int16s),
        draw(int32s),
        draw(int64s),
        draw(float32s),
        draw(float64s),
    )


@composite
def all_scalars_with_defaults(draw):
    return AllScalarsWithDefaults(
        draw(booleans()),
        draw(uint8s),
        draw(uint16s),
        draw(uint32s),
        draw(uint64s),
        draw(int8s),
        draw(int16s),
        draw(int32s),
        draw(int64s),
        draw(float32s),
        draw(float64s),
    )


@given(common1s())
def test_common1(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(common1s())
def test_common1_repr(inst):
    """Common1 has an overriden repr."""
    assert repr(inst) == f"{inst.id}:{inst.aSmallInt}:{inst.aBigInt}"


@given(all_scalars())
def test_all_scalars(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(all_scalars_with_defaults())
def test_all_scalars_with_defaults(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
