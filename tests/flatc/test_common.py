"""Test serialization and deserialization of common tables."""
from hypothesis import given
from hypothesis.strategies import booleans, composite, lists, text, tuples

from tests import model_from_bytes, model_to_bytes

from ..strats import (
    float32s,
    float64s,
    int8s,
    int16s,
    int32s,
    int64s,
    uint8s,
    uint16s,
    uint32s,
    uint64s,
)
from .models_common import AllScalars, AllScalarsWithDefaults, Common1, Common2


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


common_2s = tuples(lists(text()), text()).map(lambda t: Common2(*t))


@given(common1s())
def test_common1(inst: Common1) -> None:
    restruct = model_from_bytes(inst.__class__, model_to_bytes(inst))
    assert inst == restruct
    assert isinstance(restruct.aSmallInt, int)


@given(common_2s)
def test_common2(inst: Common2) -> None:
    restruct = model_from_bytes(inst.__class__, model_to_bytes(inst))
    assert inst == restruct


@given(all_scalars())
def test_all_scalars(inst: AllScalars) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(all_scalars_with_defaults())
def test_all_scalars_with_defaults(inst: AllScalarsWithDefaults) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
