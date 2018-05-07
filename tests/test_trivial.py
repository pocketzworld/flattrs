"""Test serialization and deserialization of common tables."""
from flatbuffers.builder import Builder as CanonicalBuilder
from hypothesis import given
from hypothesis.strategies import composite, text, integers

from flattrs import model_from_bytes, model_to_bytes

from .models import JustAString


@composite
def just_a_strings(draw):
    return JustAString(draw(text()))


@given(just_a_strings())
def test_just_a_string_rt(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
