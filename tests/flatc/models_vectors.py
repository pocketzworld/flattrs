from attrs import field

import flatc
from flatc.ByteArrayTable import ByteArrayTable
from flatc.OptionalByteArrayTable import OptionalByteArrayTable
from flatc.OptionalVectorsOfScalars import OptionalVectorsOfScalars
from flatc.OptVectorOfEnums import OptVectorOfEnums
from flatc.VectorOfCommon1 import VectorOfCommon1
from flatc.VectorOfEnums import VectorOfEnums
from flatc.VectorOfOptionalCommon1 import VectorOfOptionalCommon1
from flatc.VectorsOfBools import VectorsOfBools
from flatc.VectorsOfFloats import VectorsOfFloats
from flatc.VectorsOfInts import VectorsOfInts
from flatc.VectorsOfScalars import VectorsOfScalars
from tests import Flatbuffer, from_package

from .models_common import Common1
from .models_enums import ASimpleUByteEnum


@Flatbuffer(VectorsOfBools)
class VectorsOfBools:
    vec_of_bools: list[bool]


@Flatbuffer(VectorsOfInts)
class VectorsOfInts:
    vecOfInt8s: list[int]
    vecOfInt16s: list[int]
    vecOfInt32s: list[int]
    vecOfInt64s: list[int]


@Flatbuffer(VectorsOfFloats)
class VectorsOfFloats:
    vecOfFloat32s: list[float]
    vecOfFloat64s: list[float]


@Flatbuffer(VectorsOfScalars)
class VectorsOfScalars:
    vecOfBools: list[bool]
    vecOfUint8s: bytes = field(repr=False)
    vecOfUint16s: list[int]
    vecOfUint32s: list[int]
    vecOfUint64s: list[int]
    vecOfInt8s: list[int]
    vecOfInt16s: list[int]
    vecOfInt32s: list[int]
    vecOfInt64s: list[int]
    vecOfFloat32s: list[float]
    vecOfFloat64s: list[float]


@Flatbuffer(OptionalVectorsOfScalars)
class OptionalVectorsOfScalars:
    vecOfBools: list[bool] | None
    vecOfUint8s: bytes | None = field(repr=False)
    vecOfUint16s: list[int] | None
    vecOfUint32s: list[int] | None
    vecOfUint64s: list[int] | None
    vecOfInt8s: list[int] | None
    vecOfInt16s: list[int] | None
    vecOfInt32s: list[int] | None
    vecOfInt64s: list[int] | None
    vecOfFloat32s: list[float] | None
    vecOfFloat64s: list[float] | None


# @from_package(flattrs_test, frozen=True)
# class SeqVectorsOfScalars:
#     vecOfBools: Sequence[bool] = attr.ib()
#     vecOfUint8s: Sequence[int] = attr.ib()
#     vecOfUint16s: Sequence[int] = attr.ib()
#     vecOfUint32s: Sequence[int] = attr.ib()
#     vecOfUint64s: Sequence[int] = attr.ib()
#     vecOfInt8s: Sequence[int] = attr.ib()
#     vecOfInt16s: Sequence[int] = attr.ib()
#     vecOfInt32s: Sequence[int] = attr.ib()
#     vecOfInt64s: Sequence[int] = attr.ib()
#     vecOfFloat32s: Sequence[float] = attr.ib()
#     vecOfFloat64s: Sequence[float] = attr.ib()


@Flatbuffer(VectorOfCommon1)
class VectorOfCommon1:
    vecOfCommon: list[Common1]


@Flatbuffer(VectorOfOptionalCommon1)
class VectorOfOptionalCommon1:
    vecOfCommon: list[Common1] | None


# @Flatbuffer(SeqVectorOfOptionalCommon1)
# class SeqVectorOfOptionalCommon1:
#     vecOfCommon: Optional[Sequence[Common1]] = attr.ib()


# @from_package(flattrs_test, frozen=True)
# class SeqVectorOfCommon1:
#     vecOfCommon: Sequence[Common1] = attr.ib()


@Flatbuffer(ByteArrayTable)
class ByteArrayTable:
    contents: bytes = field(repr=False)


@Flatbuffer(OptionalByteArrayTable)
class OptionalByteArrayTable:
    contents: bytes | None = field(repr=False)


@Flatbuffer(VectorOfEnums)
class VectorOfEnums:
    enums: list[ASimpleUByteEnum]


@Flatbuffer(OptVectorOfEnums)
class OptVectorOfEnums:
    enums: list[ASimpleUByteEnum] | None


# @from_package(flattrs_test, frozen=True)
# class SeqVectorOfEnums:
#     enums: Sequence[ASimpleUByteEnum] = attr.ib()


# @from_package(flattrs_test, frozen=True)
# class SeqVectorOfStrings:
#     strings: Sequence[str] = attr.ib()


@from_package(flatc)
class VectorOfStrings:
    strings: list[str]


@from_package(flatc)
class OptionalVectorOfStrings:
    strings: list[str] | None


# @from_package(flattrs_test)
# class OptionalSeqVectorOfStrings:
#     strings: Optional[Sequence[str]] = attr.ib()
