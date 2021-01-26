import hashlib
import linecache
from collections.abc import Sequence
from enum import Enum, IntEnum, unique
from importlib import import_module
from sys import modules
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

import attr
from attr import fields, has
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

from ._compat import is_py36, is_py39plus

try:
    from .cflattr.builder import Builder
except ImportError:
    from flatbuffers.builder import Builder


UNION_CL = "__fb_union_cl"


def Flatbuffer(fb_cl, frozen: bool = False, repr: bool = True):
    def wrapper(cl):
        res = attr.s(slots=True, frozen=frozen, repr=repr)(cl)
        res.__fb_module__ = modules[fb_cl.__module__]
        res.__fb_class__ = fb_cl
        _make_fb_functions(res)

        return res

    return wrapper


def FlatbufferEnum(fb_cl):
    def wrapper(cl):
        res = unique(cl)
        res.__fb_module__ = modules[fb_cl.__module__]
        res.__fb_class__ = fb_cl

        if cl.__name__ != fb_cl.__name__:
            raise ValueError(f"Names don't match: {cl.__name__}/{fb_cl.__name__}.")

        for member in cl:
            if not hasattr(fb_cl, member.name):
                raise ValueError(f"{cl}/{member.name} doesn't match {fb_cl}.")

        return res

    return wrapper


def from_package(pkg, frozen: bool = False, repr: bool = True):
    def wrap_cls(cl):
        cl_name = cl.__name__
        module = import_module(f"{pkg.__package__}.{cl_name}")
        fb_cl = getattr(module, cl_name)
        return Flatbuffer(fb_cl, frozen=frozen, repr=repr)(cl)

    return wrap_cls


def from_package_enum(pkg):
    def wrap_cls(cl):
        cl_name = cl.__name__
        module = import_module(f"{pkg.__package__}.{cl_name}")
        fb_cl = getattr(module, cl_name)
        return FlatbufferEnum(fb_cl)(cl)

    return wrap_cls


Flatbuffer.from_package = from_package
FlatbufferEnum.from_package = from_package_enum


none_type = type(None)
if is_py36:

    def is_generic_subclass(t, s):
        return issubclass(t, s)


elif not is_py39plus:
    from typing import _GenericAlias

    def is_generic_subclass(t, s):
        return isinstance(t, _GenericAlias) and t.__origin__ is s


else:
    from types import GenericAlias
    from typing import _GenericAlias

    def is_generic_subclass(t, s):
        return (isinstance(t, _GenericAlias) and t.__origin__ is s) or (
            isinstance(t, GenericAlias) and t.__origin__ is s
        )


