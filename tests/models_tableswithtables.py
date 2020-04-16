from typing import Union

import attr
from flattr import Flatbuffer, UNION_CL

from .flattrs_test.UnionOfTables import UnionOfTables
from .flattrs_test.CommonUnion import CommonUnion
from .models_common import Common1, AllScalars


@Flatbuffer(UnionOfTables)
class UnionOfTables:
    innerUnion: Union[Common1, AllScalars] = attr.ib(
        metadata={UNION_CL: CommonUnion}
    )
