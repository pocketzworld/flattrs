from enum import IntEnum

import flattrs_test
from flattrs_test.ASimpleUByteEnum import ASimpleUByteEnum
from tests import FlatbufferEnum, from_package, from_package_enum


@FlatbufferEnum(ASimpleUByteEnum)
class ASimpleUByteEnum(IntEnum):
    ONE = 0
    TWO = 255


@from_package_enum(flattrs_test)
class ASimpleByteEnum(IntEnum):
    THREE_ = 0
    FOUR_ = -127


@from_package_enum(flattrs_test)
class AnUInt8Enum(IntEnum):
    FIVE_ = 254
    SIX = 255


@from_package_enum(flattrs_test)
class AnInt8Enum(IntEnum):
    SEVEN = -127
    EIGHT = -126


@from_package_enum(flattrs_test)
class AnUInt16Enum(IntEnum):
    NINE = 0
    TEN = 65000


@from_package_enum(flattrs_test)
class AnInt16Enum(IntEnum):
    ELEVEN = -30000
    TWELVE = -29999


@from_package_enum(flattrs_test)
class AnUInt32Enum(IntEnum):
    THIRTEEN = 0
    FOURTEEN = 4_000_000_000


@from_package_enum(flattrs_test)
class AnInt32Enum(IntEnum):
    FIFTEEN = 0
    SIXTEEN = 1


@from_package_enum(flattrs_test)
class AnUInt64Enum(IntEnum):
    SEVENTEEN = 40000000000
    EIGHTEEN = 40000000001


@from_package_enum(flattrs_test)
class AnInt64Enum(IntEnum):
    NINETEEN = -40000000001
    TWENTY = -40000000000


@from_package(flattrs_test)
class AllEnums:
    simple_ubyte: ASimpleUByteEnum
    simple_byte: ASimpleByteEnum
    uint8enum: AnUInt8Enum = AnUInt8Enum.FIVE_
    int8enum: AnInt8Enum = AnInt8Enum.SEVEN
    uint16enum: AnUInt16Enum = AnUInt16Enum.NINE
    int16enum: AnInt16Enum = AnInt16Enum.ELEVEN
    uint32enum: AnUInt32Enum = AnUInt32Enum.FOURTEEN
    int32enum: AnInt32Enum = AnInt32Enum.SIXTEEN
    uint64enum: AnUInt64Enum = AnUInt64Enum.SEVENTEEN
    int64enum: AnInt64Enum = AnInt64Enum.NINETEEN
