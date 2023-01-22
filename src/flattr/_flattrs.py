import hashlib
import linecache
from typing import Any, Callable, Final

from attrs import NOTHING, fields
from flatbuffers.number_types import (
    BoolFlags,
    Float32Flags,
    Float64Flags,
    Int8Flags,
    Int16Flags,
    Int32Flags,
    Int64Flags,
    Uint8Flags,
    Uint16Flags,
    Uint32Flags,
    Uint64Flags,
)
from flatbuffers.table import Table

from ._consts import SCALAR_TYPE_TO_DEFAULT, SCALAR_TYPE_TO_PYTHON
from ._types import (
    FieldName,
    MaybeDefault,
    Optionality,
    PythonScalarType,
    ScalarType,
    SlotNumber,
    UnionMapping,
)

none_type = type(None)


def make_from_fb_fn(
    cl,
    string_fields: list[tuple[FieldName, SlotNumber, Optionality]],
    byte_fields: list[str],
    optional_bytes: list[str],
    enum_fields: list[tuple[FieldName, ScalarType, SlotNumber, MaybeDefault]],
    table_fields: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_tables: list[tuple[str, type, bool]],
    lists_of_strings: list[tuple[FieldName, SlotNumber, Optionality]],
    union_fields: list[tuple[FieldName, tuple[type, ...], UnionMapping, SlotNumber]],
    inlines: list[tuple[FieldName, ScalarType, SlotNumber, MaybeDefault]],
    lists_of_scalars: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ],
    lists_of_enums: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ],
) -> Callable:
    """Compile a function to init an attrs model from a FB model, flattrs-style.

    The input is assumed to be an instance of `flatbuffers.Table`.
    """
    name = cl.__name__
    globs = {"_Table": Table}
    lines = []
    inst_lines = []  # Instantiation lines
    string_names = {s[0]: s for s in string_fields}
    list_table_fields = {t[0]: t for t in lists_of_tables}
    union_field_names = {t[0]: t for t in union_fields}
    lists_of_scalar_names = {t[0]: t for t in lists_of_scalars + lists_of_enums}
    lists_of_strings_names = {t[0]: t for t in lists_of_strings}
    inline_names = {t[0]: t for t in inlines}
    enum_names = {e[0]: e for e in enum_fields}
    table_names = {t[0]: t for t in table_fields}

    from_fb = "__fb_from_fb__"
    lines.append("@classmethod")
    lines.append("def __fb_from_fb__(cls, tab):")

    inst_lines.append("    return cls(")
    field_offset = 4
    for field in fields(cl):
        fname = field.name
        if fname in string_names:
            string_def = string_names[fname]
            if string_def[2]:
                inst_lines.append(
                    f"        tab.String(tab.Pos + o).decode() if (o := tab.Offset({field_offset})) != 0 else None,"
                )
            else:
                inst_lines.append(
                    f"        tab.String(tab.Pos + tab.Offset({field_offset})).decode(),"
                )
            field_offset += 2
        elif fname in byte_fields:
            inst_lines.append(
                f"        tab.String(tab.Pos + tab.Offset({field_offset})),"
            )
            field_offset += 2
        elif fname in optional_bytes:
            inst_lines.append(
                f"        tab.String(tab.Pos + o) if (o := tab.Offset({field_offset})) != 0 else None,"
            )
            field_offset += 2
        elif fname in enum_names:
            _, fb_type, slot_idx, default = enum_names[fname]
            globs[f"_{fname}_type"] = field.type
            globs[f"_{fname}_flags"] = SCALAR_TYPES_TO_FLAGS[fb_type]
            inst_lines.append(
                f"        _{fname}_type(tab.Get(_{fname}_flags, tab.Pos + o) if (o := tab.Offset({field_offset})) != 0 else {default}),"
            )
            field_offset += 2
        elif fname in table_names:
            table_def = table_names[fname]
            tn = table_def[1].__name__
            globs[tn] = table_def[1]
            lines.append(f"    _{fname}_offset = tab.Offset({4 + table_def[2] * 2})")
            suffix = ""
            if table_def[3]:
                suffix = f" if _{fname}_offset != 0 else None"
            inst_lines.append(
                f"        {tn}.{from_fb}(tab.__class__(tab.Bytes, tab.Indirect(_{fname}_offset + tab.Pos))){suffix},"
            )
            field_offset += 2
        elif fname in list_table_fields:
            _, type, slot_idx, is_optional = list_table_fields[fname]
            tn = type.__name__
            globs[tn] = type
            lines.append(f"    _{fname}_offset = tab.Offset({4 + slot_idx * 2})")
            lines.append(
                f"    _{fname}_vector = tab.Vector(_{fname}_offset) if _{fname}_offset != 0 else None"
            )
            for_ = f"for i in range(tab.VectorLen(_{fname}_offset) if _{fname}_offset != 0 else 0)"
            line = f"        [{tn}.{from_fb}(tab.__class__(tab.Bytes, tab.Indirect(_{fname}_vector + 4 * i))) {for_}]"

            if is_optional:
                line = f"{line} if _{fname}_offset != 0 else None"
            inst_lines.append(f"{line},")
        elif fname in lists_of_strings_names:
            list_def = lists_of_strings_names[fname]
            is_optional = list_def[2]
            slot_idx = list_def[1]
            lines.append(f"    _{fname}_offset = tab.Offset({4 + slot_idx * 2})")
            lines.append(
                f"    _{fname}_vector = tab.Vector(_{fname}_offset) if _{fname}_offset != 0 else None"
            )
            for_ = f"for i in range(tab.VectorLen(_{fname}_offset))"
            line = f"        [tab.String(_{fname}_vector + i * 4).decode() {for_}]"
            if is_optional:
                # We adjust the previous line a little
                line = f"{line} if _{fname}_offset != 0 else None"
            inst_lines.append(f"{line},")
        elif fname in inline_names:
            inline = inline_names[fname]
            globs[f"_{fname}_type"] = SCALAR_TYPE_TO_PYTHON[inline[1]]
            globs[f"_{fname}_flags"] = SCALAR_TYPES_TO_FLAGS[inline[1]]
            if inline[3] is not NOTHING:
                globs[f"_{fname}_default"] = inline[3]
                default = f"_{fname}_default"
            else:
                default = SCALAR_TYPE_TO_DEFAULT[inline[1]]
            inst_lines.append(
                f"        _{fname}_type(tab.Get(_{fname}_flags, tab.Pos + o)) if (o := tab.Offset({field_offset})) != 0 else {default},"
            )
            field_offset += 2
        elif fname in union_field_names:
            # We prepare a dictionary to select the proper class at runtime.
            # Then we just grab the proper type and instantiate it.
            _, union_types, union_mapping, slot_idx = union_field_names[fname]
            dn = f"_{fname}_union_dict"
            union_resolution_dict = {}

            for ix, union_type in union_mapping.items():
                # Unions might be prefixed by a namespace string, depending on how
                # they're defined.
                attr_model = union_type

                def _load_from_content(table: Table, o, attr_model=attr_model):
                    obj = Table(bytearray(), 0)
                    table.Union(obj, o)
                    return attr_model.__fb_from_fb__(obj)

                union_resolution_dict[ix] = _load_from_content

            globs[dn] = union_resolution_dict
            globs[f"_{fname}_flags"] = Uint8Flags
            lines.append(f"    _{fname}_offset = tab.Offset({4 + slot_idx * 2})")
            if none_type in union_types:
                inst_lines.append(
                    f"        {dn}[tab.Get(_{fname}_flags, _{fname}_offset + tab.Pos)](tab, tab.Offset({6 + slot_idx * 2})) if _{fname}_offset != 0 else None,"
                )
            else:
                inst_lines.append(
                    f"        {dn}[tab.Get(_{fname}_flags, _{fname}_offset + tab.Pos) if _{fname}_offset != 0 else None](tab, tab.Offset({6 + slot_idx * 2})),"
                )
        elif fname in lists_of_scalar_names:
            list_def = lists_of_scalar_names[fname]
            flags = SCALAR_TYPES_TO_FLAGS[list_def[3]]
            globs[f"_{fname}_flags"] = flags
            globs[f"_{fname}_type"] = list_def[2]
            lines.append(f"    _{fname}_offset = tab.Offset({4 + list_def[1] * 2})")
            lines.append(
                f"    _{fname}_vector = tab.Vector(_{fname}_offset) if _{fname}_offset != 0 else None"
            )
            for_ = f"for i in range(tab.VectorLen(_{fname}_offset) if _{fname}_offset != 0 else 0)"
            i = "i" if flags.bytewidth == 1 else f"i * {flags.bytewidth}"
            line = f"        [_{fname}_type(tab.Get(_{fname}_flags, _{fname}_vector + {i})) {for_}]"
            if list_def[4]:
                # We adjust the previous line a little
                line = f"{line} if _{fname}_offset != 0 else None"
            inst_lines.append(line + ", ")
            field_offset += 2
        else:
            raise ValueError(f"Can't handle {fname} (type {field.type}).")

    inst_lines.append("    )")

    sha1 = hashlib.sha1()
    sha1.update(name.encode("utf-8"))
    unique_filename = "<FB from_fb for %s, %s>" % (name, sha1.hexdigest())
    script = "\n".join(lines + inst_lines)
    eval(compile(script, unique_filename, "exec"), globs)

    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )

    return globs["__fb_from_fb__"]


