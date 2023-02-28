from typing import Final

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

global_converter = Converter()
dumps: Final = global_converter.dumps
loads: Final = global_converter.loads
make_dumps: Final = global_converter.make_dumps
make_loads: Final = global_converter.make_loads

__all__ = [
    "dumps",
    "Float",
    "Float32",
    "Float64",
    "Int16",
    "Int16Enum",
    "Int32",
    "Int32Enum",
    "Int64",
    "Int64Enum",
    "Int8",
    "Int8Enum",
    "loads",
    "make_dumps",
    "make_loads",
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
