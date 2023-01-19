"""Functionality for the `flatc` backend."""
import hashlib
import linecache
from enum import IntEnum, ReprEnum
from re import sub
from typing import Any, Callable, Final, List, Tuple, Type

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

from ._types import FieldName, MaybeDefault, Optionality, ScalarType, SlotNumber
from .typing import get_list_args, is_subclass

none_type = type(None)


def make_from_bytes_fn(cl) -> Callable:
    """Compile a function to load this model from Flatbuffer bytes."""
    name = cl.__fb_class__.__name__
    globs = {"_fb_cls_loader": getattr(cl.__fb_class__, f"GetRootAs{name}")}
    lines = []
    lines.append("@classmethod")
    lines.append("def __fb_from_bytes__(cls, data):")
    lines.append("    fb_model = _fb_cls_loader(data, 0)")
    lines.append("    return cls.__fb_from_fb__(fb_model)")

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


def make_from_fb_fn(
    cl,
    string_fields: List[str],
    optional_strings: List[str],
    byte_fields: List[str],
    optional_bytes: List[str],
    enum_fields: list[tuple[str, str, int]],
    table_fields: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_tables: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_strings: List[Tuple[str, bool]],
    union_fields: List[Tuple[str, List[Type], Type]],
    inlines: list[tuple[str, str, int]],
    lists_of_scalars: List[Tuple[str, Type, Any, bool]],
    lists_of_enums: List[Tuple[str, Type, Any]],
    seqs_of_tables: List[Tuple[str, Type, bool]],
    seqs_of_scalars: List[Tuple[str, Type]],
    seqs_of_enums: List[Tuple[str, Type]],
    seqs_of_strings: List[Tuple[str, bool]],
) -> Callable:
    """Compile a function to init an attrs model from a FB model."""
    name = cl.__fb_class__.__name__
    globs = {}
    lines = []
    list_table_fields = {t[0]: t for t in lists_of_tables}
    seq_table_fields = {t[0]: t for t in seqs_of_tables}
    union_field_names = {t[0]: t for t in union_fields}
    lists_of_scalar_names = {t[0]: t[1] for t in lists_of_scalars}
    seqs_of_scalar_names = {t[0]: t[1] for t in seqs_of_scalars}
    lists_of_enum_names = {t[0]: t for t in lists_of_enums}
    seqs_of_enum_names = {t[0]: t for t in seqs_of_enums}
    lists_of_strings_names = {t[0]: t[1] for t in lists_of_strings}
    seqs_of_strings_names = {t[0]: t[1] for t in seqs_of_strings}
    inline_names = {i[0] for i in inlines}
    enum_names = {e[0] for e in enum_fields}
    table_field_names = {t[0]: t for t in table_fields}

    optionals = {f[0] for f in lists_of_scalars if f[3]}

    from_fb = "__fb_from_fb__"
    lines.append("@classmethod")
    lines.append("def __fb_from_fb__(cls, fb_instance):")
    for fname in optional_bytes:
        norm_field_name = _normalize_fn(fname)
        lines.append(f"    __fb_{fname} = fb_instance.{norm_field_name}AsNumpy()")
    lines.append("    return cls(")
    for field in fields(cl):
        fname = field.name
        norm_field_name = _normalize_fn(fname)
        if fname in string_fields:
            lines.append(f"        fb_instance.{norm_field_name}().decode('utf8'),")
        elif fname in optional_strings:
            lines.append(
                f"        fb_instance.{norm_field_name}().decode('utf8') if fb_instance.{norm_field_name}() is not None else None,"
            )
        elif fname in byte_fields:
            lines.append(f"        fb_instance.{norm_field_name}AsNumpy().tobytes(),")
        elif fname in optional_bytes:
            lines.append(
                f"        __fb_{fname}.tobytes() if not isinstance(__fb_{fname}, int) else None,"
            )
        elif fname in enum_names:
            enum_name = field.type.__name__
            globs[enum_name] = field.type
            lines.append(f"        {enum_name}(fb_instance.{norm_field_name}()),")
        elif fname in table_field_names:
            table_def = table_field_names[fname]
            table_name = table_def[1].__name__
            globs[table_name] = table_def[1]
            suffix = ""
            if table_def[3]:
                suffix = f" if fb_instance.{norm_field_name}() is not None else None"
            lines.append(
                f"        {table_name}.{from_fb}(fb_instance.{norm_field_name}()){suffix},"
            )
        elif fname in list_table_fields:
            _, type, _, is_optional = list_table_fields[fname]
            tn = type.__name__
            globs[tn] = type

            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            line = f"        [{tn}.{from_fb}(fb_instance.{norm_field_name}(i)) {for_}]"

            if is_optional:
                # We need the field offset since the Python bindings hide them.
                offset = _get_table_list_offset(cl, fname)
                # We adjust the previous line a little
                line = f"{line} if fb_instance._tab.Offset({offset}) != 0 else None"
            lines.append(f"{line},")
        elif fname in seq_table_fields:
            _, type, is_optional = seq_table_fields[fname]
            tn = type.__name__
            globs[tn] = type
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            line = f"        tuple({tn}.{from_fb}(fb_instance.{norm_field_name}(i)) {for_})"
            if is_optional:
                # We need the field offset since the Python bindings hide them.
                offset = _get_table_list_offset(cl, fname)
                # We adjust the previous line a little
                line = (
                    f"{line} if int(fb_instance._tab.Offset({offset})) != 0 else None"
                )
            lines.append(f"{line},")
        elif fname in lists_of_strings_names:
            is_optional = lists_of_strings_names[fname]
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            line = f"        [fb_instance.{norm_field_name}(i).decode('utf8') {for_}]"
            if is_optional:
                offset = _get_table_list_offset(cl, fname)
                # We adjust the previous line a little
                line = (
                    f"{line} if int(fb_instance._tab.Offset({offset})) != 0 else None"
                )
            lines.append(f"{line},")
        elif fname in seqs_of_strings_names:
            is_optional = seqs_of_strings_names[fname]
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            line = (
                f"        tuple(fb_instance.{norm_field_name}(i).decode('utf8') {for_})"
            )
            if is_optional:
                offset = _get_table_list_offset(cl, fname)
                # We adjust the previous line a little
                line = (
                    f"{line} if int(fb_instance._tab.Offset({offset})) != 0 else None"
                )
            lines.append(f"{line},")
        elif fname in inline_names:
            type = field.type
            globs[f"_{fname}_type"] = type
            lines.append(f"        _{fname}_type(fb_instance.{norm_field_name}()),")
        elif fname in union_field_names:
            # We prepare a dictionary to select the proper class at runtime.
            # Then we just grab the proper type and instantiate it.
            _, union_types, union_enum, slot_num = union_field_names[fname]
            dn = f"_{fname}_union_dict"
            union_resolution_dict = {}
            stripped_union_dict: dict[str, Any] = {
                k.split("_")[-1]: v for k, v in union_enum.__dict__.items()
            }

            for union_type in [u for u in union_types if u is not none_type]:
                # Unions might be prefixed by a namespace string, depending on how
                # they're defined.
                code = stripped_union_dict[union_type.__name__]
                fb_cls = union_type.__fb_class__
                attr_model = union_type

                def _load_from_content(table, attr_model=attr_model, fb_cls=fb_cls):
                    res = fb_cls()
                    res.Init(table.Bytes, table.Pos)
                    return attr_model.__fb_from_fb__(res)

                union_resolution_dict[code] = _load_from_content

            if none_type in union_types:
                none_code = getattr(union_enum, "NONE")
                union_resolution_dict[none_code] = lambda _: None

            globs[dn] = union_resolution_dict
            lines.append(
                f"        {dn}[fb_instance.{norm_field_name}Type()](fb_instance.{norm_field_name}()),"
            )
        elif fname in lists_of_scalar_names:
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            line = f"        [fb_instance.{norm_field_name}(i) {for_}]"
            if fname in optionals:
                # We need the field offset since the Python bindings hide them.
                _, offset = _get_scalar_list_type(cl, fname)
                # We adjust the previous line a little
                line = f"{line} if fb_instance._tab.Offset({offset}) != 0 else None"
            lines.append(line + ", ")
        elif fname in seqs_of_scalar_names:
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            lines.append(f"        tuple(fb_instance.{norm_field_name}(i) {for_}),")
        elif fname in lists_of_enum_names:
            enum_type = lists_of_enum_names[fname][1]
            dn = f"_{fname}_enum"
            globs[dn] = enum_type
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            lines.append(f"        [{dn}(fb_instance.{norm_field_name}(i)) {for_}],")
        elif fname in seqs_of_enum_names:
            enum_type = seqs_of_enum_names[fname][1]
            dn = f"_{fname}_enum"
            globs[dn] = enum_type
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            lines.append(
                f"        tuple({dn}(fb_instance.{norm_field_name}(i)) {for_}),"
            )
        else:
            raise ValueError(f"Can't handle {fname} (type {field.type}).")

    lines.append("    )")
    lines.append("")

    sha1 = hashlib.sha1()
    sha1.update(name.encode("utf-8"))
    unique_filename = "<FB from_fb for %s, %s>" % (name, sha1.hexdigest())
    script = "\n".join(lines)
    eval(compile(script, unique_filename, "exec"), globs)

    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )

    return globs["__fb_from_fb__"]


