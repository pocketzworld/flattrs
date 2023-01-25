from flattr import (
    Float32,
    Int8,
    Int16,
    Int32,
    Int64,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    flattrs,
)


@flattrs
class Common1:
    id: str
    aSmallInt: Uint8
    aBigInt: Int32

    def __repr__(self):
        return f"{self.id}:{self.aSmallInt}:{self.aBigInt}"


@flattrs
class AllScalars:
    boolean: bool
    uint8: Uint8
    uint16: Uint16
    uint32: Uint32
    uint64: Uint64
    int8: Int8
    int16: Int16
    int32: Int32
    int64: Int64
    float32: Float32
    float64: float


@flattrs
class AllScalarsWithDefaults:
    boolean: bool = True
    uint8: Uint8 = 1
    uint16: Uint16 = 1
    uint32: Uint32 = 1
    uint64: Uint64 = 1
    int8: Int8 = 1
    int16: Int16 = 1
    int32: Int32 = 1
    int64: Int64 = 1
    float32: Float32 = 1.0
    float64: float = 1.0
