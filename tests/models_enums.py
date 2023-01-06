from enum import IntEnum

import flattrs_test
from flattr import FlatbufferEnum, from_package_enum
from flattrs_test.ASimpleUByteEnum import ASimpleUByteEnum


@FlatbufferEnum(ASimpleUByteEnum)
class ASimpleUByteEnum(IntEnum):
    ONE = 0
    TWO = 1


@from_package_enum(flattrs_test)
class ASimpleByteEnum(IntEnum):
    ONE = 0
    TWO = 1
