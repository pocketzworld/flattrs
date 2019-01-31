import attr

from flattr import Flatbuffer

from tests.flattrs_test.nested.NestedJustAString import NestedJustAString


@Flatbuffer(NestedJustAString)
class NestedJustAString:
    id: str = attr.ib()
