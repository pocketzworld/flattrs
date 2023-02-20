"""Functionality for the `flatc` backend."""
import hashlib
import linecache
from enum import Enum
from re import sub
from typing import Any, Callable, Final, Type, TypeVar

from attrs import NOTHING, AttrsInstance, fields
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

from flattrs._analysis import analyze
from flattrs._consts import (
    HELPER_TYPE_TO_SCALAR_TYPE,
    SCALAR_TYPE_TO_DEFAULT,
    SCALAR_TYPE_TO_WIDTH,
    NoneType,
)
from flattrs._types import (
    FieldName,
    MaybeDefault,
    Optionality,
    PythonScalarType,
    ScalarType,
    SlotNumber,
    UnionMapping,
)
from flattrs.typing import get_list_args, get_union_args, is_subclass

try:
    from flattrs.cflattr.builder import Builder
except ImportError:
    from flatbuffers.builder import Builder

_T = TypeVar("_T")
UNION_CL: Final = "_fb_union"


def _make_fb_functions(
    cl: type[AttrsInstance],
    num_slots: int,
    make_from_bytes_fn: Callable[[Any], Callable],
    make_from_fb_fn: Callable,
    field_overrides: list[tuple[FieldName, ScalarType, MaybeDefault]] = [],
    scalar_list_overrides: list[tuple[FieldName, ScalarType]] = [],
    union_overrides: dict[FieldName, UnionMapping] = {},
) -> None:
    """Generate all necessary functions for a class to work with Flatbuffers."""
    fb_cls = analyze(cl, field_overrides, scalar_list_overrides, union_overrides)

    setattr(
        cl,
        "__fb_add_to_builder__",
        _make_add_to_builder_fn(
            cl,
            num_slots,
            fb_cls.strings,
            fb_cls.byte_fields,
            fb_cls.tables,
            fb_cls.lists_of_tables,
            fb_cls.lists_of_strings,
            fb_cls.lists_of_scalars + fb_cls.lists_of_enums,
            fb_cls.inlines + fb_cls.enums,
            fb_cls.unions,
        ),
    )

    setattr(cl, "__fb_from_bytes__", make_from_bytes_fn(cl))
    setattr(
        cl,
        "__fb_from_fb__",
        make_from_fb_fn(
            cl,
            fb_cls.strings,
            fb_cls.byte_fields,
            fb_cls.enums,
            fb_cls.tables,
            fb_cls.lists_of_tables,
            fb_cls.lists_of_strings,
            fb_cls.unions,
            fb_cls.inlines,
            fb_cls.lists_of_scalars,
            fb_cls.lists_of_enums,
        ),
    )


