from typing import Optional, Union

import attr

from flatc import flattrs_test
from flatc.flattrs_test.CommonUnion import CommonUnion
from flatc.flattrs_test.UnionOfTables import UnionOfTables
from tests import UNION_CL, Flatbuffer, from_package

from .models_common import AllScalars, Common1


@from_package(flattrs_test)
class ContainsTable:
    inner: Common1


@from_package(flattrs_test)
class OptionalTable:
    inner: Common1 | None


@Flatbuffer(UnionOfTables)
class UnionOfTables:
    innerUnion: Union[Common1, AllScalars] = attr.ib(metadata={UNION_CL: CommonUnion})