def _make_fb_functions(cl):
    """Inspect the given class for any non-nestable buffers.

    Non-nestables are other tables, strings and lists of non-nestables.
    """
    fn_name = "__fb_nonnestables__"
    strings = []
    optional_strings = []
    byte_fields = []
    optional_bytes = []
    tables = []
    optional_tables = []
    lists_of_tables = []
    seqs_of_tables = []
    lists_of_strings = []
    seqs_of_strings = []
    lists_of_scalars: List[Tuple[str, Type, Any, bool]] = []
    seqs_of_scalars: List[Tuple[str, Type, Any, bool]] = []
    lists_of_enums: List[Tuple[str, Type, Any, bool]] = []
    seqs_of_enums: List[Tuple[str, Type, Any, bool]] = []
    enums = []
    inlines = []
    unions: Tuple[str, List[Type], Any] = []
    for field in fields(cl):
        type = field.type
        if type is str:
            strings.append(field.name)
        elif type in (bytes, bytearray):
            byte_fields.append(field.name)
        elif has(type):
            tables.append(field.name)
        elif getattr(type, "__origin__", None) is Union:
            union_args = type.__args__
            if len(union_args) == 2 and none_type in union_args:
                # This is an optional field.
                if union_args[0] is str:
                    optional_strings.append(field.name)
                elif union_args[0] is bytes:
                    optional_bytes.append(field.name)
                elif has(union_args[0]):
                    optional_tables.append(field.name)
                elif is_generic_subclass(union_args[0], list):
                    arg = union_args[0].__args__[0]
                    if arg is str:
                        lists_of_strings.append(field.name)
                    elif has(arg):
                        lists_of_tables.append((field.name, arg))
                    elif arg in (int, float, bool):
                        lists_of_scalars.append(
                            (
                                field.name,
                                arg,
                                _get_scalar_list_type(cl, field.name)[0],
                                True,
                            )
                        )
                    elif issubclass(arg, IntEnum):
                        lists_of_enums.append(
                            (
                                field.name,
                                arg,
                                _get_scalar_list_type(cl, field.name)[0],
                                True,
                            )
                        )
                elif issubclass(union_args[0], IntEnum):
                    raise ValueError("Flatbuffers don't support optional enums.")
            else:
                unions.append((field.name, type.__args__, field.metadata[UNION_CL]))
        elif is_generic_subclass(type, list):
            arg = type.__args__[0]
            if arg is str:
                lists_of_strings.append(field.name)
            elif has(arg):
                lists_of_tables.append((field.name, arg))
            elif arg in (int, float, bool):
                lists_of_scalars.append(
                    (field.name, arg, _get_scalar_list_type(cl, field.name)[0], False)
                )
            elif issubclass(arg, IntEnum):
                lists_of_enums.append(
                    (field.name, arg, _get_scalar_list_type(cl, field.name)[0], False)
                )
        elif is_generic_subclass(type, Sequence):
            arg = type.__args__[0]
            if arg is str:
                seqs_of_strings.append(field.name)
            elif has(arg):
                seqs_of_tables.append((field.name, arg))
            elif arg in (int, float, bool):
                seqs_of_scalars.append(
                    (field.name, arg, _get_scalar_list_type(cl, field.name)[0], False)
                )
            elif issubclass(arg, IntEnum):
                seqs_of_enums.append(
                    (field.name, arg, _get_scalar_list_type(cl, field.name)[0], False)
                )
        elif issubclass(type, IntEnum):
            enums.append(field.name)
        else:
            inlines.append(field.name)

    setattr(
        cl,
        fn_name,
        _make_nonnestables_fn(
            cl,
            strings,
            optional_strings,
            byte_fields,
            tables,
            optional_tables,
            lists_of_tables + seqs_of_tables,
            lists_of_strings + seqs_of_strings,
            unions,
        ),
    )

    setattr(
        cl,
        "__fb_add_to_builder__",
        _make_add_to_builder_fn(
            cl,
            strings,
            optional_strings,
            byte_fields,
            optional_bytes,
            tables,
            optional_tables,
            lists_of_tables + seqs_of_tables,
            lists_of_strings + seqs_of_strings,
            lists_of_scalars + lists_of_enums + seqs_of_scalars + seqs_of_enums,
            inlines + enums,
            unions,
        ),
    )

    setattr(cl, "__fb_from_bytes__", _make_from_bytes_fn(cl))
    setattr(
        cl,
        "__fb_from_fb__",
        _make_from_fb_fn(
            cl,
            strings,
            optional_strings,
            byte_fields,
            optional_bytes,
            enums,
            tables,
            optional_tables,
            lists_of_tables,
            lists_of_strings,
            unions,
            inlines,
            lists_of_scalars,
            lists_of_enums,
            seqs_of_tables,
            seqs_of_scalars,
            seqs_of_enums,
            seqs_of_strings,
        ),
    )


def model_to_bytes(inst, builder: Optional[Builder] = None) -> bytes:
    builder = Builder(10000) if builder is None else builder
    fb_items = inst.__fb_nonnestables__()
    string_offsets = {}
    node_offsets = {}

    for fb_item, fb_type, fb_vec_start in fb_items:
        if fb_type is FBItemType.VECTOR:
            # Make a vector.
            fb_vec_start(builder, len(fb_item))
            for item in reversed(fb_item):
                builder.PrependUOffsetTRelative(node_offsets[id(item)])
            offset = builder.EndVector(len(fb_item))
            node_offsets[id(fb_item)] = offset
        else:
            item_id = id(fb_item)
            if item_id not in node_offsets:
                offset = fb_item.__fb_add_to_builder__(
                    builder, string_offsets, node_offsets
                )
                node_offsets[item_id] = offset

    builder.Finish(offset)  # Last offset.
    return bytes(builder.Output())


