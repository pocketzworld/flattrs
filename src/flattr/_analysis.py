"""Types used internally."""
from enum import Enum, IntEnum

from attrs import NOTHING, AttrsInstance, fields, frozen, has

from ._consts import HELPER_TYPE_TO_SCALAR_TYPE, NoneType
from ._types import (
    FieldName,
    MaybeDefault,
    Optionality,
    PythonScalarType,
    ScalarType,
    SlotNumber,
    UnionMapping,
)
from .types import (
    Float,
    Float64,
    Int8,
    Int16,
    Int32,
    Int64,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    UnionVal,
)
from .typing import (
    get_annotation_and_base,
    get_optional_arg,
    get_union_args,
    is_generic_subclass,
    is_subclass,
    resolve_types,
)


@frozen
class FlatbufferTable:
    cl: type[AttrsInstance]
    num_slots: int
    inlines: list[FieldName, ScalarType, SlotNumber, MaybeDefault]
    enums: list[FieldName, ScalarType, SlotNumber, MaybeDefault]
    strings: list[tuple[FieldName, SlotNumber, Optionality]]
    byte_fields: list[tuple[FieldName, SlotNumber, Optionality]]
    tables: list[tuple[FieldName, type, SlotNumber, Optionality]]
    lists_of_strings: list[tuple[FieldName, SlotNumber, Optionality]]
    lists_of_scalars: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ]
    lists_of_enums: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ]
    lists_of_tables: list[tuple[FieldName, type, SlotNumber, Optionality]]
    unions: list[tuple[FieldName, tuple[type, ...], UnionMapping, SlotNumber]]


