from typing import Final

from ._types import ScalarType
from .types import (
    Float,
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
)

NoneType = type(None)

ENUM_TYPE_TO_SCALAR_TYPE: Final = {
    Uint8Enum: "Uint8",
    Uint16Enum: "Uint16",
    Uint32Enum: "Uint32",
    Uint64Enum: "Uint64",
    Int8Enum: "Int8",
    Int16Enum: "Int16",
    Int32Enum: "Int32",
    Int64Enum: "Int64",
}

SCALAR_TYPE_TO_PYTHON: Final[dict[ScalarType, type]] = {
    "Uint8": int,
    "Uint16": int,
    "Uint32": int,
    "Uint64": int,
    "Int8": int,
    "Int16": int,
    "Int32": int,
    "Int64": int,
    "Bool": bool,
    "Float32": float,
    "Float64": float,
}

SCALAR_TYPE_TO_DEFAULT: Final[dict[ScalarType, str]] = {
    "float": "0.0",
    "double": "0.0",
    "Float32": "0.0",
    "Float64": "0.0",
    "Uint8": "0",
    "Uint16": "0",
    "Uint32": "0",
    "Uint64": "0",
    "Int8": "0",
    "Int16": "0",
    "Int32": "0",
    "Int64": "0",
    "Bool": "False",
}

HELPER_TYPE_TO_SCALAR_TYPE: Final[dict[type, ScalarType]] = {
    Uint8: "Uint8",
    Uint16: "Uint16",
    Uint32: "Uint32",
    Uint64: "Uint64",
    Int8: "Int8",
    Int16: "Int16",
    Int32: "Int32",
    bool: "Bool",
    Float: "Float32",
    Float64: "Float64",
    Int64: "Int64",
}

SCALAR_TYPE_TO_WIDTH: Final[dict[ScalarType, int]] = {
    "Bool": 1,
    "Uint8": 1,
    "Uint16": 2,
    "Uint32": 4,
    "Uint64": 8,
    "Int8": 1,
    "Int16": 2,
    "Int32": 4,
    "Int64": 8,
    "Float32": 4,
    "Float64": 8,
}
