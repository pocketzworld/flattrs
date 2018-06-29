from typing import List

import attr
from flattr import Flatbuffer

from .flattrs_test.VectorsOfScalars import VectorsOfScalars
from .flattrs_test.VectorOfCommon1 import VectorOfCommon1

from .models_common import Common1


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


@Flatbuffer(VectorOfCommon1)
class VectorOfCommon1:
    vecOfCommon: List[Common1] = attr.ib()
