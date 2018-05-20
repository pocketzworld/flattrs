import pytest
from hypothesis import given
from hypothesis.strategies import composite, integers

from flattr import model_to_bytes
from flattr.cflattr.builder import Builder as CBuilder
from flatbuffers.builder import Builder

from ..test_trivial import (
    just_a_strings,
    just_a_floats,
    just_a_doubles,
    lists_of_strings,
)


@composite
def builders(draw):
    size = draw(integers(0, 50000))
    return CBuilder(size), Builder(size)


@given(just_a_strings(), builders())
def test_just_a_strings(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(lists_of_strings(), builders())
def test_list_of_strings(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(just_a_floats(), builders())
def test_just_a_floats(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(just_a_doubles(), builders())
def test_just_a_doubles(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)
