"""Test serialization and deserialization of common tables."""
from struct import pack, unpack
from flatbuffers.builder import Builder as CanonicalBuilder
from hypothesis import given
from hypothesis.strategies import (
    composite,
    text,
    integers,
    none,
    lists,
    floats,
)

from flattrs import model_from_bytes, model_to_bytes

from .models import (
    JustAString,
    JustAnOptionalString,
    JustAFloat,
    JustADouble,
    ListOfStrings,
)


@composite
def just_a_strings(draw):
    return JustAString(draw(text()))


@composite
def just_an_optional_strings(draw):
    return JustAnOptionalString(draw(text() | none()))


@composite
def just_a_floats(draw):
    return JustAFloat(unpack("f", pack("f", draw(floats(allow_nan=False))))[0])


@composite
def just_a_doubles(draw):
    return JustADouble(draw(floats(allow_nan=False)))


@composite
def lists_of_strings(draw):
    return ListOfStrings(draw(lists(text())))


@given(just_a_strings())
def test_just_a_string_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_an_optional_strings())
def test_just_an_optional_string_rt(inst):
    # Remove then we update Flatbuffers.
    if not inst.id:
        inst.id = None
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_a_floats())
def test_just_a_float_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(just_a_doubles())
def test_just_a_double_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))


@given(lists_of_strings())
def test_lists_of_strings_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
