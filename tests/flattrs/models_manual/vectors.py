from __future__ import annotations

from attrs import define, field

from flattrs import Float32, Int8, Int16, Int32, Uint16, Uint32, Uint64

from .common import Common1
from .enums import ASimpleUByteEnum


@define
class VectorsOfBools:
    vec_of_bools: list[bool]


@define
class VectorsOfInts:
    vecOfInt8s: list[Int8]
    vecOfInt16s: list[Int16]
    vecOfInt32s: list[Int32]
    vecOfInt64s: list[int]


@define
class VectorsOfFloats:
    vecOfFloat32s: list[Float32]
    vecOfFloat64s: list[float]


@define
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


@define
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


@define
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


@define
class VectorOfCommon1:
    vecOfCommon: list[Common1]


@define
class SeqVectorOfCommon1:
    vecOfCommon: list[Common1] | None = None


@define
class ByteArrayTable:
    contents: bytes = field(repr=False)


@define
class OptionalByteArrayTable:
    contents: bytes | None = field(default=None, repr=False)


@define
class VectorOfEnums:
    enums: list[ASimpleUByteEnum]


@define
class OptVectorOfEnums:
    enums: list[ASimpleUByteEnum] | None = None


@define
class SeqVectorOfEnums:
    enums: list[ASimpleUByteEnum] | None = None


@define
class SeqVectorOfStrings:
    strings: list[str]


@define
class VectorOfStrings:
    strings: list[str]


@define
class OptionalVectorOfStrings:
    strings: list[str] | None = None


@define
class OptionalSeqVectorOfStrings:
    strings: list[str] | None = None


@define
class VectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None = None


@define
class SeqVectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None = None