def _make_add_to_builder_fn(
    cl: type,
    num_slots: int,
    string_fields: list[tuple[FieldName, SlotNumber, Optionality]],
    byte_fields: list[tuple[FieldName, SlotNumber, Optionality]],
    table_fields: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_tables: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_strings: list[tuple[FieldName, SlotNumber, Optionality]],
    lists_of_scalars: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ],
    scalars: list[tuple[FieldName, ScalarType, SlotNumber, MaybeDefault]],
    unions: list[tuple[FieldName, tuple[type, ...], UnionMapping, SlotNumber]],
) -> Callable[[Any, Builder, dict[int, int], dict[int, int]], int]:
    name = cl.__name__
    globs = {}
    lines = []
    lines.append("def __fb_add_to_builder__(self, builder, strs, nodes):")

    for field, slot_idx, is_optional in string_fields:
        lines.append(f"    __fb_self_{field} = self.{field}")
        if is_optional:
            lines.append(
                f"    if __fb_self_{field} is not None and __fb_self_{field} not in strs:"
            )
        else:
            lines.append(f"    if __fb_self_{field} not in strs:")

        lines.append(
            f"        strs[__fb_self_{field}] = builder.CreateString(__fb_self_{field})"
        )

    for field, slot_idx, is_optional in byte_fields:
        lines.append(f"    __fb_self_{field} = self.{field}")
        infix = ""
        if is_optional:
            infix = f"__fb_self_{field} is not None and "
        lines.append(f"    if {infix}id(__fb_self_{field}) not in nodes:")
        lines.append(
            f"        nodes[id(__fb_self_{field})] = builder.CreateByteVector(__fb_self_{field})"
        )

    for field, _, is_optional in lists_of_strings:
        lines.append(f"    __fb_self_{field} = self.{field}")
        i = ""
        if is_optional:
            i = "    "
            lines.append(f"    if __fb_self_{field} is not None:")

        lines.append(f"{i}    __fb_self_{field}_offsets = []")
        lines.append(f"{i}    for e in __fb_self_{field}:")
        lines.append(f"{i}        if e in strs:")
        lines.append(f"{i}            __fb_self_{field}_offsets.append(strs[e])")
        lines.append(f"{i}        else:")
        lines.append(f"{i}            offset = builder.CreateString(e)")
        lines.append(f"{i}            strs[e] = offset")
        lines.append(f"{i}            __fb_self_{field}_offsets.append(offset)")
        lines.append(f"{i}    builder.StartVector(4, len(__fb_self_{field}), 4)")
        lines.append(f"{i}    for o in reversed(__fb_self_{field}_offsets):")
        lines.append(f"{i}        builder.PrependUOffsetTRelative(o)")
        lines.append(f"{i}    __fb_self_{field}_offset = builder.EndVector()")

    for field, _, _, fb_number_type, is_optional in lists_of_scalars:
        prepend = SCALAR_TYPE_TO_PREPEND[fb_number_type]
        w = SCALAR_TYPE_TO_WIDTH[fb_number_type]

        lines.append(f"    __fb_self_{field} = self.{field}")
        indent = ""
        if is_optional:
            lines.append(f"    if __fb_self_{field} is not None:")
            indent = "  "
        lines.append(f"    {indent}builder.StartVector({w}, len(self.{field}), {w})")
        lines.append(f"    {indent}for o in reversed(__fb_self_{field}):")
        lines.append(f"    {indent}    builder.{prepend}(o)")
        lines.append(f"    {indent}__fb_self_{field}_offset = builder.EndVector()")

    for field, _, slot_idx, is_optional in lists_of_tables:
        lines.append(f"    __fb_self_{field} = self.{field}")

        indent = ""
        if is_optional:
            lines.append(f"    if __fb_self_{field} is not None:")
            indent = "    "

        lines.append(
            f"    {indent}offsets = [t.__fb_add_to_builder__(builder, strs, nodes) for t in __fb_self_{field}]"
        )
        lines.append(f"    {indent}builder.StartVector(4, len(offsets), 4)")
        lines.append(
            f"    {indent}for o in reversed(offsets): builder.PrependUOffsetTRelative(o)"
        )
        lines.append(f"    {indent}nodes[id(__fb_self_{field})] = builder.EndVector()")

    for field, _, _, is_optional in table_fields:
        prefix = ""
        if is_optional:
            prefix = f"if self.{field} is not None: "
        lines.append(
            f"    {prefix}nodes[id(self.{field})] = self.{field}.__fb_add_to_builder__(builder, strs, nodes)"
        )

    for field, union_members, _, _ in unions:
        prefix = ""
        is_optional = NoneType in union_members
        if is_optional:
            prefix = f"if self.{field} is not None: "
        lines.append(
            f"    {prefix}nodes[id(self.{field})] = self.{field}.__fb_add_to_builder__(builder, strs, nodes)"
        )

    # The actual object starts here.
    lines.append(f"    builder.StartObject({num_slots})")

    for field, slot_idx, is_optional in string_fields:
        indent = ""
        if is_optional:
            lines.append(f"    if __fb_self_{field} is not None:")
            indent = "    "
        lines.append(
            f"    {indent}builder.PrependUOffsetTRelativeSlot({slot_idx}, strs[__fb_self_{field}], 0)"
        )

    for field, slot_idx, is_optional in byte_fields:
        prefix = ""
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        lines.append(
            f"    {prefix}builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(__fb_self_{field})], 0)"
        )

    for field, slot_idx, is_optional in lists_of_strings:
        prefix = ""
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        lines.append(
            f"    {prefix}builder.PrependUOffsetTRelativeSlot({slot_idx}, __fb_self_{field}_offset, 0)"
        )

    for field, _, slot_idx, is_optional in table_fields:
        indent = ""
        if is_optional:
            lines.append(f"    if self.{field} is not None:")
            indent = "    "
        lines.append(
            f"    {indent}builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(self.{field})], 0)"
        )

    for field, _, slot_idx, is_optional in lists_of_tables:
        lines.append(f"    __fb_self_{field} = self.{field}")
        if is_optional:
            indent = f"if __fb_self_{field} is not None: "
        else:
            indent = ""
        lines.append(
            f"    {indent}builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(__fb_self_{field})], 0)"
        )

    for field, slot_idx, _, _, is_optional in lists_of_scalars:
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        else:
            prefix = ""
        lines.append(
            f"    {prefix}builder.PrependUOffsetTRelativeSlot({slot_idx}, __fb_self_{field}_offset, 0)"
        )

    for field, fb_type, slot_idx, default in scalars:
        if default is NOTHING:
            default = SCALAR_TYPE_TO_DEFAULT[fb_type]
        lines.append(
            f"    builder.Prepend{fb_type}Slot({slot_idx}, self.{field}, {default})"
        )

    for field, union_types, union_mapping, slot_idx in unions:
        union_dict_name = f"_{field}_union_types"
        # Unions might be prefixed by a namespace string, depending on how
        # they're defined.
        # stripped_union_dict = {k.split("_")[-1]: v for k, v in fb_enum.__dict__.items()}

        union_dict = {t: ix for ix, t in union_mapping.items() if t is not NoneType}
        # Flatbuffer unions always have a special member, NONE, signifying
        # a missing value. If None is part of union_types, we handle it
        # specially.
        if NoneType in union_types:
            union_dict[NoneType] = 0

        globs[union_dict_name] = union_dict
        lines.append(
            f"    builder.PrependUint8Slot({slot_idx}, {union_dict_name}[self.{field}.__class__], 0)"
        )
        indent = ""
        if NoneType in union_types:
            lines.append(f"    if self.{field} is not None:")
            indent = "    "
        lines.append(
            f"    {indent}builder.PrependUOffsetTRelativeSlot({slot_idx+1}, nodes[id(self.{field})], 0)"
        )

    lines.append("    return builder.EndObject()")
    lines.append("")
    sha1 = hashlib.sha1()
    sha1.update(name.encode("utf-8"))
    unique_filename = "<FB add_to_builder for %s, %s>" % (
        name,
        sha1.hexdigest(),
    )
    script = "\n".join(lines)
    eval(compile(script, unique_filename, "exec"), globs)

    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )

    return globs["__fb_add_to_builder__"]


