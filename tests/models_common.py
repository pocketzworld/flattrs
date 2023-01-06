import attr

import flattrs_test
from flattr import Flatbuffer, from_package
from flattrs_test.AllScalarsWithDefaults import AllScalarsWithDefaults


@Flatbuffer.from_package(flattrs_test, repr=False)
class Common1:
    id: str = attr.ib()
    aSmallInt: int = attr.ib()
    aBigInt: int = attr.ib()

    def __repr__(self):
        return f"{self.id}:{self.aSmallInt}:{self.aBigInt}"


@from_package(flattrs_test)
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
