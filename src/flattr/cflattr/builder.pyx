#cython: language_level=3,
# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from libc.string cimport memcmp, memcpy, memset
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t, int8_t, int16_t, int32_t, int64_t
from cpython.mem cimport PyMem_Malloc, PyMem_Free

import struct

from .number_types cimport Flags, enforce_number

from flatbuffers import encode

cdef struct FlatbufferType:
    uint8_t bytewidth


cdef struct StoredVtable:
    uint32_t num_fields
    unsigned char* vtable
    int64_t offset        # Offset from the end of the file.
    StoredVtable* next


cdef FlatbufferType Fb_bool_t = FlatbufferType(1)
cdef FlatbufferType Fb_uint8_t = FlatbufferType(1)
cdef FlatbufferType Fb_uint16_t = FlatbufferType(2)
cdef FlatbufferType Fb_uint32_t = FlatbufferType(4)
cdef FlatbufferType Fb_uint64_t = FlatbufferType(8)
cdef FlatbufferType Fb_int8_t = FlatbufferType(1)
cdef FlatbufferType Fb_int16_t = FlatbufferType(2)
cdef FlatbufferType Fb_int32_t = FlatbufferType(4)
cdef FlatbufferType Fb_int64_t = FlatbufferType(8)
cdef FlatbufferType Fb_float32_t = FlatbufferType(4)
cdef FlatbufferType Fb_float64_t = FlatbufferType(8)


cdef inline void Write(packer_type, buf, Py_ssize_t head, Py_ssize_t n):
    """ Write encodes `n` at buf[head] using `packer_type`. """
    packer_type.pack_into(buf, head, n)


cpdef inline void writeBool(bint n, unsigned char* buffer, Py_ssize_t head):
    buffer[head] = 1 if n else 0


cpdef inline void writeUint8(uint8_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head] = n & 0xFF


cpdef inline void writeUint16(uint16_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head+1] = (n >> 8) & 0xFF
    buffer[head] = n & 0xFF


cpdef inline void writeUint32(uint32_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head+3] = (n >> 24) & 0xFF
    buffer[head+2] = (n >> 16) & 0xFF
    buffer[head+1] = (n >> 8) & 0xFF
    buffer[head] = n & 0xFF


cpdef inline void writeUint64(uint64_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head+7] = (n >> 56) & 0xFF
    buffer[head+6] = (n >> 48) & 0xFF
    buffer[head+5] = (n >> 40) & 0xFF
    buffer[head+4] = (n >> 32) & 0xFF
    buffer[head+3] = (n >> 24) & 0xFF
    buffer[head+2] = (n >> 16) & 0xFF
    buffer[head+1] = (n >> 8) & 0xFF
    buffer[head] = n & 0xFF


cpdef inline void writeInt8(int8_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head] = n & 0xFF


cpdef inline void writeInt16(int16_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head+1] = (n >> 8) & 0xFF
    buffer[head] = n & 0xFF


cpdef inline void writeInt32(int32_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head+3] = (n >> 24) & 0xFF
    buffer[head+2] = (n >> 16) & 0xFF
    buffer[head+1] = (n >> 8) & 0xFF
    buffer[head] = n & 0xFF


cpdef inline void writeInt64(int64_t n, unsigned char* buffer, Py_ssize_t head):
    buffer[head+7] = (n >> 56) & 0xFF
    buffer[head+6] = (n >> 48) & 0xFF
    buffer[head+5] = (n >> 40) & 0xFF
    buffer[head+4] = (n >> 32) & 0xFF
    buffer[head+3] = (n >> 24) & 0xFF
    buffer[head+2] = (n >> 16) & 0xFF
    buffer[head+1] = (n >> 8) & 0xFF
    buffer[head] = n & 0xFF


cdef union double2bytes:
    double d
    unsigned char b[8]


