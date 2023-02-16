"""Test serialization and deserialization of common tables."""
from struct import pack, unpack

from hypothesis import given
from hypothesis.strategies import (
    binary,
    composite,
    floats,
    lists,
    none,
    sampled_from,
    text,
)

from tests import model_from_bytes, model_to_bytes

from .models_enums import ASimpleByteEnum
from .models_trivial import (
    HasCaps,
    JustADouble,
    JustAFloat,
    JustAnEnum,
    JustAnOptionalString,
    JustAString,
    JustBytes,
    JustOptionalBytes,
)


@composite
def just_a_strings(draw):
    return JustAString(draw(text()))


@composite
def just_an_optional_strings(draw):
    return JustAnOptionalString(draw(text() | none()))


@composite
def just_bytes(draw):
    return JustBytes(draw(binary()))


@composite
def just_optional_bytes(draw):
    return JustOptionalBytes(draw(binary() | none()))


@composite
def just_a_floats(draw):
    return JustAFloat(unpack("f", pack("f", draw(floats(allow_nan=False))))[0])


@composite
def just_a_doubles(draw):
    return JustADouble(draw(floats(allow_nan=False)))


@composite
def just_a_byte_enums(draw):
    return JustAnEnum(draw(sampled_from(ASimpleByteEnum)))


@given(just_a_strings())
def test_just_a_string_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_an_optional_strings())
def test_just_an_optional_string_rt(inst):
    # Remove then we update Flatbuffers.
    if not inst.id:
        inst.id = None
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_bytes())
def test_just_bytes_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_optional_bytes())
def test_just_optional_bytes_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_a_floats())
def test_just_a_float_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_a_doubles())
def test_just_a_double_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_a_byte_enums())
def test_just_a_simple_byte_enum_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(text().map(lambda t: HasCaps(t, t, t)))
def test_has_caps(inst: HasCaps) -> bool:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
