import pytest
from hypothesis import given
from hypothesis.strategies import composite, integers

from flattrs import model_to_bytes
from flattrs.cflattrs.builder import Builder as CBuilder
from flatbuffers.builder import Builder

from ..test_trivial import just_a_strings


@composite
def builders(draw):
    size = draw(integers(0, 50000))
    return CBuilder(size), Builder(size)


@given(just_a_strings(), builders())
def test_just_a_strings(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)
