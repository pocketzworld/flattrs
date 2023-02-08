from __future__ import annotations

from attrs import field

from flattr import Float32, flattrs

from .enums import ASimpleByteEnum


@flattrs
class JustAString:
    id: str


@flattrs
class JustAnOptionalString:
    id: str | None = None


@flattrs
class JustBytes:
    value: bytes = field(repr=False)


@flattrs
class JustOptionalBytes:
    value: bytes | None = field(default=None, repr=False)


@flattrs
class JustAFloat:
    value: Float32


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
    aBc: str


@flattrs
class Empty:
    pass
