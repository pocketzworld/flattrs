import hashlib
import linecache
from collections.abc import Sequence
from enum import Enum, IntEnum, unique
from importlib import import_module
from sys import modules
from types import UnionType
from typing import Any, Callable, Final, List, Optional, Set, Type, TypeVar, Union

import attr
from attrs import NOTHING, define, fields, has

from ._consts import SCALAR_TYPE_TO_DEFAULT
from ._flatc import (
    _get_num_slots_from_flatc_module,
    _get_scalar_list_type,
    _normalize_fn,
    get_scalar_list_types,
    get_scalar_types,
)
from ._flatc import make_from_bytes_fn as flatc_make_from_bytes_fn
from ._flatc import make_from_fb_fn as flatc_make_from_fb_fn
from ._flattrs import make_from_bytes_flattrs_fn
from ._flattrs import make_from_fb_fn as flattrs_make_from_fb_fn
from ._types import (
    FieldName,
    MaybeDefault,
    Optionality,
    PythonScalarType,
    ScalarType,
    SlotNumber,
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
)
from .typing import (
    get_optional_arg,
    get_union_args,
    is_annotated_with,
    is_generic_subclass,
)

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
    field_descriptors: tuple[Union[type, Callable[..., Any]], ...] = (
        (attr.attrib, attr.field)
    ),
) -> Callable[[_T], _T]:
    return lambda c: c


UNION_CL = "__fb_union_cl"


@__dataclass_transform__()
def flattrs(cl=None, *, frozen: bool = False, repr: bool | None = None):
    if cl is not None:
        # Direct application
        return flattrs(frozen=frozen, repr=repr)(cl)

    def wrapper(cl):
        res = define(slots=True, frozen=frozen, repr=repr)(cl)
        num_slots = _guess_num_slots(res)
        _make_fb_functions(
            res,
            num_slots=num_slots,
            make_from_bytes_fn=make_from_bytes_flattrs_fn,
            make_from_fb_fn=flattrs_make_from_fb_fn,
        )

        return res

    return wrapper


