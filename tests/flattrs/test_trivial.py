"""Test serialization and deserialization of common tables."""
from struct import pack, unpack

from hypothesis import given
from hypothesis.strategies import (
    binary,
    composite,
    floats,
    just,
    lists,
    none,
    sampled_from,
    text,
)

from flattr import model_from_bytes, model_to_bytes

from ..strats import float32s, float64s
from .models_enums import ASimpleByteEnum

# from .models import (
#     JustADouble,
#     JustAFloat,
#     JustAnEnum,
#     JustAnOptionalString,
#     JustAString,
#     JustBytes,
#     JustOptionalBytes,
#     ListOfStrings,
# )
# from .models_enums import ASimpleByteEnum
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

# @composite
# def just_an_optional_strings(draw):
#     return JustAnOptionalString(draw(text() | none()))


# @composite
# def just_bytes(draw):
#     return JustBytes(draw(binary()))


# @composite
# def just_optional_bytes(draw):
#     return JustOptionalBytes(draw(binary() | none()))


# @composite
# def just_a_floats(draw):
#     return JustAFloat(unpack("f", pack("f", draw(floats(allow_nan=False))))[0])


# @composite
# def just_a_doubles(draw):
#     return JustADouble(draw(floats(allow_nan=False)))


# @composite
# def just_a_byte_enums(draw):
#     return JustAnEnum(draw(sampled_from(ASimpleByteEnum)))


# @composite
# def lists_of_strings(draw):
#     return ListOfStrings(draw(lists(text())))


@given(text().map(JustAString))
def test_just_a_string_rt(inst: JustAString) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given((text() | none()).map(JustAnOptionalString))
def test_just_an_optional_string_rt(inst: JustAnOptionalString) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(binary().map(JustBytes))
def test_just_bytes_rt(inst: JustBytes) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given((binary() | just(None)).map(JustOptionalBytes))
def test_just_optional_bytes_rt(inst: JustOptionalBytes) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(float32s.map(JustAFloat))
def test_just_a_float_rt(inst: JustAFloat) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(float64s.map(JustADouble))
def test_just_a_double_rt(inst: JustADouble) -> None:
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(sampled_from(ASimpleByteEnum).map(JustAnEnum))
def test_just_a_simple_byte_enum_rt(inst: JustAnEnum):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(text().map(lambda t: HasCaps(t, t)))
def test_has_caps(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
