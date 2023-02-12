import attr
from attrs import field

import flattrs_test
from flattrs_test.HasCaps import HasCaps
from flattrs_test.JustADouble import JustADouble
from flattrs_test.JustAFloat import JustAFloat
from flattrs_test.JustAnOptionalString import JustAnOptionalString
from flattrs_test.JustAString import JustAString
from flattrs_test.JustBytes import JustBytes
from flattrs_test.JustOptionalBytes import JustOptionalBytes
from tests import Flatbuffer

from .models_enums import ASimpleByteEnum


@Flatbuffer(JustAString)
class JustAString:
    id: str = attr.ib()


@Flatbuffer(JustAnOptionalString)
class JustAnOptionalString:
    id: str | None


@Flatbuffer(JustBytes)
class JustBytes:
    value: bytes = attr.ib()


@Flatbuffer(JustOptionalBytes)
class JustOptionalBytes:
    value: bytes | None = field(repr=False)


@Flatbuffer(JustAFloat)
class JustAFloat:
    value: float


@Flatbuffer(JustADouble)
class JustADouble:
    value: float


@Flatbuffer.from_package(flattrs_test)
class JustAnEnum:
    value: ASimpleByteEnum


@Flatbuffer(HasCaps)
class HasCaps:
    fieldCAPS: str
    fieldCAPSInMiddle: str
    aBc: str
