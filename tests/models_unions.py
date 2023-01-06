from typing import Union

import attr

from flattr import UNION_CL, Flatbuffer
from flattrs_test.NestedUnion import NestedUnion
from flattrs_test.UnionOfNestedTables import UnionOfNestedTables
from flattrs_test.UnionOfOptionalTables import UnionOfOptionalTables

from .models_common import Common1
from .models_nested import NestedJustAString


@Flatbuffer(UnionOfNestedTables)
class UnionOfNestedTables:
    innerUnion: Union[Common1, NestedJustAString] = attr.ib(
        metadata={UNION_CL: NestedUnion}
    )


@Flatbuffer(UnionOfOptionalTables)
class UnionOfOptionalTables:
    innerUnion: Union[None, Common1, NestedJustAString] = attr.ib(
        metadata={UNION_CL: NestedUnion}
    )
