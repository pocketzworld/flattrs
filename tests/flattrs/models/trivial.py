from __future__ import annotations

from flattr import Float32, flattrs

from .enums import ASimpleByteEnum


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
    value: Float32


@flattrs
class JustADouble:
    value: float


@flattrs
class JustAnEnum:
    value: ASimpleByteEnum | None


@flattrs
class HasCaps:
    fieldCAPS: str
    fieldCAPSInMiddle: str
    aBc: str
