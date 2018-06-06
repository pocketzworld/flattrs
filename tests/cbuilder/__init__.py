from hypothesis.strategies import composite, integers

from flatbuffers.builder import Builder
from flattr.cflattr.builder import Builder as CBuilder


@composite
def builders(draw):
    size = draw(integers(0, 50000))
    return CBuilder(size), Builder(size)
