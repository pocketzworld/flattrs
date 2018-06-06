import attr
from flattr import Flatbuffer

from .flattrs_test.Common1 import Common1
from .flattrs_test.AllScalars import AllScalars
from .flattrs_test.AllScalarsWithDefaults import AllScalarsWithDefaults


@Flatbuffer(Common1)
class Common1:
    id: str = attr.ib()
    aSmallInt: int = attr.ib()
    aBigInt: int = attr.ib()


@Flatbuffer(AllScalars)
class AllScalars:
    boolean: bool = attr.ib()
    uint8: int = attr.ib()
    uint16: int = attr.ib()
    uint32: int = attr.ib()
    uint64: int = attr.ib()
    int8: int = attr.ib()
    int16: int = attr.ib()
    int32: int = attr.ib()
    int64: int = attr.ib()
    float32: float = attr.ib()
    float64: float = attr.ib()


@Flatbuffer(AllScalarsWithDefaults)
class AllScalarsWithDefaults:
    boolean: bool = attr.ib()
    uint8: int = attr.ib()
    uint16: int = attr.ib()
    uint32: int = attr.ib()
    uint64: int = attr.ib()
    int8: int = attr.ib()
    int16: int = attr.ib()
    int32: int = attr.ib()
    int64: int = attr.ib()
    float32: float = attr.ib()
    float64: float = attr.ib()
