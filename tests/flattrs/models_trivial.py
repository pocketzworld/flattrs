from typing import Annotated

from flattr import flattrs
from flattr.types import Float

from .models_enums import ASimpleByteEnum


@flattrs
class JustAString:
    id: str


@flattrs
class JustAnOptionalString:
    id: str | None


@flattrs
class JustBytes:
    value: bytes


@flattrs
class JustOptionalBytes:
    value: bytes | None


@flattrs
class JustAFloat:
    value: Float


@flattrs
class JustAFloatAnnotated:
    value: Annotated[float, Float]


@flattrs
class JustADouble:
    value: float


@flattrs
class JustAnEnum:
    value: ASimpleByteEnum


@flattrs
class HasCaps:
    fieldCAPS: str
    fieldCAPSInMiddle: str
