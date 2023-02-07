from __future__ import annotations

from attrs import field

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
    vecOfUint8s: bytes = field(repr=False)
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
    vecOfBools: list[bool] | None = None
    vecOfUint8s: bytes | None = field(default=None, repr=False)
    vecOfUint16s: list[Uint16] | None = None
    vecOfUint32s: list[Uint32] | None = None
    vecOfUint64s: list[Uint64] | None = None
    vecOfInt8s: list[Int8] | None = None
    vecOfInt16s: list[Int16] | None = None
    vecOfInt32s: list[Int32] | None = None
    vecOfInt64s: list[int] | None = None
    vecOfFloat32s: list[Float32] | None = None
    vecOfFloat64s: list[float] | None = None


@flattrs
class SeqVectorsOfScalars:
    vecOfBools: list[bool] | None = None
    vecOfUint8s: bytes | None = field(default=None, repr=False)
    vecOfUint16s: list[Uint16] | None = None
    vecOfUint32s: list[Uint32] | None = None
    vecOfUint64s: list[Uint64] | None = None
    vecOfInt8s: list[Int8] | None = None
    vecOfInt16s: list[Int16] | None = None
    vecOfInt32s: list[Int32] | None = None
    vecOfInt64s: list[int] | None = None
    vecOfFloat32s: list[Float32] | None = None
    vecOfFloat64s: list[float] | None = None


@flattrs
class VectorOfCommon1:
    vecOfCommon: list[Common1]


@flattrs
class SeqVectorOfCommon1:
    vecOfCommon: list[Common1] | None = None


@flattrs
class ByteArrayTable:
    contents: bytes = field(repr=False)


@flattrs
class OptionalByteArrayTable:
    contents: bytes | None = field(default=None, repr=False)


@flattrs
class VectorOfEnums:
    enums: list[ASimpleUByteEnum]


@flattrs
class OptVectorOfEnums:
    enums: list[ASimpleUByteEnum] | None = None


@flattrs
class SeqVectorOfEnums:
    enums: list[ASimpleUByteEnum] | None = None


@flattrs
class SeqVectorOfStrings:
    strings: list[str]


@flattrs
class VectorOfStrings:
    strings: list[str]


@flattrs
class OptionalVectorOfStrings:
    strings: list[str] | None = None


@flattrs
class OptionalSeqVectorOfStrings:
    strings: list[str] | None = None


@flattrs
class VectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None = None


@flattrs
class SeqVectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None = None
