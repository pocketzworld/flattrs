# automatically generated by the FlatBuffers compiler, do not modify

# namespace: flattrs_test

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class NoReprField(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = NoReprField()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsNoReprField(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # NoReprField
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # NoReprField
    def NoReprInt(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint16Flags, o + self._tab.Pos)
        return 0

def NoReprFieldStart(builder): builder.StartObject(1)
def Start(builder):
    return NoReprFieldStart(builder)
def NoReprFieldAddNoReprInt(builder, noReprInt): builder.PrependUint16Slot(0, noReprInt, 0)
def AddNoReprInt(builder, noReprInt):
    return NoReprFieldAddNoReprInt(builder, noReprInt)
def NoReprFieldEnd(builder): return builder.EndObject()
def End(builder):
    return NoReprFieldEnd(builder)