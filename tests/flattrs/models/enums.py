from __future__ import annotations

from enum import IntEnum

from flattr import (
    Int8Enum,
    Int16Enum,
    Int32Enum,
    Uint8Enum,
    Uint16Enum,
    Uint32Enum,
    Uint64Enum,
    flattrs,
)


class ASimpleUByteEnum(Uint8Enum):
    ONE = 0
    TWO = 255


class ASimpleByteEnum(Int8Enum):
    THREE = 0
    FOUR = -127


class AnUInt8Enum(Uint8Enum):
    FIVE = 254
    SIX = 255


class AnInt8Enum(Int8Enum):
    SEVEN = -127
    EIGHT = -126


class AnUInt16Enum(Uint16Enum):
    NINE = 0
    TEN = 65000


class AnInt16Enum(Int16Enum):
    ELEVEN = -30000
    TWELVE = -29999


class AnUInt32Enum(Uint32Enum):
    THIRTEEN = 0
    FOURTEEN = 4000000000


class AnInt32Enum(Int32Enum):
    FIFTEEN = 0
    SIXTEEN = 1


class AnUInt64Enum(Uint64Enum):
    SEVENTEEN = 40000000000
    EIGHTEEN = 40000000001


class AnInt64Enum(IntEnum):
    NINETEEN = -40000000001
    TWENTY = -40000000000


@flattrs
class AllEnums:
    simple_ubyte: ASimpleUByteEnum | None
    simple_byte: ASimpleByteEnum | None
    uint8enum: AnUInt8Enum | None
    int8enum: AnInt8Enum | None
    uint16enum: AnUInt16Enum | None
    int16enum: AnInt16Enum | None
    uint32enum: AnUInt32Enum | None
    int32enum: AnInt32Enum | None
    uint64enum: AnUInt64Enum | None
    int64enum: AnInt64Enum | None
