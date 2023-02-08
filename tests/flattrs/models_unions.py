from typing import Annotated, Union

from flattr import UnionVal, flattrs

from .models.common import AllScalars, AllScalarsWithDefaults, Common1
from .models_nested import NestedJustAString


@flattrs
class UnionOfNestedTables:
    innerUnion: Union[Common1, NestedJustAString]


@flattrs
class UnionOfOptionalTables:
    innerUnion: Union[None, Common1, NestedJustAString]


@flattrs
class NumberedUnionTable:
    innerUnion: Union[
        None, AllScalars, Annotated[Common1, UnionVal(100)], AllScalarsWithDefaults
    ]