def make_from_bytes_flattrs_fn(cl) -> Callable:
    """Compile a function to load this model from Flatbuffer bytes."""
    import struct

    from flatbuffers.table import Table

    name = cl.__name__
    globs = {
        "Table": Table,
        "uint32": struct.Struct("<I"),
    }
    lines = []
    lines.append("@classmethod")
    lines.append("def __fb_from_bytes__(cls, data: bytes):")
    lines.append("    start_offset = uint32.unpack_from(data, 0)[0]")
    lines.append("    return cls.__fb_from_fb__(Table(data, start_offset))")

    lines.append("")
    sha1 = hashlib.sha1()
    sha1.update(name.encode("utf-8"))
    unique_filename = "<FB from_bytes for %s, %s>" % (name, sha1.hexdigest())
    script = "\n".join(lines)
    eval(compile(script, unique_filename, "exec"), globs)

    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )

    return globs["__fb_from_bytes__"]


SCALAR_TYPES_TO_FLAGS: Final[dict[ScalarType, type]] = {
    "Float32": Float32Flags,
    "Float64": Float64Flags,
    "Uint8": Uint8Flags,
    "Uint16": Uint16Flags,
    "Uint32": Uint32Flags,
    "Uint64": Uint64Flags,
    "Int8": Int8Flags,
    "Int16": Int16Flags,
    "Int32": Int32Flags,
    "Int64": Int64Flags,
    "Bool": BoolFlags,
}