def analyze(
    cl: type[AttrsInstance],
    field_overrides: list[tuple[FieldName, ScalarType, MaybeDefault]] = [],
    scalar_list_overrides: list[tuple[FieldName, ScalarType]] = [],
    union_overrides: dict[FieldName, UnionMapping] = {},
) -> FlatbufferTable:
    resolve_types(cl)
    strings: list[tuple[FieldName, SlotNumber, Optionality]] = []
    byte_fields: list[tuple[FieldName, SlotNumber, Optionality]] = []
    tables: list[tuple[FieldName, type, SlotNumber, Optionality]] = []
    lists_of_tables: list[tuple[FieldName, type, SlotNumber, Optionality]] = []
    lists_of_strings: list[tuple[FieldName, SlotNumber, Optionality]] = []
    lists_of_scalars: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ] = []
    lists_of_enums: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ] = []
    enums: list[FieldName, str, SlotNumber, MaybeDefault] = []
    inlines: list[FieldName, ScalarType, SlotNumber, MaybeDefault] = []
    unions: list[tuple[FieldName, tuple[type, ...], UnionMapping, SlotNumber]] = []
    next_slot_idx = 0

    overridden = {f[0]: f for f in field_overrides}
    overridden_sl: dict[FieldName, ScalarType] = {
        f[0]: f[1] for f in scalar_list_overrides
    }

    for field in fields(cl):
        if field.name in overridden:
            f = overridden[field.name]
            if issubclass(field.type, IntEnum):
                enums.append((field.name, f[1], next_slot_idx, f[2]))
            else:
                inlines.append((field.name, f[1], next_slot_idx, f[2]))
            next_slot_idx += 1
            continue

        ftype = field.type
        if ftype is str:
            strings.append((field.name, next_slot_idx, False))
        elif ftype is bytes:
            byte_fields.append((field.name, next_slot_idx, False))
        elif has(ftype):
            tables.append((field.name, field.type, next_slot_idx, False))
        elif o := get_optional_arg(ftype):
            # This is an optional field.
            if o is str:
                strings.append((field.name, next_slot_idx, True))
            elif o is bytes:
                byte_fields.append((field.name, next_slot_idx, True))
            elif has(o):
                tables.append((field.name, o, next_slot_idx, True))
            elif is_generic_subclass(o, list):
                arg = o.__args__[0]
                if arg is str:
                    lists_of_strings.append((field.name, next_slot_idx, True))
                elif has(arg):
                    lists_of_tables.append((field.name, arg, next_slot_idx, True))
                elif arg in (
                    bool,
                    Uint8,
                    Uint16,
                    Uint32,
                    Uint64,
                    Int8,
                    Int16,
                    Int32,
                    int,
                    Float,
                    Float64,
                ):
                    lists_of_scalars.append(
                        (
                            field.name,
                            next_slot_idx,
                            arg,
                            overridden_sl.get(
                                field.name, HELPER_TYPE_TO_SCALAR_TYPE[arg]
                            ),
                            True,
                        )
                    )
                elif issubclass(arg, Enum) and issubclass(arg, int):
                    for helper_type, scalar_type in HELPER_TYPE_TO_SCALAR_TYPE.items():
                        if helper_type in arg.__mro__:
                            break
                    lists_of_enums.append(
                        (
                            field.name,
                            next_slot_idx,
                            arg,
                            overridden_sl.get(field.name, scalar_type),
                            True,
                        )
                    )
                else:
                    raise TypeError(f"Cannot handle {field.name} {ftype}")
            else:
                raise TypeError(f"Cannot handle {field.name} {ftype}")
        elif u := get_union_args(ftype):
            unions.append(
                (
                    field.name,
                    u,
                    union_overrides[field.name]
                    if field.name in union_overrides
                    else _make_union_mapping(u),
                    next_slot_idx,
                )
            )
            next_slot_idx += 1
        elif is_generic_subclass(ftype, list):
            arg = ftype.__args__[0]
            if arg is str:
                lists_of_strings.append((field.name, next_slot_idx, False))
            elif has(arg):
                lists_of_tables.append((field.name, arg, next_slot_idx, False))
            elif arg in HELPER_TYPE_TO_SCALAR_TYPE:
                lists_of_scalars.append(
                    (
                        field.name,
                        next_slot_idx,
                        arg,
                        overridden_sl.get(field.name, HELPER_TYPE_TO_SCALAR_TYPE[arg]),
                        False,
                    )
                )
            elif issubclass(arg, Enum) and issubclass(arg, int):
                for helper_type, scalar_type in HELPER_TYPE_TO_SCALAR_TYPE.items():
                    if helper_type in arg.__mro__:
                        break
                lists_of_enums.append(
                    (
                        field.name,
                        next_slot_idx,
                        arg,
                        overridden_sl.get(field.name, scalar_type),
                        False,
                    )
                )
            else:
                raise TypeError(f"Cannot handle {field.name} {ftype}")
        elif is_subclass(ftype, Enum) and is_subclass(
            ftype, int
        ):  # Enums before scalars, since IntEnum is a subclass of int.
            for helper_type, scalar_type in HELPER_TYPE_TO_SCALAR_TYPE.items():
                if helper_type in ftype.__mro__:
                    break
            enums.append(
                (
                    field.name,
                    scalar_type,
                    next_slot_idx,
                    field.default if field.default is not NOTHING else list(ftype)[0],
                )
            )
        elif is_subclass(ftype, (bool, Float, Float64, Uint8, Uint64, Int32, Int64)):
            inlines.append(
                (
                    field.name,
                    HELPER_TYPE_TO_SCALAR_TYPE[ftype],
                    next_slot_idx,
                    field.default,
                )
            )
        else:
            raise TypeError(f"Cannot handle {ftype}")

        next_slot_idx += 1
    return FlatbufferTable(
        cl,
        next_slot_idx,
        inlines,
        enums,
        strings,
        byte_fields,
        tables,
        lists_of_strings,
        lists_of_scalars,
        lists_of_enums,
        lists_of_tables,
        unions,
    )


def _make_union_mapping(union_types: tuple[type, ...]) -> UnionMapping:
    """Create a mapping of values to union members for use by the structuring logic."""
    res = {}

    curr_ix = 1
    for t in union_types:
        if t is NoneType:
            continue
        if union_val_and_base := get_annotation_and_base(t, UnionVal):
            union_val, base = union_val_and_base
            curr_ix = union_val
            t = base
        res[curr_ix] = t
        curr_ix += 1

    return res
