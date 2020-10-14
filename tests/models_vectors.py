from typing import List, Optional, Sequence

import attr

from flattr import Flatbuffer, from_package

from . import flattrs_test
from .flattrs_test.ByteArrayTable import ByteArrayTable
from .flattrs_test.OptionalByteArrayTable import OptionalByteArrayTable
from .flattrs_test.VectorOfCommon1 import VectorOfCommon1
from .flattrs_test.VectorOfEnums import VectorOfEnums
from .flattrs_test.VectorsOfScalars import VectorsOfScalars
from .models_common import Common1
from .models_enums import ASimpleUByteEnum


@Flatbuffer(VectorsOfScalars)
class VectorsOfScalars:
    vecOfBools: List[bool] = attr.ib()
    vecOfUint8s: List[int] = attr.ib()
    vecOfUint16s: List[int] = attr.ib()
    vecOfUint32s: List[int] = attr.ib()
    vecOfUint64s: List[int] = attr.ib()
    vecOfInt8s: List[int] = attr.ib()
    vecOfInt16s: List[int] = attr.ib()
    vecOfInt32s: List[int] = attr.ib()
    vecOfInt64s: List[int] = attr.ib()
    vecOfFloat32s: List[float] = attr.ib()
    vecOfFloat64s: List[float] = attr.ib()


@from_package(flattrs_test, frozen=True)
class SeqVectorsOfScalars:
    vecOfBools: Sequence[bool] = attr.ib()
    vecOfUint8s: Sequence[int] = attr.ib()
    vecOfUint16s: Sequence[int] = attr.ib()
    vecOfUint32s: Sequence[int] = attr.ib()
    vecOfUint64s: Sequence[int] = attr.ib()
    vecOfInt8s: Sequence[int] = attr.ib()
    vecOfInt16s: Sequence[int] = attr.ib()
    vecOfInt32s: Sequence[int] = attr.ib()
    vecOfInt64s: Sequence[int] = attr.ib()
    vecOfFloat32s: Sequence[float] = attr.ib()
    vecOfFloat64s: Sequence[float] = attr.ib()


@Flatbuffer(VectorOfCommon1)
class VectorOfCommon1:
    vecOfCommon: List[Common1] = attr.ib()


@from_package(flattrs_test, frozen=True)
class SeqVectorOfCommon1:
    vecOfCommon: Sequence[Common1] = attr.ib()


@Flatbuffer(ByteArrayTable)
class ByteArrayTable:
    contents: bytes = attr.ib()


@Flatbuffer(OptionalByteArrayTable)
class OptionalByteArrayTable:
    contents: Optional[bytes] = attr.ib()


@Flatbuffer(VectorOfEnums)
class VectorOfEnums:
    enums: List[ASimpleUByteEnum] = attr.ib()


@from_package(flattrs_test, frozen=True)
class SeqVectorOfEnums:
    enums: Sequence[ASimpleUByteEnum] = attr.ib()
