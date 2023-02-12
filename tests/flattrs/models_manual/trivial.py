from __future__ import annotations

from attrs import define, field

from flattr import Float32

from .enums import ASimpleByteEnum


@define
class JustAString:
    id: str


@define
class JustAnOptionalString:
    id: str | None = None


@define
class JustBytes:
    value: bytes = field(repr=False)


@define
class JustOptionalBytes:
    value: bytes | None = field(default=None, repr=False)


@define
class JustAFloat:
    value: Float32


@define
class JustADouble:
    value: float


@define
class JustAnEnum:
    value: ASimpleByteEnum


@define
class HasCaps:
    fieldCAPS: str
    fieldCAPSInMiddle: str
    aBc: str


@define
class Empty:
    pass