SCALAR_TYPE_TO_PREPEND: Final[dict[ScalarType, str]] = {
    "Bool": "PrependBool",
    "Uint8": "PrependUint8",
    "Uint16": "PrependUint16",
    "Uint32": "PrependUint32",
    "Uint64": "PrependUint64",
    "Int8": "PrependInt8",
    "Int16": "PrependInt16",
    "Int32": "PrependInt32",
    "Int64": "PrependInt64",
    "Float32": "PrependFloat32",
    "Float64": "PrependFloat64",
}


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
    string_fields: list[tuple[FieldName, SlotNumber, Optionality]],
    byte_fields: list[tuple[str, SlotNumber, Optionality]],
    enum_fields: list[tuple[str, str, int]],
    table_fields: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_tables: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_strings: list[tuple[FieldName, SlotNumber, Optionality]],
    union_fields: list[tuple[FieldName, tuple[type, ...], UnionMapping, SlotNumber]],
    inlines: list[tuple[str, str, int]],
    lists_of_scalars: list[tuple[FieldName, Type, Any, Optionality]],
    lists_of_enums: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ],
) -> Callable:
    """Compile a function to init an attrs model from a FB model."""
    name = cl.__fb_class__.__name__
    globs = {}
    lines = []
    byte_names = {f[0]: f for f in byte_fields}
    string_names = {s[0]: s for s in string_fields}
    list_table_fields = {t[0]: t for t in lists_of_tables}
    union_field_names = {t[0]: t for t in union_fields}
    lists_of_scalar_names = {t[0]: t[1] for t in lists_of_scalars}
    lists_of_enum_names = {t[0]: t for t in lists_of_enums}
    lists_of_strings_names = {t[0]: t for t in lists_of_strings}
    inline_names = {i[0] for i in inlines}
    enum_names = {e[0] for e in enum_fields}
    table_field_names = {t[0]: t for t in table_fields}

    optionals = {f[0] for f in lists_of_scalars if f[3]}

    from_fb = "__fb_from_fb__"
    lines.append("@classmethod")
    lines.append("def __fb_from_fb__(cls, fb_instance):")
    for fname, _, is_optional in byte_fields:
        if is_optional:
            norm_field_name = _normalize_fn(fname)
            lines.append(f"    __fb_{fname} = fb_instance.{norm_field_name}AsNumpy()")
    lines.append("    return cls(")
    for field in fields(cl):
        fname = field.name
        norm_field_name = _normalize_fn(fname)
        if fname in string_names:
            string_def = string_names[fname]
            if string_def[2]:
                lines.append(
                    f"        fb_instance.{norm_field_name}().decode('utf8') if fb_instance.{norm_field_name}() is not None else None,"
                )
            else:
                lines.append(f"        fb_instance.{norm_field_name}().decode('utf8'),")
        elif fname in byte_names:
            byte_def = byte_names[fname]
            if byte_def[2]:
                lines.append(
                    f"        __fb_{fname}.tobytes() if not isinstance(__fb_{fname}, int) else None,"
                )
            else:
                lines.append(
                    f"        fb_instance.{norm_field_name}AsNumpy().tobytes(),"
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
        elif fname in lists_of_strings_names:
            is_optional = lists_of_strings_names[fname][2]
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            line = f"        [fb_instance.{norm_field_name}(i).decode('utf8') {for_}]"
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
            _, _, union_mapping, _ = union_field_names[fname]
            dn = f"_{fname}_union_dict"
            union_resolution_dict = {}

            for ix, union_type in union_mapping.items():
                if union_type is NoneType:
                    union_resolution_dict[0] = lambda _: None
                    continue
                fb_cls = union_type.__fb_class__
                attr_model = union_type

                def _load_from_content(table, attr_model=attr_model, fb_cls=fb_cls):
                    res = fb_cls()
                    res.Init(table.Bytes, table.Pos)
                    return attr_model.__fb_from_fb__(res)

                union_resolution_dict[ix] = _load_from_content

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
        elif fname in lists_of_enum_names:
            list_def = lists_of_enum_names[fname]
            enum_type = list_def[2]
            dn = f"_{fname}_enum"
            globs[dn] = enum_type
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            line = f"[{dn}(fb_instance.{norm_field_name}(i)) {for_}]"
            if list_def[4]:
                _, offset = _get_scalar_list_type(cl, fname)
                line = f"{line} if fb_instance._tab.Offset({offset}) != 0 else None"
            lines.append(line + ", ")
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
    """For numbers and enums."""
    res = []
    for field in fields(cl):
        if args := get_list_args(field.type):
            arg = args[0]
            if arg in (bool, int, float):
                st = _get_scalar_list_type(cl, field.name)
                res.append((field.name, FLAGS_TO_SCALAR_TYPE[st[0]]))
            elif issubclass(arg, Enum) and issubclass(arg, int):
                for helper_type, scalar_type in HELPER_TYPE_TO_SCALAR_TYPE.items():
                    if helper_type in arg.__mro__:
                        break
                else:
                    raise TypeError(f"Cannot handle enum {arg}")
                st = _get_scalar_list_type(cl, field.name)
                res.append(
                    (
                        field.name,
                        FLAGS_TO_SCALAR_TYPE[st[0]],
                    )
                )
    return res


def get_scalar_types(cl, mod) -> list[tuple[FieldName, ScalarType, MaybeDefault]]:
    scalars = []
    for field in fields(cl):
        if field.type in (bool, float, int) or (
            is_subclass(field.type, Enum) and is_subclass(field.type, int)
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


def _get_scalar_list_type(cl, fname: str) -> tuple[Any, int]:
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


def get_num_slots_from_flatc_module(mod) -> int:
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


def get_union_mapping_overrides(cl) -> dict[FieldName, UnionMapping]:
    """Fish out the flatc union mapping."""
    res = {}
    for field in fields(cl):
        if UNION_CL in field.metadata:
            union_args = get_union_args(field.type)
            union_dict = {a.__name__: a for a in union_args}
            flatc_mapping = field.metadata[UNION_CL]
            mapping = {}
            for k, v in flatc_mapping.__dict__.items():
                if not isinstance(v, int):
                    continue
                if v == 0:
                    mapping[0] = NoneType
                    continue
                # Unions may be prefixed by their namespace.
                k = k.split("_")[-1]
                mapping[v] = union_dict[k]
            res[field.name] = mapping
    return res


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