def model_from_bytes(cl, payload):
    return cl.__fb_from_bytes__(payload)


class FBItemType(str, Enum):
    TABLE = "table"
    VECTOR = "vector"


FBItem = Tuple[Any, FBItemType, Callable]

fb_number_type_to_builder_prepend = {
    BoolFlags: "PrependBool",
    Uint8Flags: "PrependUint8",
    Uint16Flags: "PrependUint16",
    Uint32Flags: "PrependUint32",
    Uint64Flags: "PrependUint64",
    Int8Flags: "PrependInt8",
    Int16Flags: "PrependInt16",
    Int32Flags: "PrependInt32",
    Int64Flags: "PrependInt64",
    Float32Flags: "PrependFloat32",
    Float64Flags: "PrependFloat64",
}


def _make_nonnestables_fn(
    cl,
    string_fields: List[str],
    optional_strings: List[str],
    byte_fields: List[str],
    table_fields: List[str],
    optional_tables: List[str],
    lists_of_tables: List[Tuple[str, Type]],
    lists_of_strings: List[str],
    unions: List[Tuple[str, List[Type], Type]],
) -> Callable[[], Tuple[Set[str], List[bytes], List[FBItem]]]:
    name = cl.__fb_class__.__name__
    mod = cl.__fb_module__
    globs = {"FBTable": FBItemType.TABLE, "FBVector": FBItemType.VECTOR}
    lines = []
    lines.append("def __fb_nonnestables__(self):")

    lines.append("    fb_items = []")

    for table_field in table_fields:
        lines.append(
            f"    {table_field}_items = self.{table_field}.__fb_nonnestables__()"
        )
        lines.append(f"    fb_items.extend({table_field}_items)")

    for table_field, union_classes, _ in unions:
        if none_type not in union_classes:
            lines.append(
                f"    {table_field}_items = self.{table_field}.__fb_nonnestables__()"
            )
            lines.append(f"    fb_items.extend({table_field}_items)")
        else:
            lines.append(f"    if self.{table_field} is not None:")
            lines.append(
                f"        {table_field}_items = self.{table_field}.__fb_nonnestables__()"
            )
            lines.append(f"        fb_items.extend({table_field}_items)")

    for table_field in optional_tables:
        lines.append(f"    if self.{table_field} is not None:")
        lines.append(
            f"        {table_field}_items = self.{table_field}.__fb_nonnestables__()"
        )
        lines.append(f"        fb_items.extend({table_field}_items)")

    for field, _ in lists_of_tables:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        globs[f"{field}VectorStart"] = getattr(
            mod, f"{cl.__name__}Start{norm_field_name}Vector"
        )

        lines.append(f"    {field}_items = self.{field}")
        lines.append(f"    for item in {field}_items:")
        lines.append(f"        i_is = item.__fb_nonnestables__()")
        lines.append(f"        fb_items.extend(i_is)")
        lines.append(f"    vec_start = {field}VectorStart")
        lines.append(f"    fb_items.append(({field}_items, FBVector, vec_start))")

    lines.append("    fb_items.append((self, FBTable, None))")

    lines.append("    return fb_items")

    sha1 = hashlib.sha1()
    sha1.update(name.encode("utf-8"))
    unique_filename = "<FB nonnestables for %s, %s>" % (name, sha1.hexdigest())
    script = "\n".join(lines)
    eval(compile(script, unique_filename, "exec"), globs)

    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )

    return globs["__fb_nonnestables__"]


