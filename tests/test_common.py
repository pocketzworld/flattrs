"""Test serialization and deserialization of common tables."""
from flatbuffers.builder import Builder as CanonicalBuilder
from hypothesis import given
from hypothesis.strategies import composite, text, integers

from flattr import model_from_bytes, model_to_bytes

from .models import Common1
from .strats import uint8s, int32s


@composite
def common1s(draw):
    return Common1(draw(text()), draw(uint8s), draw(int32s))


@given(common1s())
def test_common1(inst):
    assert inst == model_from_bytes(inst.__class__, model_to_bytes(inst))
