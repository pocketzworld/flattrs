# automatically generated by the FlatBuffers compiler, do not modify

# namespace: flattrs_test

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Empty(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Empty()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsEmpty(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Empty
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

def EmptyStart(builder): builder.StartObject(0)
def Start(builder):
    return EmptyStart(builder)
def EmptyEnd(builder): return builder.EndObject()
def End(builder):
    return EmptyEnd(builder)