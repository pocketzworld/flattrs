# automatically generated by the FlatBuffers compiler, do not modify

# namespace: 

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class VectorsOfFloats(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = VectorsOfFloats()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsVectorsOfFloats(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # VectorsOfFloats
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # VectorsOfFloats
    def VecOfFloat32s(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Float32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # VectorsOfFloats
    def VecOfFloat32sAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Float32Flags, o)
        return 0

    # VectorsOfFloats
    def VecOfFloat32sLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # VectorsOfFloats
    def VecOfFloat32sIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

    # VectorsOfFloats
    def VecOfFloat64s(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Float64Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 8))
        return 0

    # VectorsOfFloats
    def VecOfFloat64sAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Float64Flags, o)
        return 0

    # VectorsOfFloats
    def VecOfFloat64sLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # VectorsOfFloats
    def VecOfFloat64sIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return o == 0

def VectorsOfFloatsStart(builder): builder.StartObject(2)
def Start(builder):
    return VectorsOfFloatsStart(builder)
def VectorsOfFloatsAddVecOfFloat32s(builder, vecOfFloat32s): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(vecOfFloat32s), 0)
def AddVecOfFloat32s(builder, vecOfFloat32s):
    return VectorsOfFloatsAddVecOfFloat32s(builder, vecOfFloat32s)
def VectorsOfFloatsStartVecOfFloat32sVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def StartVecOfFloat32sVector(builder, numElems):
    return VectorsOfFloatsStartVecOfFloat32sVector(builder, numElems)
def VectorsOfFloatsAddVecOfFloat64s(builder, vecOfFloat64s): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(vecOfFloat64s), 0)
def AddVecOfFloat64s(builder, vecOfFloat64s):
    return VectorsOfFloatsAddVecOfFloat64s(builder, vecOfFloat64s)
def VectorsOfFloatsStartVecOfFloat64sVector(builder, numElems): return builder.StartVector(8, numElems, 8)
def StartVecOfFloat64sVector(builder, numElems):
    return VectorsOfFloatsStartVecOfFloat64sVector(builder, numElems)
def VectorsOfFloatsEnd(builder): return builder.EndObject()
def End(builder):
    return VectorsOfFloatsEnd(builder)