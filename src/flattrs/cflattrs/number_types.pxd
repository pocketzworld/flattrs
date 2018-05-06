from libc.stdint cimport uint64_t

cdef class Flags:
    cdef public unsigned short bytewidth
    cdef public uint64_t min_val
    cdef public uint64_t max_val
    cdef public py_type
    cdef public str name
    cdef public packer_type
    cdef public bint should_check


cdef inline void enforce_number(uint64_t n, Flags flags) except *:
    return
