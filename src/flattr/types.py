from enum import IntEnum
from typing import TypeAlias

try:
    from enum import ReprEnum as Enum
except ImportError:
    from enum import Enum


class Uint8(int):
    """An 8-bit Flatbuffer unsigned int."""


class Uint8Enum(Uint8, Enum):
    """An 8-bit Flatbuffer enum."""


UbyteEnum: TypeAlias = Uint8Enum


class Uint16(int):
    """A 16-bit Flatbuffer unsigned int."""


class Uint16Enum(Uint16, Enum):
    """A 16-bit Flatbuffer enum."""


class Uint32(int):
    """A 32-bit Flatbuffer unsigned int."""


class Uint32Enum(Uint32, Enum):
    """A 32-bit Flatbuffer enum."""


class Uint64(int):
    """A 64-bit Flatbuffer unsigned int."""


class Uint64Enum(Uint64, Enum):
    """A 64-bit Flatbuffer enum."""


class Int8(int):
    """An 8-bit Flatbuffer signed int."""


class Int8Enum(Int8, Enum):
    """An 8-bit Flatbuffer signed enum."""


ByteEnum: TypeAlias = Int8Enum


class Int16(int):
    """A 16-bit Flatbuffer signed int."""


class Int16Enum(Int16, Enum):
    """A 16-bit Flatbuffer signed enum."""


class Int32(int):
    """A 32-bit Flatbuffer signed int."""


class Int32Enum(Int32, Enum):
    """A 32-bit Flatbuffer signed enum."""


Int64: TypeAlias = int
Int64Enum: TypeAlias = IntEnum


class Float(float):
    """A 32-bit Flatbuffer float."""


Float32: TypeAlias = Float
Float64: TypeAlias = float


class UnionVal(int):
    """Annotate a union member with this to set the union type value."""

    pass