def _normalize_fn(fname: str) -> str:
    """The name needs to be capitalized.

    If there are two or more consecutive capitals:
    * the cluster is title-cased (isNPC -> isNpc)
    If there is an underscore, it is replaced by camelCase
    * simple_ubyte -> simpleUbytes
    """
    res = sub("[A-Z]+", lambda m: m.group(0).title(), fname)
    res = sub("_[a-z]", lambda m: m.group(0)[1:].title(), res)
    # Title-casing needs to happen after the caps processing.
    res = f"{fname[0].upper()}{res[1:]}"
    return res


def get_scalar_list_types(cl) -> list[tuple[FieldName, ScalarType]]:
    res = []
    for field in fields(cl):
        if (args := get_list_args(field.type)) and args[0] in (bool, int, float):
            st = _get_scalar_list_type(cl, field.name)
            res.append((field.name, FLAGS_TO_SCALAR_TYPE[st[0]]))
    return res


def get_scalar_types(cl, mod) -> list[tuple[FieldName, ScalarType, MaybeDefault]]:
    scalars = []
    for field in fields(cl):
        if field.type in (bool, float, int) or (
            is_subclass(field.type, ReprEnum) and is_subclass(field.type, int)
        ):
            scalar_type, default = _get_scalar_type(mod, field.name)
            scalars.append((field.name, scalar_type, default))
    return scalars


