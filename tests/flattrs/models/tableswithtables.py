from __future__ import annotations

from flattr import flattrs

from .common import AllScalars, AllScalarsWithDefaults, Common1
from .nested.nested_trivial import NestedJustAString


@flattrs
class ContainsTable:
    inner: Common1


CommonUnion = Common1 | AllScalars
NumberedUnion = AllScalars | Common1 | AllScalarsWithDefaults


@flattrs
class UnionOfTables:
    innerUnion: CommonUnion


NestedUnion = Common1 | NestedJustAString


@flattrs
class UnionOfNestedTables:
    innerUnion: NestedUnion


@flattrs
class UnionOfOptionalTables:
    innerUnion: CommonUnion | None


@flattrs
class NumberedUnionTable:
    innerUnion: NumberedUnion | None


@flattrs
class OptionalTable:
    inner: Common1 | None
