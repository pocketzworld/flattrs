from typing import Optional, Union

import attr

from flattr import UNION_CL, Flatbuffer, from_package

from . import flattrs_test
from .flattrs_test.CommonUnion import CommonUnion
from .flattrs_test.UnionOfTables import UnionOfTables
from .models_common import AllScalars, Common1


@Flatbuffer(UnionOfTables)
class UnionOfTables:
    innerUnion: Union[Common1, AllScalars] = attr.ib(metadata={UNION_CL: CommonUnion})


@from_package(flattrs_test)
class ContainsTable:
    inner: Common1 = attr.ib()


@from_package(flattrs_test)
class OptionalTable:
    inner: Optional[Common1] = attr.ib()
