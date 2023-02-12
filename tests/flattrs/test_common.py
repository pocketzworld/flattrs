"""Test serialization and deserialization of common tables."""
from hypothesis import given
from hypothesis.strategies import DrawFn, binary, booleans, composite, text, tuples

from flattr import dumps, loads

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
from .models.common import AllScalars, AllScalarsWithDefaults, Common1

common1s = tuples(text(), uint8s, int32s).map(lambda a: Common1(*a))


@given(common1s)
def test_common1(inst: Common1) -> None:
    restruct = loads(dumps(inst), inst.__class__)
    assert inst == restruct
    assert isinstance(restruct.aSmallInt, int)


@composite
def all_scalars(draw: DrawFn) -> AllScalars:
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
def all_scalars_with_defaults(draw: DrawFn) -> AllScalarsWithDefaults:
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


@given(all_scalars())
def test_all_scalars(inst: AllScalars) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(all_scalars_with_defaults())
def test_all_scalars_with_defaults(inst: AllScalarsWithDefaults) -> None:
    assert inst == loads(dumps(inst), inst.__class__)
