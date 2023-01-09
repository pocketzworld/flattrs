import attr

from flattr import Flatbuffer
from flattrs_test.HasCaps import HasCaps


@Flatbuffer(HasCaps)
class HasCaps:
    fieldCAPS: str = attr.ib()
    fieldCAPSInMiddle: str = attr.ib()