cpdef inline void writeFloat64(double n, unsigned char* buffer, Py_ssize_t head):
    cdef double2bytes t
    t.d = n
    buffer[head+7] = t.b[7]
    buffer[head+6] = t.b[6]
    buffer[head+5] = t.b[5]
    buffer[head+4] = t.b[4]
    buffer[head+3] = t.b[3]
    buffer[head+2] = t.b[2]
    buffer[head+1] = t.b[1]
    buffer[head] = t.b[0]


cdef union float2bytes:
    float f
    unsigned char b[8]


cpdef inline void writeFloat32(float n, unsigned char* buffer, Py_ssize_t head):
    cdef float2bytes t
    t.f = n
    buffer[head+3] = t.b[3]
    buffer[head+2] = t.b[2]
    buffer[head+1] = t.b[1]
    buffer[head] = t.b[0]


class OffsetArithmeticError(RuntimeError):
    """
    Error caused by an Offset arithmetic error. Probably caused by bad
    writing of fields. This is considered an unreachable situation in
    normal circumstances.
    """
    pass


class IsNotNestedError(RuntimeError):
    """
    Error caused by using a Builder to write Object data when not inside
    an Object.
    """
    pass


class IsNestedError(RuntimeError):
    """
    Error caused by using a Builder to begin an Object when an Object is
    already being built.
    """
    pass


class StructIsNotInlineError(RuntimeError):
    """
    Error caused by using a Builder to write a Struct at a location that
    is not the current Offset.
    """
    pass


class BuilderSizeError(RuntimeError):
    """
    Error caused by causing a Builder to exceed the hardcoded limit of 2
    gigabytes.
    """
    pass

class BuilderNotFinishedError(RuntimeError):
    """
    Error caused by not calling `Finish` before calling `Output`.
    """
    pass


# VtableMetadataFields is the count of metadata fields in each vtable.
cdef unsigned int VtableMetadataFields = 2
cdef unsigned int MAX_BUFFER_SIZE = 2**31

