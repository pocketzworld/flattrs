# automatically generated by the FlatBuffers compiler, do not modify

# namespace: flattrs_test

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class JustAnEnum(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = JustAnEnum()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsJustAnEnum(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # JustAnEnum
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # JustAnEnum
    def Value(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

def JustAnEnumStart(builder): builder.StartObject(1)
def Start(builder):
    return JustAnEnumStart(builder)
def JustAnEnumAddValue(builder, value): builder.PrependInt8Slot(0, value, 0)
def AddValue(builder, value):
    return JustAnEnumAddValue(builder, value)
def JustAnEnumEnd(builder): return builder.EndObject()
def End(builder):
    return JustAnEnumEnd(builder)