"""Test serialization and deserialization of common tables."""
from flatbuffers.builder import Builder as CanonicalBuilder
from hypothesis import given
from hypothesis.strategies import composite, text, integers, none, lists

from flattrs import model_from_bytes, model_to_bytes

from .models import JustAString, JustAnOptionalString, ListOfStrings


@composite
def just_a_strings(draw):
    return JustAString(draw(text()))


@composite
def just_an_optional_strings(draw):
    return JustAnOptionalString(draw(text() | none()))


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


@given(lists_of_strings())
def test_lists_of_strings_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
