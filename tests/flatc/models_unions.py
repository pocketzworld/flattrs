from typing import Union

from attrs import field

from flattr import UNION_CL, Flatbuffer
from flattrs_test.NestedUnion import NestedUnion
from flattrs_test.NumberedUnion import NumberedUnion
from flattrs_test.NumberedUnionTable import NumberedUnionTable
from flattrs_test.UnionOfNestedTables import UnionOfNestedTables
from flattrs_test.UnionOfOptionalTables import UnionOfOptionalTables

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
