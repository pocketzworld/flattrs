from flattrs.cflattrs.builder import (
    writeBool,
    writeUint8,
    writeUint16,
    writeUint32,
    writeUint64,
    writeInt8,
    writeInt16,
    writeInt32,
    writeInt64,
    writeFloat32,
    writeFloat64,
)
from struct import Struct, pack, unpack

from hypothesis import given
from hypothesis.strategies import booleans, integers, floats


@given(booleans())
def test_bool(val):
    sut, oracle = writeUint8, Struct("?")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(0, (2 ** 8) - 1))
def test_uint8(val):
    sut, oracle = writeUint8, Struct("<B")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(0, 2 ** 16 - 1))
def test_uint16(val):
    sut, oracle = writeUint16, Struct("<H")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(0, 2 ** 32 - 1))
def test_uint32(val):
    sut, oracle = writeUint32, Struct("<I")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(0, 2 ** 64 - 1))
def test_uint64(val):
    sut, oracle = writeUint64, Struct("<Q")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(-(2 ** 7), (2 ** 7) - 1))
def test_int8(val):
    sut, oracle = writeInt8, Struct("<b")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(-(2 ** 15), (2 ** 15) - 1))
def test_int16(val):
    sut, oracle = writeInt16, Struct("<h")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(-(2 ** 31), (2 ** 31) - 1))
def test_int32(val):
    sut, oracle = writeInt32, Struct("<i")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(integers(-(2 ** 63), (2 ** 63) - 1))
def test_int64(val):
    sut, oracle = writeInt64, Struct("<q")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(floats(allow_nan=False))
def test_floats(val):
    sut, oracle = writeFloat32, Struct("<f")

    b1 = bytearray(20)
    b2 = bytearray(20)

    val = unpack("f", pack("f", val))[0]

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2


@given(floats(allow_nan=False))
def test_doubles(val):
    sut, oracle = writeFloat64, Struct("<d")

    b1 = bytearray(20)
    b2 = bytearray(20)

    sut(val, b1, 0)
    oracle.pack_into(b2, 0, val)

    assert b1 == b2