def _make_add_to_builder_fn(
    cl,
    string_fields: List[str],
    optional_strings: List[str],
    byte_fields: List[str],
    optional_bytes: List[str],
    table_fields: List[str],
    optional_tables: List[str],
    lists_of_tables: List[Tuple[str, Type]],
    lists_of_strings: List[str],
    lists_of_scalars: List[Tuple[str, Type]],
    inlines: List[str],
    unions: List[Tuple[str, Type, Type]],
):
    name = cl.__fb_class__.__name__
    mod = cl.__fb_module__
    start = getattr(mod, f"{name}Start")
    num_slots = _get_num_slots(start)
    globs = {}
    lines = []
    lines.append("def __fb_add_to_builder__(self, builder, strs, nodes):")

    for field in string_fields:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(f"    if __fb_self_{field} not in strs:")
        lines.append(
            f"        strs[__fb_self_{field}] = builder.CreateString(__fb_self_{field})"
        )

    for field in optional_strings:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(
            f"    if __fb_self_{field} is not None and __fb_self_{field} not in strs:"
        )
        lines.append(
            f"        strs[__fb_self_{field}] = builder.CreateString(__fb_self_{field})"
        )

    for field in byte_fields:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(f"    if id(__fb_self_{field}) not in nodes:")
        lines.append(
            f"        nodes[id(__fb_self_{field})] = builder.CreateByteVector(__fb_self_{field})"
        )

    for field in optional_bytes:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(
            f"    if __fb_self_{field} is not None and id(__fb_self_{field}) not in nodes:"
        )
        lines.append(
            f"        nodes[id(__fb_self_{field})] = builder.CreateByteVector(__fb_self_{field})"
        )

    for field in lists_of_strings:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        globs[f"{field}StartVector"] = getattr(
            mod, f"{cl.__name__}Start{norm_field_name}Vector"
        )

        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(f"    __fb_self_{field}_offsets = []")
        lines.append(f"    for e in __fb_self_{field}:")
        lines.append(f"        if e in strs:")
        lines.append(f"            __fb_self_{field}_offsets.append(strs[e])")
        lines.append(f"        else:")
        lines.append(f"            offset = builder.CreateString(e)")
        lines.append(f"            strs[e] = offset")
        lines.append(f"            __fb_self_{field}_offsets.append(offset)")
        lines.append(f"    {field}StartVector(builder, len(__fb_self_{field}))")
        lines.append(f"    for o in reversed(__fb_self_{field}_offsets):")
        lines.append(f"        builder.PrependUOffsetTRelative(o)")
        lines.append(
            f"    __fb_self_{field}_offset = builder.EndVector(len(__fb_self_{field}))"
        )

    for field, _, fb_number_type, is_optional in lists_of_scalars:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        prepend = fb_number_type_to_builder_prepend[fb_number_type]
        globs[f"{field}StartVector"] = getattr(
            mod, f"{cl.__name__}Start{norm_field_name}Vector"
        )

        lines.append(f"    __fb_self_{field} = self.{field}")
        indent = ""
        if is_optional:
            lines.append(f"    if __fb_self_{field} is not None:")
            indent = "  "
        lines.append(f"    {indent}{field}StartVector(builder, len(__fb_self_{field}))")
        lines.append(f"    {indent}for o in reversed(__fb_self_{field}):")
        lines.append(f"    {indent}    builder.{prepend}(o)")
        lines.append(
            f"    {indent}__fb_self_{field}_offset = builder.EndVector(len(__fb_self_{field}))"
        )

    lines.append(f"    builder.StartObject({num_slots})")

    for field in string_fields:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        slot_num, default = _get_offsets_for_string(field_start)
        lines.append(
            f"    builder.PrependUOffsetTRelativeSlot({slot_num}, strs[__fb_self_{field}], {default})"
        )

    for field in optional_strings:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        globs[field_starter_name] = field_start
        lines.append(f"    if __fb_self_{field} is not None:")
        lines.append(f"        {field_starter_name}(builder, strs[__fb_self_{field}])")

    for field in byte_fields:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        slot_num, default = _get_offsets_for_string(field_start)
        lines.append(
            f"    builder.PrependUOffsetTRelativeSlot({slot_num}, nodes[id(__fb_self_{field})], {default})"
        )

    for field in optional_bytes:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        slot_num, default = _get_offsets_for_string(field_start)
        lines.append(f"    if __fb_self_{field} is not None:")
        lines.append(
            f"        builder.PrependUOffsetTRelativeSlot({slot_num}, nodes[id(__fb_self_{field})], {default})"
        )

    for field in lists_of_strings:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        globs[field_starter_name] = field_start
        lines.append(f"    {field_starter_name}(builder, __fb_self_{field}_offset)")

    for field in table_fields + [l[0] for l in lists_of_tables] + byte_fields:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        globs[field_starter_name] = field_start
        lines.append(f"    {field_starter_name}(builder, nodes[id(self.{field})])")

    for field, _, _, is_optional in lists_of_scalars:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        globs[field_starter_name] = field_start
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        else:
            prefix = ""
        lines.append(
            f"    {prefix}{field_starter_name}(builder, __fb_self_{field}_offset)"
        )

    for field in optional_tables:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        globs[field_starter_name] = field_start
        lines.append(f"    if self.{field} is not None:")
        lines.append(f"        {field_starter_name}(builder, nodes[id(self.{field})])")

    for field in inlines:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        globs[field_starter_name] = field_start
        lines.append(f"    {field_starter_name}(builder, self.{field})")

    for field, union_types, fb_enum in unions:
        norm_field_name = f"{field[0].upper()}{field[1:]}"
        type_adder_name = f"{name}Add{norm_field_name}Type"
        type_adder = getattr(mod, type_adder_name)
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)

        union_dict_name = f"{norm_field_name}_union_types"
        # Unions might be prefixed by a namespace string, depending on how
        # they're defined.
        stripped_union_dict = {k.split("_")[-1]: v for k, v in fb_enum.__dict__.items()}
        union_dict = {
            t: stripped_union_dict[t.__name__]
            for t in union_types
            if t is not none_type
        }
        # Flatbuffer unions always have a special member, NONE, signifying
        # a missing value. If None is part of union_types, we handle it
        # specially.
        if none_type in union_types:
            union_dict[none_type] = stripped_union_dict["NONE"]

        globs[type_adder_name] = type_adder
        globs[field_starter_name] = field_start
        globs[union_dict_name] = union_dict
        lines.append(
            f"    {type_adder_name}(builder, {union_dict_name}[self.{field}.__class__])"
        )
        if none_type in union_types:
            lines.append(f"    if self.{field} is not None:")
            lines.append(
                f"        {field_starter_name}(builder, nodes[id(self.{field})])"
            )
        else:
            lines.append(f"    {field_starter_name}(builder, nodes[id(self.{field})])")

    lines.append("    return builder.EndObject()")
    lines.append("")
    sha1 = hashlib.sha1()
    sha1.update(name.encode("utf-8"))
    unique_filename = "<FB add_to_builder for %s, %s>" % (name, sha1.hexdigest(),)
    script = "\n".join(lines)
    eval(compile(script, unique_filename, "exec"), globs)

    linecache.cache[unique_filename] = (
        len(script),
        None,
        script.splitlines(True),
        unique_filename,
    )

    return globs["__fb_add_to_builder__"]


