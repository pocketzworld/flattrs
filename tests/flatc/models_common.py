import flattrs_test
from flattrs_test.AllScalarsWithDefaults import AllScalarsWithDefaults
from tests import Flatbuffer, from_package


@Flatbuffer.from_package(flattrs_test)
class Common1:
    id: str
    aSmallInt: int
    aBigInt: int


@from_package(flattrs_test)
class AllScalars:
    boolean: bool
    uint8: int
    uint16: int
    uint32: int
    uint64: int
    int8: int
    int16: int
    int32: int
    int64: int
    float32: float
    float64: float


@Flatbuffer(AllScalarsWithDefaults)
class AllScalarsWithDefaults:
    boolean: bool = True
    uint8: int = 1
    uint16: int = 1
    uint32: int = 1
    uint64: int = 1
    int8: int = 1
    int16: int = 1
    int32: int = 1
    int64: int = 1
    float32: float = 1.0
    float64: float = 1.0
