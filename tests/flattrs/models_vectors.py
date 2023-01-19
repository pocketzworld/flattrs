from flattr import flattrs
from flattr.types import (
    Float32,
    Float64,
    Int8,
    Int16,
    Int32,
    Int64,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
)

from .models_common import Common1


@flattrs
class VectorsOfBools:
    vecOfBools: list[bool]


@flattrs
class VectorsOfScalars:
    vecOfBools: list[bool]
    vecOfUint8s: list[Uint8]
    vecOfUint16s: list[Uint16]
    vecOfUint32s: list[Uint32]
    vecOfUint64s: list[Uint64]
    vecOfInt8s: list[Int8]
    vecOfInt16s: list[Int16]
    vecOfInt32s: list[Int32]
    vecOfInt64s: list[Int64]
    vecOfFloat32s: list[Float32]
    vecOfFloat64s: list[Float64]


@flattrs
class VectorsOfInts:
    vecOfInt8s: list[Int8]
    vecOfInt16s: list[Int16]
    vecOfInt32s: list[Int32]
    vecOfInt64s: list[Int64]


@flattrs
class OptionalVectorsOfScalars:
    vecOfBools: list[bool] | None
    vecOfUint8s: list[Uint8] | None
    vecOfUint16s: list[Uint16] | None
    vecOfUint32s: list[Uint32] | None
    vecOfUint64s: list[Uint64] | None
    vecOfInt8s: list[Int8] | None
    vecOfInt16s: list[Int16] | None
    vecOfInt32s: list[Int32] | None
    vecOfInt64s: list[int] | None
    vecOfFloat32s: list[Float32] | None
    vecOfFloat64s: list[float] | None


@flattrs
class VectorOfCommon1:
    vecOfCommon: list[Common1]


@flattrs
class VectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None


@flattrs
class ByteArrayTable:
    contents: bytes
