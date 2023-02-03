from __future__ import annotations

from flattr import Float32, Int8, Int16, Int32, Uint16, Uint32, Uint64, flattrs

from .common import Common1
from .enums import ASimpleUByteEnum


@flattrs
class VectorsOfBools:
    vec_of_bools: list[bool]


@flattrs
class VectorsOfInts:
    vecOfInt8s: list[Int8]
    vecOfInt16s: list[Int16]
    vecOfInt32s: list[Int32]
    vecOfInt64s: list[int]


@flattrs
class VectorsOfFloats:
    vecOfFloat32s: list[Float32]
    vecOfFloat64s: list[float]


@flattrs
class VectorsOfScalars:
    vecOfBools: list[bool]
    vecOfUint8s: bytes
    vecOfUint16s: list[Uint16]
    vecOfUint32s: list[Uint32]
    vecOfUint64s: list[Uint64]
    vecOfInt8s: list[Int8]
    vecOfInt16s: list[Int16]
    vecOfInt32s: list[Int32]
    vecOfInt64s: list[int]
    vecOfFloat32s: list[Float32]
    vecOfFloat64s: list[float]


@flattrs
class OptionalVectorsOfScalars:
    vecOfBools: list[bool] | None
    vecOfUint8s: bytes | None
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
class SeqVectorsOfScalars:
    vecOfBools: list[bool] | None
    vecOfUint8s: bytes | None
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
class SeqVectorOfCommon1:
    vecOfCommon: list[Common1] | None


@flattrs
class ByteArrayTable:
    contents: bytes


@flattrs
class OptionalByteArrayTable:
    contents: bytes | None


@flattrs
class VectorOfEnums:
    enums: list[ASimpleUByteEnum]


@flattrs
class OptVectorOfEnums:
    enums: list[ASimpleUByteEnum] | None


@flattrs
class SeqVectorOfEnums:
    enums: list[ASimpleUByteEnum] | None


@flattrs
class SeqVectorOfStrings:
    strings: list[str]


@flattrs
class VectorOfStrings:
    strings: list[str]


@flattrs
class OptionalVectorOfStrings:
    strings: list[str] | None


@flattrs
class OptionalSeqVectorOfStrings:
    strings: list[str] | None


@flattrs
class VectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None


@flattrs
class SeqVectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None
