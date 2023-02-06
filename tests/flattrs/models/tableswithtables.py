from __future__ import annotations

from typing import Annotated

from flattr import UnionVal, flattrs

from .common import AllScalars, AllScalarsWithDefaults, Common1
from .enums import AnInt8Enum
from .nested.nested_trivial import NestedJustAString


@flattrs
class ContainsTable:
    inner: Common1


CommonUnion = Common1 | AllScalars


NumberedUnion = AllScalars | Annotated[Common1, UnionVal(100)] | AllScalarsWithDefaults


@flattrs
class UnionOfTables:
    innerUnion: CommonUnion


NestedUnion = Common1 | NestedJustAString


NestedUnion2 = Common1 | NestedJustAString


@flattrs
class UnionOfNestedTables:
    innerUnion: NestedUnion


@flattrs
class UnionOfOptionalTables:
    innerUnion: CommonUnion | None = None


@flattrs
class NumberedUnionTable:
    innerUnion: NumberedUnion | None = None


@flattrs
class OptionalTable:
    inner: Common1 | None = None


@flattrs
class ContainsNamespaced:
    inside: NestedJustAString


@flattrs
class OptionalTableAfterEnum:
    an_enum: AnInt8Enum = AnInt8Enum.EIGHT
    opt_table: Common1 | None = None
