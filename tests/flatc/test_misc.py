"""Misc tests to improve coverage."""
from enum import IntEnum

import pytest

from tests import FlatbufferEnum


def test_enum_name_mismatch() -> None:
    from flatc.flattrs_test.ASimpleUByteEnum import ASimpleUByteEnum

    with pytest.raises(ValueError):

        @FlatbufferEnum(ASimpleUByteEnum)
        class ASimpleUbyteEnum(IntEnum):  # Name does't match the flatc version.
            ONE = 0
            TWO = 255


def test_enum_member_name_mismatch() -> None:
    from flatc.flattrs_test.ASimpleUByteEnum import ASimpleUByteEnum

    with pytest.raises(ValueError):

        @FlatbufferEnum(ASimpleUByteEnum)
        class ASimpleUByteEnum(IntEnum):
            ONE = 0
            TWOO = 255
