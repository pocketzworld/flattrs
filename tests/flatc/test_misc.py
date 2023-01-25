"""Misc tests to improve coverage."""
from enum import IntEnum

import pytest

from flattr import FlatbufferEnum


def test_enum_name_mismatch() -> None:
    from flattrs_test.ASimpleUByteEnum import ASimpleUByteEnum

    with pytest.raises(ValueError):

        @FlatbufferEnum(ASimpleUByteEnum)
        class ASimpleUByteEnum(IntEnum):
            ONE = 0
            TWOO = 255
