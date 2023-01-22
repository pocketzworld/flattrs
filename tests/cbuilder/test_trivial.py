from hypothesis import given

from flattr import model_to_bytes

from ..flatc.test_trivial import just_a_doubles, just_a_floats, just_a_strings
from ..flatc.test_vectors import vectors_of_strings
from . import builders


@given(just_a_strings(), builders())
def test_just_a_strings(inst, builders):
    cbuilder, builder = builders

    assert model_to_bytes(inst, cbuilder) == model_to_bytes(inst, builder)


@given(vectors_of_strings, builders())
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
