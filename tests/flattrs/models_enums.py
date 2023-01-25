from flattr import flattrs
from flattr.types import (
    ByteEnum,
    Int8Enum,
    Int16Enum,
    Int32Enum,
    Int64Enum,
    UbyteEnum,
    Uint8Enum,
    Uint16Enum,
    Uint32Enum,
    Uint64Enum,
)


class ASimpleUByteEnum(UbyteEnum):
    ONE = 0
    TWO = 255


class ASimpleByteEnum(ByteEnum):
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
    FOURTEEN = 4_000_000_000


class AnInt32Enum(Int32Enum):
    FIFTEEN = 0
    SIXTEEN = 1


class AnUInt64Enum(Uint64Enum):
    SEVENTEEN = 40000000000
    EIGHTEEN = 40000000001


class AnInt64Enum(Int64Enum):
    NINETEEN = -40000000001
    TWENTY = -40000000000


@flattrs
class AllEnums:
    simple_ubyte: ASimpleUByteEnum
    simple_byte: ASimpleByteEnum
    uint8enum: AnUInt8Enum = AnUInt8Enum.FIVE
    int8enum: AnInt8Enum = AnInt8Enum.SEVEN
    uint16enum: AnUInt16Enum = AnUInt16Enum.NINE
    int16enum: AnInt16Enum = AnInt16Enum.ELEVEN
    uint32enum: AnUInt32Enum = AnUInt32Enum.FOURTEEN
    int32enum: AnInt32Enum = AnInt32Enum.SIXTEEN
    uint64enum: AnUInt64Enum = AnUInt64Enum.SEVENTEEN
    int64enum: AnInt64Enum = AnInt64Enum.NINETEEN
