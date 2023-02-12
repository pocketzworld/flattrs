import hashlib
import linecache
from enum import Enum, unique
from importlib import import_module
from sys import modules
from typing import Any, Callable, Final, TypeVar

import attr
from attrs import NOTHING, AttrsInstance, define, fields

from ._analysis import analyze
from ._consts import SCALAR_TYPE_TO_DEFAULT, SCALAR_TYPE_TO_WIDTH, NoneType
from ._flatc import (
    get_num_slots_from_flatc_module,
    get_scalar_list_types,
    get_scalar_types,
    get_union_mapping_overrides,
)
from ._flatc import make_from_bytes_fn as flatc_make_from_bytes_fn
from ._flatc import make_from_fb_fn as flatc_make_from_fb_fn
from ._types import (
    FieldName,
    MaybeDefault,
    Optionality,
    PythonScalarType,
    ScalarType,
    SlotNumber,
    UnionMapping,
)
from .typing import get_union_args, resolve_types

try:
    from .cflattr.builder import Builder
except ImportError:
    from flatbuffers.builder import Builder

_T = TypeVar("_T")


def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: tuple[type | Callable[..., Any], ...] = (
        (attr.attrib, attr.field)
    ),
) -> Callable[[_T], _T]:
    return lambda c: c


@__dataclass_transform__()
def Flatbuffer(fb_cl, frozen: bool = False, repr: bool = True):
    def wrapper(cl):
        res = define(slots=True, frozen=frozen, repr=repr)(cl)
        res.__fb_module__ = modules[fb_cl.__module__]
        res.__fb_class__ = fb_cl
        num_slots = get_num_slots_from_flatc_module(res.__fb_module__)
        scalars = get_scalar_types(res, res.__fb_module__)
        scalar_list_overrides = get_scalar_list_types(res)
        union_overrides = get_union_mapping_overrides(res)
        _make_fb_functions(
            res,
            num_slots=num_slots,
            make_from_bytes_fn=flatc_make_from_bytes_fn,
            make_from_fb_fn=flatc_make_from_fb_fn,
            field_overrides=scalars,
            scalar_list_overrides=scalar_list_overrides,
            union_overrides=union_overrides,
        )

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
            if (
                not hasattr(fb_cl, member.name)
                or getattr(fb_cl, member.name) != member.value
            ):
                raise ValueError(f"{cl}/{member.name} doesn't match {fb_cl}.")

        return res

    return wrapper


@__dataclass_transform__()
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


def model_to_bytes(inst, builder: Builder | None = None) -> bytes:
    builder = Builder(10000) if builder is None else builder
    string_offsets = {}
    node_offsets = {}

    offset = inst.__fb_add_to_builder__(builder, string_offsets, node_offsets)

    builder.Finish(offset)  # Last offset.
    return bytes(builder.Output())


def model_from_bytes(cl: type[_T], payload: bytes) -> _T:
    """Deserialize an instance of `cl` from the given payload."""
    return cl.__fb_from_bytes__(payload)


class FBItemType(str, Enum):
    TABLE = "table"


FBItem = tuple[Any, FBItemType, Callable]


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


def _guess_num_slots(cl) -> int:
    """Guess the number of slots for an attrs class.

    Each attribute is one slot, unions being two.
    """
    return len(fields(cl)) + sum(get_union_args(a.type) is not None for a in fields(cl))


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
