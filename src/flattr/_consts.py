from typing import Final

from ._types import ScalarType

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