def _get_scalar_type(fb_module, fname: str) -> tuple[str, str]:
    """Fish out the scalar type from the flatc-generated code."""

    class DummyBuilder:
        def PrependBoolSlot(self, slot_num, value, default):
            self.type = "Bool"
            self.default = default

        def PrependUint8Slot(self, slot_num, value, default):
            self.type = "Uint8"
            self.default = default

        def PrependUint16Slot(self, slot_num, value, default):
            self.type = "Uint16"
            self.default = default

        def PrependUint32Slot(self, slot_num, value, default):
            self.type = "Uint32"
            self.default = default

        def PrependUint64Slot(self, slot_num, value, default):
            self.type = "Uint64"
            self.default = default

        def PrependInt8Slot(self, slot_num, value, default):
            self.type = "Int8"
            self.default = default

        def PrependInt16Slot(self, slot_num, value, default):
            self.type = "Int16"
            self.default = default

        def PrependInt32Slot(self, slot_num, value, default):
            self.type = "Int32"
            self.default = default

        def PrependInt64Slot(self, slot_num, value, default):
            self.type = "Int64"
            self.default = default

        def PrependFloat32Slot(self, slot_num, value, default):
            self.type = "Float32"
            self.default = default

        def PrependFloat64Slot(self, slot_num, value, default):
            self.type = "Float64"
            self.default = default

    adder = getattr(fb_module, f"Add{_normalize_fn(fname)}")

    b = DummyBuilder()
    adder(b, None)

    return b.type, b.default


def _get_scalar_list_type(cl, fname: str) -> Tuple[Any, int]:
    """Fish out the scalar type and field offset for a lists of scalars."""

    class DummyTab:
        def Offset(self, offset):
            self.field_offset = offset
            return 1

        def GetVectorAsNumpy(self, number_flags, _):
            self.scalar_type = number_flags
            return object()

    tab = DummyTab()
    inst = cl.__fb_class__()
    inst._tab = tab
    norm_field_name = _normalize_fn(fname)
    getattr(inst, f"{norm_field_name}AsNumpy")()

    return tab.scalar_type, tab.field_offset


def _get_table_list_offset(cl, fname: str) -> int:
    class DummyTab:
        def Offset(self, offset):
            self.field_offset = offset
            return 0

    tab = DummyTab()
    inst = cl.__fb_class__()
    inst._tab = tab
    norm_field_name = _normalize_fn(fname)
    getattr(inst, f"{norm_field_name}Length")()

    return tab.field_offset


def _get_num_slots_from_flatc_module(mod) -> int:
    """Fish out the number of slots from a flatc module."""
    starter = mod.Start
    return _get_num_slots(starter)


def _get_num_slots(fn) -> int:
    class DummyBuilder:
        def StartObject(self, slot_num):
            self.slot_num = slot_num

    d = DummyBuilder()
    fn(d)
    return d.slot_num


FLAGS_TO_SCALAR_TYPE: Final[dict[type, ScalarType]] = {
    Uint8Flags: "Uint8",
    Uint16Flags: "Uint16",
    Uint32Flags: "Uint32",
    Uint64Flags: "Uint64",
    Int8Flags: "Int8",
    Int16Flags: "Int16",
    Int32Flags: "Int32",
    Int64Flags: "Int64",
    Float32Flags: "Float32",
    Float64Flags: "Float64",
    BoolFlags: "Bool",
}
