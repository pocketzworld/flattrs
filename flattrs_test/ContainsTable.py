# automatically generated by the FlatBuffers compiler, do not modify

# namespace: flattrs_test

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class ContainsTable(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ContainsTable()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsContainsTable(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # ContainsTable
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ContainsTable
    def Inner(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Indirect(o + self._tab.Pos)
            from flattrs_test.Common1 import Common1
            obj = Common1()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

def ContainsTableStart(builder): builder.StartObject(1)
def Start(builder):
    return ContainsTableStart(builder)
def ContainsTableAddInner(builder, inner): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(inner), 0)
def AddInner(builder, inner):
    return ContainsTableAddInner(builder, inner)
def ContainsTableEnd(builder): return builder.EndObject()
def End(builder):
    return ContainsTableEnd(builder)