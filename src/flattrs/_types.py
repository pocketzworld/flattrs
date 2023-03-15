"""Types used internally."""
from typing import Any, Literal, TypeAlias

from attrs import NOTHING, AttrsInstance

FieldName: TypeAlias = str
SlotNumber: TypeAlias = int
MaybeDefault: TypeAlias = Any | Literal[NOTHING]
ScalarType: TypeAlias = Literal[
    "Bool", "Uint8", "Uint16", "Uint32", "Float32", "float", "Float64", "double"
]
PythonScalarType: TypeAlias = type[int] | type[bool] | type[float]
Optionality: TypeAlias = bool
UnionMapping: TypeAlias = dict[int, type[AttrsInstance]]
