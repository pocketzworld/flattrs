from enum import IntEnum
from typing import Annotated, Literal, TypeAlias

from attrs import frozen

try:
    from enum import ReprEnum as Enum
except ImportError:
    from enum import Enum


@frozen
class ScalarMarker:
    signed: bool
    width: Literal[8, 16, 32, 64]


Uint8 = Annotated[int, ScalarMarker(False, 8)]
Uint16 = Annotated[int, ScalarMarker(False, 16)]
Uint32 = Annotated[int, ScalarMarker(False, 32)]
Uint64 = Annotated[int, ScalarMarker(False, 64)]
Int8 = Annotated[int, ScalarMarker(True, 8)]
Int16 = Annotated[int, ScalarMarker(True, 16)]
Int32 = Annotated[int, ScalarMarker(True, 32)]
Int64: TypeAlias = int
Float = Annotated[float, ScalarMarker(True, 32)]
Float32: TypeAlias = Float
Float64: TypeAlias = float


class Uint8Enum(IntEnum):
    """An 8-bit Flatbuffer enum."""


UbyteEnum: TypeAlias = Uint8Enum


class Uint16Enum(IntEnum):
    """A 16-bit Flatbuffer enum."""


class Uint32Enum(IntEnum):
    """A 32-bit Flatbuffer enum."""


class Uint64Enum(IntEnum):
    """A 64-bit Flatbuffer enum."""


class Int8Enum(Int8, Enum):
    """An 8-bit Flatbuffer signed enum."""


ByteEnum: TypeAlias = Int8Enum


class Int16Enum(IntEnum):
    """A 16-bit Flatbuffer signed enum."""


class Int32Enum(IntEnum):
    """A 32-bit Flatbuffer signed enum."""


Int64Enum: TypeAlias = IntEnum


class UnionVal(int):
    """Annotate a union member with this to set the union type value."""

    pass
