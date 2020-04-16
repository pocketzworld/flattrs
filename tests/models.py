from typing import List, Optional

import attr

from flattr import Flatbuffer

from . import flattrs_test
from tests.flattrs_test.JustAFloat import JustAFloat
from tests.flattrs_test.JustADouble import JustADouble
from tests.flattrs_test.JustAString import JustAString
from tests.flattrs_test.JustBytes import JustBytes
from tests.flattrs_test.JustOptionalBytes import JustOptionalBytes
from tests.flattrs_test.JustAnOptionalString import JustAnOptionalString
from tests.flattrs_test.ListOfStrings import ListOfStrings

from .models_enums import ASimpleByteEnum


@Flatbuffer(JustAString)
class JustAString:
    id: str = attr.ib()


@Flatbuffer(JustAnOptionalString)
class JustAnOptionalString:
    id: Optional[str] = attr.ib()


@Flatbuffer(JustBytes)
class JustBytes:
    value: bytes = attr.ib()


@Flatbuffer(JustOptionalBytes)
class JustOptionalBytes:
    value: Optional[bytes] = attr.ib()


@Flatbuffer(JustAFloat)
class JustAFloat:
    value: float = attr.ib()


@Flatbuffer(JustADouble)
class JustADouble:
    value: float = attr.ib()


@Flatbuffer.from_package(flattrs_test)
class JustAnEnum:
    value: ASimpleByteEnum = attr.ib()


@Flatbuffer(ListOfStrings)
class ListOfStrings:
    content: List[str] = attr.ib()