def _make_from_bytes_fn(cl) -> Callable:
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


def _make_from_fb_fn(
    cl,
    string_fields: List[str],
    optional_strings: List[str],
    byte_fields: List[str],
    optional_bytes: List[str],
    enum_fields: List[str],
    table_fields: List[str],
    optional_tables: List[str],
    lists_of_tables: List[Tuple[str, Type]],
    lists_of_strings: List[str],
    union_fields: List[Tuple[str, List[Type], Type]],
    inlines: List[str],
    lists_of_scalars: List[Tuple[str, Type, Any, bool]],
    lists_of_enums: List[Tuple[str, Type, Any]],
    seqs_of_tables: List[Tuple[str, Type]],
    seqs_of_scalars: List[Tuple[str, Type]],
    seqs_of_enums: List[Tuple[str, Type]],
    seqs_of_strings: List[str],
) -> Callable:
    """Compile a function to init an attrs model from a FB model."""
    name = cl.__fb_class__.__name__
    globs = {}
    lines = []
    table_field_names = {t[0]: t[1] for t in lists_of_tables}
    seq_table_field_names = {t[0]: t[1] for t in seqs_of_tables}
    union_field_names = {t[0]: t for t in union_fields}
    lists_of_scalar_names = {t[0]: t[1] for t in lists_of_scalars}
    seqs_of_scalar_names = {t[0]: t[1] for t in seqs_of_scalars}
    lists_of_enum_names = {t[0]: t for t in lists_of_enums}
    seqs_of_enum_names = {t[0]: t for t in seqs_of_enums}

    optionals = {f[0] for f in lists_of_scalars if f[3]}

    from_fb = "__fb_from_fb__"
    lines.append("@classmethod")
    lines.append("def __fb_from_fb__(cls, fb_instance):")
    for fname in optional_bytes:
        norm_field_name = f"{fname[0].upper()}{fname[1:]}"
        lines.append(f"    __fb_{fname} = fb_instance.{norm_field_name}AsNumpy()")
    lines.append("    return cls(")
    for field in fields(cl):
        fname = field.name
        norm_field_name = f"{fname[0].upper()}{fname[1:]}"
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
        elif fname in enum_fields:
            enum_name = field.type.__name__
            globs[enum_name] = field.type
            lines.append(f"        {enum_name}(fb_instance.{norm_field_name}()),")
        elif fname in table_fields:
            table_name = field.type.__name__
            globs[table_name] = field.type
            lines.append(
                f"        {table_name}.{from_fb}(fb_instance.{norm_field_name}()),"
            )
        elif fname in optional_tables:
            cl = field.type.__args__[0]
            table_name = cl.__name__
            globs[table_name] = cl
            lines.append(
                f"        {table_name}.{from_fb}(fb_instance.{norm_field_name}()) if fb_instance.{norm_field_name}() is not None else None,"
            )
        elif fname in table_field_names:
            type = table_field_names[fname]
            tn = type.__name__
            globs[tn] = type
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            lines.append(
                f"        [{tn}.{from_fb}(fb_instance.{norm_field_name}(i)) {for_}],"
            )
        elif fname in seq_table_field_names:
            type = seq_table_field_names[fname]
            tn = type.__name__
            globs[tn] = type
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            lines.append(
                f"        tuple({tn}.{from_fb}(fb_instance.{norm_field_name}(i)) {for_}),"
            )
        elif fname in lists_of_strings:
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            lines.append(
                f"        [fb_instance.{norm_field_name}(i).decode('utf8') {for_}],"
            )
        elif fname in seqs_of_strings:
            for_ = f"for i in range(fb_instance.{norm_field_name}Length())"
            lines.append(
                f"        tuple(fb_instance.{norm_field_name}(i).decode('utf8') {for_}),"
            )
        elif fname in inlines:
            type = field.type
            globs[f"_{fname}_type"] = type
            lines.append(f"        _{fname}_type(fb_instance.{norm_field_name}()),")
        elif fname in union_field_names:
            # We prepare a dictionary to select the proper class at runtime.
            # Then we just grab the proper type and instantiate it.
            _, union_types, union_enum = union_field_names[fname]
            dn = f"_{fname}_union_dict"
            union_resolution_dict = {}
            stripped_union_dict: Dict[str, Any] = {
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
                line = (
                    f"{line} if int(fb_instance._tab.Offset({offset})) != 0 else None"
                )
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


def _get_num_slots(fn) -> int:
    class DummyBuilder:
        def StartObject(self, slot_num):
            self.slot_num = slot_num

    d = DummyBuilder()
    fn(d)
    return d.slot_num


def _get_offsets_for_string(fn) -> Tuple[int, int]:
    sentinel = 1024

    class DummyBuilder:
        def PrependUOffsetTRelativeSlot(self, slot_num, offset, default):
            if offset is not sentinel:
                raise ValueError("Failed extracting parameters.")
            self.slot_num = slot_num
            self.default = default

    d = DummyBuilder()
    fn(d, sentinel)
    return d.slot_num, d.default


def _get_scalar_list_type(cl, fname: str) -> Tuple[Any, int]:
    """Fish out the scalar type and field offset for a lists of scalars."""

    class DummyTab:
        def Offset(self, offset):
            self.field_offset = offset
            return 1

        def GetVectorAsNumpy(self, number_type, _):
            self.scalar_type = number_type
            return object()

    tab = DummyTab()
    inst = cl.__fb_class__()
    inst._tab = tab
    norm_field_name = f"{fname[0].upper()}{fname[1:]}"
    getattr(inst, f"{norm_field_name}AsNumpy")()

    return tab.scalar_type, tab.field_offset
