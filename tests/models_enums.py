from enum import IntEnum

from flattr import FlatbufferEnum

from .flattrs_test.ASimpleUByteEnum import ASimpleUByteEnum


@FlatbufferEnum(ASimpleUByteEnum)
class ASimpleUByteEnum(IntEnum):
    ONE = 0
    TWO = 1
