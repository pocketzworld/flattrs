# automatically generated by the FlatBuffers compiler, do not modify

# namespace: flattrs_test

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class IgnoredAttributes(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = IgnoredAttributes()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsIgnoredAttributes(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # IgnoredAttributes
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # IgnoredAttributes
    def AField(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

def IgnoredAttributesStart(builder): builder.StartObject(1)
def Start(builder):
    return IgnoredAttributesStart(builder)
def IgnoredAttributesAddAField(builder, aField): builder.PrependUint8Slot(0, aField, 0)
def AddAField(builder, aField):
    return IgnoredAttributesAddAField(builder, aField)
def IgnoredAttributesEnd(builder): return builder.EndObject()
def End(builder):
    return IgnoredAttributesEnd(builder)