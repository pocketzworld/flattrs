from flatbuffers.builder import Builder
from hypothesis.strategies import composite, integers

from flattrs.cflattrs.builder import Builder as CBuilder


@composite
def builders(draw):
    size = draw(integers(0, 50000))
    return CBuilder(size), Builder(size)
