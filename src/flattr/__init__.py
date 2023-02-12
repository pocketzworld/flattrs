from typing import Final

from ._consts import UNION_CL as UNION_CL
from ._fb_attrs import Flatbuffer as _Flatbuffer  # NOQA: F401
from ._fb_attrs import FlatbufferEnum as _FlatbufferEnum
from ._fb_attrs import from_package as _from_package
from ._fb_attrs import from_package_enum as _from_package_enum
from ._fb_attrs import model_from_bytes as model_from_bytes
from ._fb_attrs import model_to_bytes as model_to_bytes
from .converters import Converter
from .types import (
    Float,
    Float32,
    Float64,
    Int8,
    Int8Enum,
    Int16,
    Int16Enum,
    Int32,
    Int32Enum,
    Int64,
    Int64Enum,
    Uint8,
    Uint8Enum,
    Uint16,
    Uint16Enum,
    Uint32,
    Uint32Enum,
    Uint64,
    Uint64Enum,
    UnionVal,
)

Flatbuffer = _Flatbuffer
FlatbufferEnum = _FlatbufferEnum
from_package = _from_package
from_package_enum = _from_package_enum
global_converter = Converter()
dumps: Final = global_converter.dumps
loads: Final = global_converter.loads

__all__ = [
    "Flatbuffer",
    "FlatbufferEnum",
    "Float",
    "Float32",
    "Float64",
    "from_package_enum",
    "from_package",
    "Int16",
    "Int16Enum",
    "Int32",
    "Int32Enum",
    "Int64",
    "Int64Enum",
    "Int8",
    "Int8Enum",
    "Uint16",
    "Uint16Enum",
    "Uint32",
    "Uint32Enum",
    "Uint64",
    "Uint64Enum",
    "Uint8",
    "Uint8Enum",
    "UnionVal",
]
