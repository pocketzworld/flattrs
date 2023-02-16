from __future__ import annotations

from attrs import define, field, frozen

from flattr import Uint16


@define
class NoReprField:
    noReprInt: Uint16 = field(repr=False)


@frozen
class FrozenTable:
    a_string: str | None = None