cdef class Builder(object):
    """ A Builder is used to construct one or more FlatBuffers.

    Typically, Builder objects will be used from code generated by the `flatc`
    compiler.

    A Builder constructs byte buffers in a last-first manner for simplicity and
    performance during reading.

    Internally, a Builder is a state machine for creating FlatBuffer objects.

    It holds the following internal state:
        - Bytes: an array of bytes.
        - current_vtable: a list of integers.
        - vtables: a list of vtable entries (i.e. a list of list of integers).

    Attributes:
      Bytes: The internal `bytearray` for the Builder.
      finished: A boolean determining if the Builder has been finalized.
    """
    cdef unsigned char* buffer
    cdef Py_ssize_t buffer_length
    cdef Py_ssize_t* current_vtable
    cdef Py_ssize_t current_vtable_length
    cdef Py_ssize_t head
    cdef Py_ssize_t minalign
    cdef int objectEnd
    cdef StoredVtable* vtables
    cdef bint nested
    cdef bint finished

    """Maximum buffer size constant, in bytes.

    Builder will never allow it's buffer grow over this size.
    Currently equals 2Gb.
    """

    def __init__(self, Py_ssize_t initialSize):
        """Initializes a Builder of size `initial_size`.

        The internal buffer is grown as needed.
        """

        if not (0 <= initialSize <= MAX_BUFFER_SIZE):
            msg = "flatbuffers: Cannot create Builder larger than 2 gigabytes."
            raise BuilderSizeError(msg)
        self.buffer = <unsigned char*> PyMem_Malloc(sizeof(unsigned char) * initialSize)
        if self.buffer is NULL:
            raise MemoryError()
        memset(self.buffer, 0, sizeof(unsigned char) * initialSize)
        self.buffer_length = initialSize
        self.current_vtable = NULL
        self.current_vtable_length = 0
        self.head = initialSize
        self.minalign = 1
        self.objectEnd = -1
        self.nested = False
        self.finished = False
        self.vtables = NULL

    def __dealloc__(self):
        PyMem_Free(self.buffer)
        if self.current_vtable != NULL:
            PyMem_Free(self.current_vtable)
            self.current_vtable = NULL
            self.current_vtable_length = 0
        while self.vtables is not NULL:
            next = self.vtables.next
            PyMem_Free(self.vtables.vtable)
            PyMem_Free(self.vtables)
            self.vtables = next

    def Output(self):
        """Return the portion of the buffer that has been used for writing data.

        This is the typical way to access the FlatBuffer data inside the
        builder. If you try to access `Builder.Bytes` directly, you would need
        to manually index it with `Head()`, since the buffer is constructed
        backwards.

        It raises BuilderNotFinishedError if the buffer has not been finished
        with `Finish`.
        """

        if not self.finished:
            raise BuilderNotFinishedError()

        cdef bytes res = self.buffer[self.head:self.buffer_length]

        return res

    @property
    def Bytes(self):
        return self.buffer[0:self.buffer_length]

    def StartObject(self, int numfields):
        """StartObject initializes bookkeeping for writing a new object."""

        self.assertNotNested()

        if numfields > 0:
            self.current_vtable = <Py_ssize_t*>PyMem_Malloc(sizeof(Py_ssize_t) * numfields)
            if self.current_vtable is NULL:
                raise MemoryError()
            memset(self.current_vtable, 0, sizeof(Py_ssize_t) * numfields)
        self.current_vtable_length = numfields
        self.objectEnd = self.Offset()
        self.minalign = 1
        self.nested = True

    cdef Py_ssize_t WriteVtable(self):
        """
        WriteVtable serializes the vtable for the current object, if needed.

        Before writing out the vtable, this checks pre-existing vtables for
        equality to this one. If an equal vtable is found, point the object to
        the existing vtable and return.

        Because vtable values are sensitive to alignment of object data, not
        all logically-equal vtables will be deduplicated.

        A vtable has the following format:
          <VOffsetT: size of the vtable in bytes, including this value>
          <VOffsetT: size of the object in bytes, including the vtable offset>
          <VOffsetT: offset for a field> * N, where N is the number of fields
                     in the schema for this type. Includes deprecated fields.
        Thus, a vtable is made of 2 + N elements, each VOffsetT bytes wide.

        An object has the following format:
          <SOffsetT: offset to this object's vtable (may be negative)>
          <byte: data>+
        """
        cdef Py_ssize_t objectOffset, i, off, objectSize, objectStart, vBytes
        cdef Py_ssize_t effective_vtable_length, vtable_offset
        cdef StoredVtable* svt

        # Prepend a zero scalar to the object. Later in this function we'll
        # write an offset here that points to the object's vtable:
        self.PrependSOffsetTRelative(0)  # 32-bit value.

        objectOffset = self.Offset()

        # Trim trailing 0 offsets.
        effective_vtable_length = 0
        for i in range(self.current_vtable_length, 0, -1):
            if self.current_vtable[i-1] != 0:
                effective_vtable_length = i
                break

        # Write out the current vtable in reverse, because
        # serialization occurs in last-first order:
        i = effective_vtable_length - 1
        cdef Py_ssize_t norm_vtable_length = sizeof(uint16_t) * effective_vtable_length
        norm_vtable = <unsigned char*>PyMem_Malloc(norm_vtable_length)
        while i >= 0:
            off = 0
            if self.current_vtable[i] != 0:
                # Forward reference to field;
                # use 32bit number to ensure no overflow:
                off = objectOffset - self.current_vtable[i]

            writeUint16(off, norm_vtable, i*2)
            i -= 1

        # Check if this vtable has been seen already.
        svt = self.vtables
        while svt is not NULL:
            if (svt.num_fields == effective_vtable_length and
                memcmp(norm_vtable, svt.vtable, norm_vtable_length) == 0):
                break
            svt = svt.next

        if svt is not NULL:
            PyMem_Free(self.current_vtable)
            self.current_vtable = NULL
            self.current_vtable_length = 0
            PyMem_Free(norm_vtable)
            objectStart = self.buffer_length - objectOffset
            self.head = objectStart

            # Write the offset to the found vtable in the
            # already-allocated SOffsetT at the beginning of this object.
            # The cached vtable contains its offset from the end of the buffer.
            vtable_offset = svt.offset
            writeInt32(vtable_offset - objectOffset, self.buffer, objectStart)
            return self.Offset()

        i = effective_vtable_length - 1
        while i >= 0:
            off = 0
            if self.current_vtable[i] != 0:
                # Forward reference to field;
                # use 32bit number to ensure no overflow:
                off = objectOffset - self.current_vtable[i]

            self.PrependVOffsetT(off)
            i -= 1
        # The two metadata fields are written last.

        # First, store the object bytesize:
        objectSize = objectOffset - self.objectEnd
        self.PrependVOffsetT(objectSize)

        # Second, store the vtable bytesize:
        vBytes = effective_vtable_length + VtableMetadataFields
        vBytes *= Fb_uint16_t.bytewidth
        self.PrependVOffsetT(vBytes)

        # Next, write the offset to the new vtable in the
        # already-allocated SOffsetT at the beginning of this object:
        objectStart = self.buffer_length - objectOffset
        writeUint32(self.Offset() - objectOffset, self.buffer, objectStart)

        # Finally, store this vtable in memory for future
        # deduplication:
        svt = <StoredVtable*>PyMem_Malloc(sizeof(StoredVtable))
        svt.num_fields = effective_vtable_length
        svt.vtable = norm_vtable
        svt.next = self.vtables
        svt.offset = self.Offset()
        self.vtables = svt

        PyMem_Free(self.current_vtable)
        self.current_vtable = NULL
        self.current_vtable_length = 0
        return objectOffset

    def EndObject(self):
        """EndObject writes data necessary to finish object construction."""
        self.assertNested()
        self.nested = False
        return self.WriteVtable()

    cdef void growByteBuffer(self):
        """Doubles the size of the byteslice, and copies the old data towards
           the end of the new buffer (since we build the buffer backwards)."""
        cdef Py_ssize_t newSize
        if self.buffer_length == MAX_BUFFER_SIZE:
            msg = "flatbuffers: cannot grow buffer beyond 2 gigabytes"
            raise BuilderSizeError(msg)

        newSize = min(self.buffer_length * 2, MAX_BUFFER_SIZE)
        if newSize == 0:
            newSize = 1
        buffer_2 = <unsigned char *>PyMem_Malloc(sizeof(unsigned char) * newSize)
        memcpy(&buffer_2[newSize-self.buffer_length], self.buffer, self.buffer_length)
        self.buffer_length = newSize
        PyMem_Free(self.buffer)
        self.buffer = buffer_2

    cdef Py_ssize_t Offset(self):
        """Offset relative to the end of the buffer."""
        return self.buffer_length - self.head

    cdef Pad(self, Py_ssize_t n):
        """Pad places zeros at the current offset."""
        cdef int i
        for i in range(n):
            self.Place(0, &Fb_uint8_t)

    cdef void Prep(self, Py_ssize_t size, Py_ssize_t additionalBytes):
        """
        Prep prepares to write an element of `size` after `additional_bytes`
        have been written, e.g. if you write a string, you need to align
        such the int length field is aligned to SizeInt32, and the string
        data follows it directly.
        If all you need to do is align, `additionalBytes` will be 0.
        """
        cdef long alignSize, updated_head, oldBufSize
        # Track the biggest thing we've ever aligned to.
        if size > self.minalign:
            self.minalign = size

        # Find the amount of alignment needed such that `size` is properly
        # aligned after `additionalBytes`:
        alignSize = (~(self.buffer_length - self.head + additionalBytes)) + 1
        alignSize &= (size - 1)

        # Reallocate the buffer if needed:
        while self.head < alignSize+size+additionalBytes:
            oldBufSize = self.buffer_length
            self.growByteBuffer()
            updated_head = self.head + self.buffer_length - oldBufSize
            self.head = updated_head
        self.Pad(alignSize)

    cdef void PrependSOffsetTRelative(self, int off):
        """
        PrependSOffsetTRelative prepends an SOffsetT, relative to where it
        will be written.
        """

        # Ensure alignment is already done:
        self.Prep(Fb_int32_t.bytewidth, 0)
        if not (off <= self.Offset()):
            msg = "flatbuffers: Offset arithmetic error."
            raise OffsetArithmeticError(msg)
        off2 = self.Offset() - off + Fb_int32_t.bytewidth
        self.PlaceSOffsetT(off2)

    cpdef void PrependUOffsetTRelative(self, Py_ssize_t off):
        """Prepends an unsigned offset into vector data, relative to where it
        will be written.
        """

        # Ensure alignment is already done:
        self.Prep(Fb_uint32_t.bytewidth, 0)
        if not (off <= self.Offset()):
            msg = "flatbuffers: Offset arithmetic error."
            raise OffsetArithmeticError(msg)
        off2 = self.Offset() - off + Fb_uint32_t.bytewidth
        self.PlaceUOffsetT(off2)

    def StartVector(self, int elemSize, Py_ssize_t numElems, Py_ssize_t alignment):
        """
        StartVector initializes bookkeeping for writing a new vector.

        A vector has the following format:
          - <UOffsetT: number of elements in this vector>
          - <T: data>+, where T is the type of elements of this vector.
        """

        self.assertNotNested()
        self.nested = True
        self.Prep(Fb_uint32_t.bytewidth, elemSize*numElems)
        self.Prep(alignment, elemSize*numElems)  # In case alignment > int.
        return self.Offset()

    cpdef Py_ssize_t EndVector(self, Py_ssize_t vectorNumElems):
        """EndVector writes data necessary to finish vector construction."""

        self.assertNested()
        ## @cond FLATBUFFERS_INTERNAL
        self.nested = False
        ## @endcond
        # we already made space for this, so write without PrependUint32
        self.PlaceUOffsetT(vectorNumElems)
        return self.Offset()

    cpdef Py_ssize_t CreateString(self, str s, encoding='utf-8', errors='strict'):
        """CreateString writes a null-terminated byte string as a vector."""
        cdef bytes x
        cdef Py_ssize_t l

        self.assertNotNested()
        ## @cond FLATBUFFERS_INTERNAL
        self.nested = True
        ## @endcond

        x = s.encode(encoding)
        l = len(x)

        self.Prep(Fb_uint32_t.bytewidth, (l+1)*Fb_uint8_t.bytewidth)
        self.Place(0, &Fb_uint8_t)

        self.head = self.head - l

        cdef char* c_string = x

        memcpy(<void*>&self.buffer[self.head], c_string, l)

        return self.EndVector(l)

    cpdef Py_ssize_t CreateByteVector(self, bytes x):
        """CreateString writes a byte vector."""
        self.assertNotNested()
        self.nested = True

        cdef l = len(x)

        self.Prep(Fb_uint32_t.bytewidth, l*Fb_uint8_t.bytewidth)

        self.head = self.head - l

        cdef char* c_string = x

        memcpy(<void*>&self.buffer[self.head], c_string, l)

        return self.EndVector(l)

    cdef void assertNested(self) except *:
        """
        Check that we are in the process of building an object.
        """

        if not self.nested:
            raise IsNotNestedError()

    cdef void assertNotNested(self) except *:
        """
        Check that no other objects are being built while making this
        object. If not, raise an exception.
        """

        if self.nested:
            raise IsNestedError()

    cdef void assertStructIsInline(self, Py_ssize_t obj) except *:
        """
        Structs are always stored inline, so need to be created right
        where they are used. You'll get this error if you created it
        elsewhere.
        """

        if obj != self.Offset():
            msg = ("flatbuffers: Tried to write a Struct at an Offset that "
                   "is different from the current Offset of the Builder.")
            raise StructIsNotInlineError(msg)

    cdef void Slot(self, Py_ssize_t slotnum) except *:
        """
        Slot sets the vtable key `voffset` to the current location in the
        buffer.

        """
        self.assertNested()
        if slotnum >= self.current_vtable_length:
            raise IndexError()
        self.current_vtable[slotnum] = self.Offset()

    cdef Py_ssize_t __Finish(self, Py_ssize_t rootTable, bint sizePrefix):
        """Finish finalizes a buffer, pointing to the given `rootTable`."""
        cdef Py_ssize_t prepSize, size

        prepSize = Fb_uint32_t.bytewidth
        if sizePrefix:
            prepSize += Fb_int32_t.bytewidth

        self.Prep(self.minalign, prepSize)
        self.PrependUOffsetTRelative(rootTable)
        if sizePrefix:
            size = self.buffer_length - self.head
            self.PrependInt32(size)
        self.finished = True
        return self.head

    def Finish(self, int rootTable):
        """Finish finalizes a buffer, pointing to the given `rootTable`."""
        return self.__Finish(rootTable, False)

    def FinishSizePrefixed(self, Py_ssize_t rootTable):
        """
        Finish finalizes a buffer, pointing to the given `rootTable`,
        with the size prefixed.
        """
        return self.__Finish(rootTable, True)

    cdef void Prepend(self, FlatbufferType* type, int64_t off):
        self.Prep(type.bytewidth, 0)
        self.Place(off, type)

    cdef void PrependSlot(self, FlatbufferType* type, Py_ssize_t o, int64_t x, int64_t d):
        if x != d:
            self.Prepend(type, x)
            self.Slot(o)

    def PrependBoolSlot(self, Py_ssize_t o, bint x, bint d):
        self.PrependSlot(&Fb_bool_t, o, x, d)

    def PrependByteSlot(self, Py_ssize_t o, int x, int d):
        self.PrependSlot(&Fb_uint8_t, o, x, d)

    def PrependUint8Slot(self, Py_ssize_t o, uint8_t x, uint8_t d):
        self.PrependSlot(&Fb_uint8_t, o, x, d)

    def PrependUint16Slot(self, Py_ssize_t o, uint16_t x, uint16_t d):
        self.PrependSlot(&Fb_uint16_t, o, x, d)

    def PrependUint32Slot(self, Py_ssize_t o, uint32_t x, uint32_t d):
        self.PrependSlot(&Fb_uint32_t, o, x, d)

    def PrependUint64Slot(self, Py_ssize_t o, uint64_t x, uint64_t d):
        self.PrependSlot(&Fb_uint64_t, o, x, d)

    def PrependInt8Slot(self, Py_ssize_t o, int8_t x, int8_t d):
        self.PrependSlot(&Fb_int8_t, o, x, d)

    def PrependInt16Slot(self, Py_ssize_t o, int16_t x, int16_t d):
        self.PrependSlot(&Fb_int16_t, o, x, d)

    def PrependInt32Slot(self, Py_ssize_t o, int32_t x, int32_t d):
        self.PrependSlot(&Fb_int32_t, o, x, d)

    def PrependInt64Slot(self, Py_ssize_t o, int64_t x, int64_t d):
        self.PrependSlot(&Fb_int64_t, o, x, d)

    def PrependFloat32Slot(self, Py_ssize_t o, float x, float d):
        if x != d:
            self.Prep(Fb_float32_t.bytewidth, 0)
            self.head = self.head - Fb_float32_t.bytewidth
            writeFloat32(x, self.buffer, self.head)
            self.Slot(o)

    def PrependFloat64Slot(self, Py_ssize_t o, double x, double d):
        if x != d:
            self.Prep(Fb_float64_t.bytewidth, 0)
            self.head = self.head - Fb_float64_t.bytewidth
            writeFloat64(x, self.buffer, self.head)
            self.Slot(o)

    def PrependUOffsetTRelativeSlot(self, Py_ssize_t o, Py_ssize_t x, Py_ssize_t d):
        """
        PrependUOffsetTRelativeSlot prepends an UOffsetT onto the object at
        vtable slot `o`. If value `x` equals default `d`, then the slot will
        be set to zero and no other data will be written.
        """
        if x != d:
            self.PrependUOffsetTRelative(x)
            self.Slot(o)

    cdef PrependStructSlot(self, v, x, d):
        """
        PrependStructSlot prepends a struct onto the object at vtable slot `o`.
        Structs are stored inline, so nothing additional is being added.
        In generated code, `d` is always 0.
        """
        if x != d:
            self.assertStructIsInline(x)
            self.Slot(v)

    def PrependBool(self, x):
        """Prepend a `bool` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_bool_t, x)

    def PrependByte(self, x):
        """Prepend a `byte` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_uint8_t, x)

    def PrependUint8(self, x):
        """Prepend an `uint8` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_uint8_t, x)

    def PrependUint16(self, x):
        """Prepend an `uint16` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_uint16_t, x)

    def PrependUint32(self, uint32_t x):
        """Prepend an `uint32` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_uint32_t, x)

    def PrependUint64(self, x):
        """Prepend an `uint64` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prep(Fb_uint64_t.bytewidth, 0)
        self.Place(x, &Fb_uint64_t)

    def PrependInt8(self, x):
        """Prepend an `int8` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_int8_t, x)

    def PrependInt16(self, x):
        """Prepend an `int16` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_int16_t, x)

    cpdef PrependInt32(self, int32_t x):
        """Prepend an `int32` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_int32_t, x)

    def PrependInt64(self, x):
        """Prepend an `int64` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prepend(&Fb_int64_t, x)

    def PrependFloat32(self, x):
        """Prepend a `float32` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prep(Fb_float32_t.bytewidth, 0)
        self.head = self.head - Fb_float32_t.bytewidth
        writeFloat32(x, self.buffer, self.head)

    def PrependFloat64(self, x):
        """Prepend a `float64` to the Builder buffer.

        Note: aligns and checks for space.
        """
        self.Prep(Fb_float64_t.bytewidth, 0)
        self.head = self.head - Fb_float64_t.bytewidth
        writeFloat64(x, self.buffer, self.head)

    cdef void PrependVOffsetT(self, uint16_t x):
        self.Prepend(&Fb_uint16_t, x)

    cdef void Place(self, uint64_t x, FlatbufferType *fb_type):
        """
        Place prepends a value specified by `flags` to the Builder,
        without checking for available space.
        """
        self.head = self.head - fb_type.bytewidth
        #Write(flags.packer_type, self.Bytes, self.head, x)

        if fb_type == &Fb_bool_t:
            writeBool(x, self.buffer, self.head)
        elif fb_type == &Fb_uint8_t:
            writeUint8(x, self.buffer, self.head)
        elif fb_type == &Fb_uint16_t:
            writeUint16(x, self.buffer, self.head)
        elif fb_type == &Fb_uint32_t:
            writeUint32(x, self.buffer, self.head)
        elif fb_type == &Fb_uint64_t:
            writeUint64(x, self.buffer, self.head)
        elif fb_type == &Fb_int8_t:
            writeInt8(x, self.buffer, self.head)
        elif fb_type == &Fb_int16_t:
            writeInt16(x, self.buffer, self.head)
        elif fb_type == &Fb_int32_t:
            writeInt32(x, self.buffer, self.head)
        elif fb_type == &Fb_int64_t:
            writeInt64(x, self.buffer, self.head)

    cdef void PlaceVOffsetT(self, uint16_t x):
        """PlaceVOffsetT prepends a VOffsetT to the Builder, without checking
        for space.
        """
        self.head = self.head - Fb_uint16_t.bytewidth
        writeUint16(x, self.buffer, self.head)

    cdef void PlaceSOffsetT(self, int32_t x):
        """PlaceSOffsetT prepends a SOffsetT to the Builder, without checking
        for space.
        """
        self.head = self.head - Fb_int32_t.bytewidth
        #Write(soffset, self.Bytes, self.head, x)
        writeInt32(x, self.buffer, self.head)

    cdef void PlaceUOffsetT(self, uint32_t x):
        """PlaceUOffsetT prepends a UOffsetT to the Builder, without checking
        for space.
        """
        self.head = self.head - Fb_uint32_t.bytewidth
        #Write(uoffset, self.Bytes, self.head, x)
        writeUint32(x, self.buffer, self.head)
