from __future__ import annotations

from typing import Annotated

from attrs import define

from flattr import UnionVal

from .common import AllScalars, AllScalarsWithDefaults, Common1
from .enums import AnInt8Enum
from .nested.nested_trivial import NestedJustAString


@define
class ContainsTable:
    inner: Common1


CommonUnion = Common1 | AllScalars


NumberedUnion = AllScalars | Annotated[Common1, UnionVal(100)] | AllScalarsWithDefaults


@define
class UnionOfTables:
    innerUnion: CommonUnion


NestedUnion = Common1 | NestedJustAString


NestedUnion2 = Common1 | NestedJustAString


@define
class UnionOfNestedTables:
    innerUnion: NestedUnion


@define
class UnionOfOptionalTables:
    innerUnion: CommonUnion | None = None


@define
class NumberedUnionTable:
    innerUnion: NumberedUnion | None = None


@define
class OptionalTable:
    inner: Common1 | None = None


@define
class ContainsNamespaced:
    inside: NestedJustAString


@define
class OptionalTableAfterEnum:
    an_enum: AnInt8Enum = AnInt8Enum.EIGHT
    opt_table: Common1 | None = None
