from typing import Union

from flattr import flattrs

from .models_common import Common1
from .models_nested import NestedJustAString


@flattrs
class UnionOfNestedTables:
    innerUnion: Union[Common1, NestedJustAString]


@flattrs
class UnionOfOptionalTables:
    innerUnion: Union[None, Common1, NestedJustAString]