@__dataclass_transform__()
def Flatbuffer(fb_cl, frozen: bool = False, repr: bool = True):
    def wrapper(cl):
        res = define(slots=True, frozen=frozen, repr=repr)(cl)
        res.__fb_module__ = modules[fb_cl.__module__]
        res.__fb_class__ = fb_cl
        num_slots = _get_num_slots_from_flatc_module(res.__fb_module__)
        scalars = get_scalar_types(res, res.__fb_module__)
        scalar_list_overrides = get_scalar_list_types(res)
        _make_fb_functions(
            res,
            num_slots=num_slots,
            make_from_bytes_fn=flatc_make_from_bytes_fn,
            make_from_fb_fn=flatc_make_from_fb_fn,
            field_overrides=scalars,
            scalar_list_overrides=scalar_list_overrides,
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


none_type = type(None)


def _make_fb_functions(
    cl,
    num_slots: int,
    make_from_bytes_fn: Callable[[Any], Callable],
    make_from_fb_fn: Callable,
    field_overrides: list[tuple[FieldName, ScalarType, MaybeDefault]] = [],
    scalar_list_overrides: list[tuple[FieldName, ScalarType]] = [],
) -> None:
    """Inspect the given class for any non-nestable buffers.

    Non-nestables are other tables, strings and lists of non-nestables.
    """
    fn_name = "__fb_nonnestables__"
    strings: list[tuple[FieldName, SlotNumber]] = []
    optional_strings = []
    byte_fields = []
    optional_bytes = []
    tables: list[tuple[FieldName, type, SlotNumber, Optionality]] = []
    lists_of_tables: list[tuple[FieldName, type, SlotNumber, Optionality]] = []
    seqs_of_tables: List[tuple[str, Type, bool]] = []
    lists_of_strings: List[tuple[str, bool]] = []
    seqs_of_strings: List[tuple[str, bool]] = []
    lists_of_scalars: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ] = []
    seqs_of_scalars: List[
        tuple[FieldName, SlotNumber, PythonScalarType, Any, bool]
    ] = []
    lists_of_enums: List[tuple[str, Type, Any, bool]] = []
    seqs_of_enums: List[tuple[str, Type, Any, bool]] = []
    enums: list[FieldName, str, SlotNumber, MaybeDefault] = []
    inlines: list[FieldName, ScalarType, SlotNumber, MaybeDefault] = []
    unions: tuple[FieldName, List[Type], Any, SlotNumber] = []
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
            strings.append((field.name, next_slot_idx))
            next_slot_idx += 1
        elif ftype in (bytes, bytearray):
            byte_fields.append((field.name, next_slot_idx))
            next_slot_idx += 1
        elif has(ftype):
            tables.append((field.name, field.type, next_slot_idx, False))
            next_slot_idx += 1
        elif o := get_optional_arg(ftype):
            # This is an optional field.
            if o is str:
                optional_strings.append((field.name, next_slot_idx))
                next_slot_idx += 1
            elif o is bytes:
                optional_bytes.append((field.name, next_slot_idx))
                next_slot_idx += 1
            elif has(o):
                tables.append((field.name, o, next_slot_idx, True))
                next_slot_idx += 1
            elif is_generic_subclass(o, list):
                arg = o.__args__[0]
                if arg is str:
                    lists_of_strings.append((field.name, True))
                elif has(arg):
                    lists_of_tables.append((field.name, arg, next_slot_idx, True))
                    next_slot_idx += 1
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
                    next_slot_idx += 1
                elif issubclass(arg, IntEnum):
                    lists_of_enums.append(
                        (
                            field.name,
                            arg,
                            _get_scalar_list_type(cl, field.name)[0],
                            True,
                        )
                    )
            elif is_generic_subclass(o, Sequence):
                arg = o.__args__[0]
                if arg is str:
                    seqs_of_strings.append((field.name, True))
                elif has(arg):
                    seqs_of_tables.append((field.name, arg, True))
                elif arg in (int, float, bool):
                    seqs_of_scalars.append(
                        (
                            field.name,
                            next_slot_idx,
                            arg,
                            _get_scalar_list_type(cl, field.name)[0],
                            True,
                        )
                    )
                    next_slot_idx += 1
                elif issubclass(arg, IntEnum):
                    seqs_of_enums.append(
                        (
                            field.name,
                            arg,
                            _get_scalar_list_type(cl, field.name)[0],
                            True,
                        )
                    )
            elif issubclass(o, IntEnum):
                raise ValueError("Flatbuffers don't support optional enums.")
        elif u := get_union_args(ftype):
            unions.append((field.name, u, field.metadata[UNION_CL], next_slot_idx))
            next_slot_idx += 2
        elif is_generic_subclass(ftype, list):
            arg = ftype.__args__[0]
            if arg is str:
                lists_of_strings.append((field.name, False))
            elif has(arg):
                lists_of_tables.append((field.name, arg, next_slot_idx, False))
                next_slot_idx += 1
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
                next_slot_idx += 1
            elif issubclass(arg, IntEnum):
                lists_of_enums.append(
                    (field.name, arg, _get_scalar_list_type(cl, field.name)[0], False)
                )
        elif is_generic_subclass(ftype, Sequence):
            arg = ftype.__args__[0]
            if arg is str:
                seqs_of_strings.append((field.name, False))
            elif has(arg):
                seqs_of_tables.append((field.name, arg, False))
            elif arg in (int, float, bool):
                seqs_of_scalars.append(
                    (
                        field.name,
                        next_slot_idx,
                        arg,
                        "Uint8",
                        False,
                    )
                )
                next_slot_idx += 1
            elif issubclass(arg, IntEnum):
                seqs_of_enums.append(
                    (field.name, arg, _get_scalar_list_type(cl, field.name)[0], False)
                )
        elif is_annotated_with(ftype, Float):
            inlines.append((field.name, "Float32", next_slot_idx, field.default))
            next_slot_idx += 1
        elif issubclass(ftype, Enum) and issubclass(
            ftype, int
        ):  # Enums before scalars, since IntEnum is a subclass of int.
            for helper_type, scalar_type in HELPER_TYPE_TO_SCALAR_TYPE.items():
                if helper_type in ftype.__mro__:
                    break
            else:
                raise TypeError(f"Cannot handle enum {ftype}")
            enums.append(
                (
                    field.name,
                    scalar_type,
                    next_slot_idx,
                    field.default if field.default is not NOTHING else list(ftype)[0],
                )
            )
            next_slot_idx += 1
        elif issubclass(ftype, (bool, Float, Float64, Uint8, Uint64, Int32, Int64)):
            inlines.append(
                (
                    field.name,
                    HELPER_TYPE_TO_SCALAR_TYPE[ftype],
                    next_slot_idx,
                    field.default,
                )
            )
            next_slot_idx += 1
        else:
            raise Exception(f"Cannot handle {ftype}")

    setattr(
        cl,
        fn_name,
        _make_nonnestables_fn(
            cl,
            tables,
            unions,
        ),
    )

    setattr(
        cl,
        "__fb_add_to_builder__",
        _make_add_to_builder_fn(
            cl,
            num_slots,
            strings,
            optional_strings,
            byte_fields,
            optional_bytes,
            tables,
            lists_of_tables + seqs_of_tables,
            lists_of_strings + seqs_of_strings,
            lists_of_scalars + lists_of_enums + seqs_of_scalars + seqs_of_enums,
            inlines + enums,
            unions,
        ),
    )

    setattr(cl, "__fb_from_bytes__", make_from_bytes_fn(cl))
    setattr(
        cl,
        "__fb_from_fb__",
        make_from_fb_fn(
            cl,
            [s[0] for s in strings],
            [s[0] for s in optional_strings],
            [s[0] for s in byte_fields],
            [s[0] for s in optional_bytes],
            enums,
            tables,
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
            offset = builder.EndVector()
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


def model_from_bytes(cl: type[_T], payload: bytes) -> _T:
    """Deserialize an instance of `cl` from the given payload."""
    return cl.__fb_from_bytes__(payload)


class FBItemType(str, Enum):
    TABLE = "table"
    VECTOR = "vector"


FBItem = tuple[Any, FBItemType, Callable]


def _make_nonnestables_fn(
    cl,
    table_fields: list[FieldName, type, SlotNumber, Optionality],
    unions: list[tuple[FieldName, tuple[type, ...], type, SlotNumber]],
) -> Callable[[], tuple[Set[str], List[bytes], List[FBItem]]]:
    name = cl.__name__
    globs = {"FBTable": FBItemType.TABLE, "FBVector": FBItemType.VECTOR}
    lines = []
    lines.append("def __fb_nonnestables__(self):")

    lines.append("    fb_items = []")

    for table_field, _, _, is_optional in table_fields:
        indent = ""
        if is_optional:
            lines.append(f"    if self.{table_field} is not None:")
            indent = "    "
        lines.append(
            f"    {indent}{table_field}_items = self.{table_field}.__fb_nonnestables__()"
        )
        lines.append(f"    {indent}fb_items.extend({table_field}_items)")

    for table_field, union_classes, _, _ in unions:
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
    num_slots: int,
    string_fields: list[tuple[str, SlotNumber]],
    optional_strings: list[tuple[str, SlotNumber]],
    byte_fields: list[tuple[FieldName, SlotNumber]],
    optional_bytes: list[tuple[FieldName, SlotNumber]],
    table_fields: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_tables: list[tuple[FieldName, type, SlotNumber, Optionality]],
    lists_of_strings: list[tuple[FieldName, Optionality]],
    lists_of_scalars: list[
        tuple[FieldName, SlotNumber, PythonScalarType, ScalarType, Optionality]
    ],
    scalars: list[tuple[FieldName, ScalarType, SlotNumber, MaybeDefault]],
    unions: list[tuple[FieldName, tuple[type, ...], Type, SlotNumber]],
):
    name = cl.__name__
    globs = {}
    lines = []
    lines.append("def __fb_add_to_builder__(self, builder, strs, nodes):")

    for field, slot_idx in string_fields:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(f"    if __fb_self_{field} not in strs:")
        lines.append(
            f"        strs[__fb_self_{field}] = builder.CreateString(__fb_self_{field})"
        )

    for field, slot_idx in optional_strings:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(
            f"    if __fb_self_{field} is not None and __fb_self_{field} not in strs:"
        )
        lines.append(
            f"        strs[__fb_self_{field}] = builder.CreateString(__fb_self_{field})"
        )

    for field, slot_idx in byte_fields:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(f"    if id(__fb_self_{field}) not in nodes:")
        lines.append(
            f"        nodes[id(__fb_self_{field})] = builder.CreateByteVector(__fb_self_{field})"
        )

    for field, slot_idx in optional_bytes:
        lines.append(f"    __fb_self_{field} = self.{field}")
        lines.append(
            f"    if __fb_self_{field} is not None and id(__fb_self_{field}) not in nodes:"
        )
        lines.append(
            f"        nodes[id(__fb_self_{field})] = builder.CreateByteVector(__fb_self_{field})"
        )

    for field, is_optional in lists_of_strings:
        mod = cl.__fb_module__
        norm_field_name = _normalize_fn(field)
        globs[f"{field}StartVector"] = getattr(
            mod, f"{cl.__name__}Start{norm_field_name}Vector"
        )

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
        lines.append(f"{i}    {field}StartVector(builder, len(__fb_self_{field}))")
        lines.append(f"{i}    for o in reversed(__fb_self_{field}_offsets):")
        lines.append(f"{i}        builder.PrependUOffsetTRelative(o)")
        lines.append(f"{i}    __fb_self_{field}_offset = builder.EndVector()")

    for field, _, _, fb_number_type, is_optional in lists_of_scalars:
        prepend = SCALAR_TYPE_TO_PREPEND[fb_number_type]

        lines.append(f"    __fb_self_{field} = self.{field}")
        indent = ""
        if is_optional:
            lines.append(f"    if __fb_self_{field} is not None:")
            indent = "  "
        lines.append(f"    {indent}builder.StartVector(1, len(self.{field}), 1)")
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

    lines.append(f"    builder.StartObject({num_slots})")

    for field, slot_idx in string_fields:
        lines.append(
            f"    builder.PrependUOffsetTRelativeSlot({slot_idx}, strs[__fb_self_{field}], 0)"
        )

    for field, slot_idx in optional_strings:
        lines.append(f"    if __fb_self_{field} is not None:")
        lines.append(
            f"        builder.PrependUOffsetTRelativeSlot({slot_idx}, strs[__fb_self_{field}], 0)"
        )

    for field, slot_idx in byte_fields:
        lines.append(
            f"    builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(__fb_self_{field})], 0)"
        )

    for field, slot_idx in optional_bytes:
        lines.append(f"    if __fb_self_{field} is not None:")
        lines.append(
            f"        builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(__fb_self_{field})], 0)"
        )

    for field, is_optional in lists_of_strings:
        norm_field_name = _normalize_fn(field)
        field_starter_name = f"{name}Add{norm_field_name}"
        field_start = getattr(mod, field_starter_name)
        globs[field_starter_name] = field_start
        prefix = ""
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        lines.append(
            f"    {prefix}{field_starter_name}(builder, __fb_self_{field}_offset)"
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

    for field, union_types, fb_enum, slot_idx in unions:
        union_dict_name = f"_{field}_union_types"
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

        globs[union_dict_name] = union_dict
        lines.append(
            f"    builder.PrependUint8Slot({slot_idx}, {union_dict_name}[self.{field}.__class__], 0)"
        )
        indent = ""
        if none_type in union_types:
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
    print(script)
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
    return len(fields(cl)) + sum(
        getattr(a.type, "__origin__", None) is Union for a in fields(cl)
    )


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
