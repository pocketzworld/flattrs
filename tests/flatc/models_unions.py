from typing import Union

from attrs import field

from flatc.flattrs_test.NestedUnion import NestedUnion
from flatc.flattrs_test.NumberedUnion import NumberedUnion
from flatc.flattrs_test.NumberedUnionTable import NumberedUnionTable
from flatc.flattrs_test.SingleClassUnion import SingleClassUnion
from flatc.flattrs_test.SingleClassUnionRequiredTable import (
    SingleClassUnionRequiredTable,
)
from flatc.flattrs_test.SingleClassUnionTable import SingleClassUnionTable
from flatc.flattrs_test.UnionOfNestedTables import UnionOfNestedTables
from flatc.flattrs_test.UnionOfOptionalTables import UnionOfOptionalTables
from tests import UNION_CL, Flatbuffer

from .models_common import AllScalars, AllScalarsWithDefaults, Common1
from .models_nested import NestedJustAString


@Flatbuffer(UnionOfNestedTables)
class UnionOfNestedTables:
    innerUnion: Union[Common1, NestedJustAString] = field(
        metadata={UNION_CL: NestedUnion}
    )


@Flatbuffer(UnionOfOptionalTables)
class UnionOfOptionalTables:
    innerUnion: Union[None, Common1, NestedJustAString] = field(
        metadata={UNION_CL: NestedUnion}
    )


@Flatbuffer(NumberedUnionTable)
class NumberedUnionTable:
    innerUnion: Union[None, AllScalars, Common1, AllScalarsWithDefaults] = field(
        metadata={UNION_CL: NumberedUnion}
    )


@Flatbuffer(SingleClassUnionTable)
class SingleClassUnionTable:
    singleClassUnion: Union[None, Common1] = field(
        metadata={UNION_CL: SingleClassUnion}
    )


@Flatbuffer(SingleClassUnionRequiredTable)
class SingleClassUnionRequiredTable:
    singleClassReqUnion: Common1 = field(metadata={UNION_CL: SingleClassUnion})
