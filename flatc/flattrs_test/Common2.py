# automatically generated by the FlatBuffers compiler, do not modify

# namespace: flattrs_test

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Common2(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Common2()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsCommon2(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Common2
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Common2
    def Strings(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.String(a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return ""

    # Common2
    def StringsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Common2
    def StringsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

    # Common2
    def AString(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def Common2Start(builder): builder.StartObject(2)
def Start(builder):
    return Common2Start(builder)
def Common2AddStrings(builder, strings): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(strings), 0)
def AddStrings(builder, strings):
    return Common2AddStrings(builder, strings)
def Common2StartStringsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def StartStringsVector(builder, numElems):
    return Common2StartStringsVector(builder, numElems)
def Common2AddAString(builder, aString): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(aString), 0)
def AddAString(builder, aString):
    return Common2AddAString(builder, aString)
def Common2End(builder): return builder.EndObject()
def End(builder):
    return Common2End(builder)