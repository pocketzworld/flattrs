from __future__ import annotations

from attrs import define, field, frozen

from flattrs import Uint8, Uint16


@define
class NoReprField:
    noReprInt: Uint16 = field(repr=False)


@frozen
class FrozenTable:
    a_string: str | None = None


@define
class IgnoredAttributes:
    a_field: Uint8
