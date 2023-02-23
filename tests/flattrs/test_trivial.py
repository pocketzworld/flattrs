"""Test serialization and deserialization of common tables."""
from hypothesis import given
from hypothesis.strategies import binary, just, none, sampled_from, text, tuples

from flattrs import dumps, loads

from ..strats import float32s, float64s
from .models.enums import ASimpleByteEnum
from .models.trivial import (
    HasCaps,
    JustADouble,
    JustAFloat,
    JustAnEnum,
    JustAnOptionalString,
    JustAString,
    JustBytes,
    JustOptionalBytes,
)


@given(text().map(JustAString))
def test_just_a_string_rt(inst: JustAString) -> None:
    assert inst == loads(
        dumps(inst),
        inst.__class__,
    )


@given((text() | none()).map(JustAnOptionalString))
def test_just_an_optional_string_rt(inst: JustAnOptionalString) -> None:
    assert inst == loads(
        dumps(inst),
        inst.__class__,
    )


@given(binary().map(JustBytes))
def test_just_bytes_rt(inst: JustBytes) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given((binary() | just(None)).map(JustOptionalBytes))
def test_just_optional_bytes_rt(inst: JustOptionalBytes) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(float32s.map(JustAFloat))
def test_just_a_float_rt(inst: JustAFloat) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(float64s.map(JustADouble))
def test_just_a_double_rt(inst: JustADouble) -> None:
    assert inst == loads(dumps(inst), inst.__class__)


@given(sampled_from(ASimpleByteEnum).map(JustAnEnum))
def test_just_a_simple_byte_enum_rt(inst: JustAnEnum):
    assert inst == loads(dumps(inst), inst.__class__)


@given(tuples(text(), text(), text()).map(lambda t: HasCaps(*t)))
def test_has_caps(inst: HasCaps) -> None:
    assert inst == loads(dumps(inst), inst.__class__)
