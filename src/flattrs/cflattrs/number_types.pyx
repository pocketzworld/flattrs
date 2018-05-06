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

import collections
import struct

from flatbuffers import packer
from flatbuffers.compat import import_numpy, NumpyRequiredForThisFeature

np = import_numpy()

# For reference, see:
# https://docs.python.org/2/library/ctypes.html#ctypes-fundamental-data-types-2

# These classes could be collections.namedtuple instances, but those are new
# in 2.6 and we want to work towards 2.5 compatability.

cdef class Flags:
    def __init__(self, unsigned short bytewidth, min_val, max_val, py_type, str name, packer_type, bint should_check):
        self.bytewidth = bytewidth
        self.min_val = min_val
        self.max_val = max_val
        self.py_type = py_type
        self.name = name
        self.packer_type = packer_type
        self.should_check = should_check


def float32_to_uint32(n):
    packed = struct.pack("<1f", n)
    (converted,) = struct.unpack("<1L", packed)
    return converted


def uint32_to_float32(n):
    packed = struct.pack("<1L", n)
    (unpacked,) = struct.unpack("<1f", packed)
    return unpacked


def float64_to_uint64(n):
    packed = struct.pack("<1d", n)
    (converted,) = struct.unpack("<1Q", packed)
    return converted


def uint64_to_float64(n):
    packed = struct.pack("<1Q", n)
    (unpacked,) = struct.unpack("<1d", packed)
    return unpacked


def to_numpy_type(number_type):
    if np is not None:
        return np.dtype(number_type.name).newbyteorder('<')
    else:
        raise NumpyRequiredForThisFeature('Numpy was not found.')
