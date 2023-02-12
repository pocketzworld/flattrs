import attr

from flattrs_test.nested.NestedJustAString import NestedJustAString
from tests import Flatbuffer


@Flatbuffer(NestedJustAString)
class NestedJustAString:
    id: str = attr.ib()
