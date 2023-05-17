import hashlib
import linecache
import struct
from functools import cache
from typing import Any, Callable, Final, TypeAlias, TypeVar

from attrs import NOTHING, AttrsInstance, Factory, define, fields
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

from ._analysis import FlatbufferTable, analyze
from ._consts import (
    SCALAR_TYPE_TO_DEFAULT,
    SCALAR_TYPE_TO_PYTHON,
    SCALAR_TYPE_TO_WIDTH,
    NoneType,
)
from ._types import ScalarType
from .types import UnionVal
from .typing import get_annotation_and_base

try:
    from .cflattrs.builder import Builder
except ImportError:  # NOQA
    from flatbuffers.builder import Builder

T = TypeVar("T", bound=AttrsInstance)
AddToBuilder: TypeAlias = Callable[[T, Builder, dict[int, int], dict[int, int]], int]
start_struct: Final = struct.Struct("<I")


@define
class Converter:
    """A converter for loading and dumping Flatbuffers."""

    _dumps_cache: Callable = Factory(
        lambda self: cache(lambda cls: self.make_dumps(cls)), takes_self=True
    )
    _to_fb_cache: Callable[[type[T]], AddToBuilder] = Factory(
        lambda self: cache(
            lambda cls: _make_add_to_builder_fn(analyze(cls), self._to_fb_cache)
        ),
        takes_self=True,
    )
    _from_fb_cache: Callable[[type[T]], Callable] = Factory(
        lambda self: cache(lambda cls: self._make_from_fb(cls)), takes_self=True
    )
    _loads_cache: Callable = Factory(
        lambda self: cache(lambda cls: self.make_loads(cls)), takes_self=True
    )

    def loads(self, payload: bytes, cl: type[T]) -> T:
        return self._loads_cache(cl)(payload)

    def dumps(self, model: AttrsInstance, builder: Builder | None = None) -> bytes:
        return self._dumps_cache(model.__class__)(model, builder)

    def _make_from_fb(self, cl: type[AttrsInstance]) -> Callable:
        """Generate all necessary functions for a class to work with Flatbuffers."""
        return make_from_fb_fn(analyze(cl), self._from_fb_cache)

    def make_loads(self, cl: type[T]) -> Callable[[bytes], T]:
        """Prepare a loading function for a model in advance."""
        from_fb = self._from_fb_cache(cl)

        def loads(
            data: bytes, _from_fb=from_fb, _unpack_from=start_struct.unpack_from
        ) -> T:
            start_offset = _unpack_from(data, 0)[0]
            return _from_fb(Table(data, start_offset))

        return loads

    def make_dumps(self, cl: type[T]) -> Callable[[T, Builder | None], bytes]:
        """Prepare a dumping function for a model in advance."""

        fb_cl = analyze(cl)

        add_to_builder = _make_add_to_builder_fn(fb_cl, self._to_fb_cache)

        def dumps(model: T, builder: Builder | None = None) -> bytes:
            builder = Builder(10000) if builder is None else builder
            offset = add_to_builder(model, builder, {}, {})
            builder.Finish(offset)
            return builder.Output()

        return dumps


def _make_add_to_builder_fn(
    cl: FlatbufferTable,
    hook_factory: Callable[[type[AttrsInstance]], AddToBuilder[Any]],
) -> AddToBuilder[Any]:
    name = cl.cl.__name__
    globs = {}
    lines = []
    lines.append("def __fb_add_to_builder__(self, builder, strs, nodes):")

    for field, slot_idx, is_optional in cl.strings:
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

    for field, slot_idx, is_optional in cl.byte_fields:
        lines.append(f"    __fb_self_{field} = self.{field}")
        infix = ""
        if is_optional:
            infix = f"__fb_self_{field} is not None and "
        lines.append(f"    if {infix}id(__fb_self_{field}) not in nodes:")
        lines.append(
            f"        nodes[id(__fb_self_{field})] = builder.CreateByteVector(__fb_self_{field})"
        )

    for field, _, is_optional in cl.lists_of_strings:
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

    for field, _, _, fb_number_type, is_optional in (
        cl.lists_of_scalars + cl.lists_of_enums
    ):
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

    for field, type, slot_idx, is_optional in cl.lists_of_tables:
        globs[f"_{field}_add_to_builder"] = hook_factory(type)
        lines.append(f"    __fb_self_{field} = self.{field}")

        indent = ""
        if is_optional:
            lines.append(f"    if __fb_self_{field} is not None:")
            indent = "    "

        lines.append(
            f"    {indent}offsets = [_{field}_add_to_builder(t, builder, strs, nodes) for t in __fb_self_{field}]"
        )
        lines.append(f"    {indent}builder.StartVector(4, len(offsets), 4)")
        lines.append(
            f"    {indent}for o in reversed(offsets): builder.PrependUOffsetTRelative(o)"
        )
        lines.append(f"    {indent}nodes[id(__fb_self_{field})] = builder.EndVector()")

    for field, type, _, is_optional in cl.tables:
        globs[f"_{field}_add_to_builder"] = hook_factory(type)
        prefix = ""
        if is_optional:
            prefix = f"if self.{field} is not None: "
        lines.append(
            f"    {prefix}nodes[id(self.{field})] = _{field}_add_to_builder(self.{field}, builder, strs, nodes)"
        )

    for field, union_members, _, _ in cl.unions:
        prefix = ""
        is_optional = NoneType in union_members
        if is_optional:
            prefix = f"if self.{field} is not None: "
        union_hooks = {}
        for type in union_members:
            if type is NoneType:
                continue
            # It's possible this is an annotation
            annot_and_base = get_annotation_and_base(type, UnionVal)
            if annot_and_base is not None:
                base = annot_and_base[1]
                union_hooks[base] = hook_factory(base)
            else:
                union_hooks[type] = hook_factory(type)
        globs[f"_{field}_hooks"] = union_hooks
        lines.append(
            f"    {prefix}nodes[id(self.{field})] = _{field}_hooks[self.{field}.__class__](self.{field}, builder, strs, nodes)"
        )

    # The actual object starts here.
    lines.append(f"    builder.StartObject({cl.num_slots})")

    for field, slot_idx, is_optional in cl.strings:
        indent = ""
        if is_optional:
            lines.append(f"    if __fb_self_{field} is not None:")
            indent = "    "
        lines.append(
            f"    {indent}builder.PrependUOffsetTRelativeSlot({slot_idx}, strs[__fb_self_{field}], 0)"
        )

    for field, slot_idx, is_optional in cl.byte_fields:
        prefix = ""
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        lines.append(
            f"    {prefix}builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(__fb_self_{field})], 0)"
        )

    for field, slot_idx, is_optional in cl.lists_of_strings:
        prefix = ""
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        lines.append(
            f"    {prefix}builder.PrependUOffsetTRelativeSlot({slot_idx}, __fb_self_{field}_offset, 0)"
        )

    for field, _, slot_idx, is_optional in cl.tables:
        indent = ""
        if is_optional:
            lines.append(f"    if self.{field} is not None:")
            indent = "    "
        lines.append(
            f"    {indent}builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(self.{field})], 0)"
        )

    for field, _, slot_idx, is_optional in cl.lists_of_tables:
        lines.append(f"    __fb_self_{field} = self.{field}")
        if is_optional:
            indent = f"if __fb_self_{field} is not None: "
        else:
            indent = ""
        lines.append(
            f"    {indent}builder.PrependUOffsetTRelativeSlot({slot_idx}, nodes[id(__fb_self_{field})], 0)"
        )

    for field, slot_idx, _, _, is_optional in cl.lists_of_scalars + cl.lists_of_enums:
        if is_optional:
            prefix = f"if __fb_self_{field} is not None: "
        else:
            prefix = ""
        lines.append(
            f"    {prefix}builder.PrependUOffsetTRelativeSlot({slot_idx}, __fb_self_{field}_offset, 0)"
        )

    for field, fb_type, slot_idx, default in cl.inlines + cl.enums:
        if default is NOTHING:
            default = SCALAR_TYPE_TO_DEFAULT[fb_type]
        lines.append(
            f"    builder.Prepend{fb_type}Slot({slot_idx}, self.{field}, {default})"
        )

    for field, union_types, union_mapping, slot_idx in cl.unions:
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


def make_from_fb_fn(
    cl: FlatbufferTable, hook_factory: Callable[[type[AttrsInstance]], Callable]
) -> Callable:
    """Compile a function to init an attrs model from a FB model, flattrs-style.

    The input is assumed to be an instance of `flatbuffers.Table`.
    """
    name = cl.cl.__name__
    globs = {"_Table": Table, "cls": cl.cl}
    lines = []
    inst_lines = []  # Instantiation lines
    byte_names = {f[0]: f for f in cl.byte_fields}
    string_names = {s[0]: s for s in cl.strings}
    list_table_fields = {t[0]: t for t in cl.lists_of_tables}
    union_field_names = {t[0]: t for t in cl.unions}
    lists_of_scalar_names = {t[0]: t for t in cl.lists_of_scalars + cl.lists_of_enums}
    lists_of_strings_names = {t[0]: t for t in cl.lists_of_strings}
    inline_names = {t[0]: t for t in cl.inlines}
    enum_names = {e[0]: e for e in cl.enums}
    table_names = {t[0]: t for t in cl.tables}

    lines.append("def __fb_from_fb__(tab):")

    inst_lines.append("    return cls(")
    for field in fields(cl.cl):
        fname = field.name
        if fname in string_names:
            string_def = string_names[fname]
            slot_idx = string_def[1]
            if string_def[2]:
                inst_lines.append(
                    f"        tab.String(tab.Pos + o).decode() if (o := tab.Offset({4 + slot_idx * 2})) != 0 else None,"
                )
            else:
                inst_lines.append(
                    f"        tab.String(tab.Pos + tab.Offset({4 + slot_idx * 2})).decode(),"
                )
        elif fname in byte_names:
            byte_def = byte_names[fname]
            slot_idx = byte_def[1]
            if byte_def[2]:
                inst_lines.append(
                    f"        tab.String(tab.Pos + o) if (o := tab.Offset({4 + slot_idx * 2})) != 0 else None,"
                )
            else:
                inst_lines.append(
                    f"        tab.String(tab.Pos + tab.Offset({4 + slot_idx * 2})),"
                )
        elif fname in enum_names:
            _, fb_type, slot_idx, default = enum_names[fname]
            globs[f"_{fname}_type"] = field.type
            globs[f"_{fname}_flags"] = SCALAR_TYPES_TO_FLAGS[fb_type]
            inst_lines.append(
                f"        _{fname}_type(tab.Get(_{fname}_flags, tab.Pos + o) if (o := tab.Offset({4 + slot_idx * 2})) != 0 else {default}),"
            )
        elif fname in table_names:
            table_def = table_names[fname]
            slot_idx = table_def[2]
            globs[f"_{fname}_from_fb"] = hook_factory(table_def[1])
            lines.append(f"    _{fname}_offset = tab.Offset({4 + slot_idx * 2})")
            suffix = ""
            if table_def[3]:
                suffix = f" if _{fname}_offset != 0 else None"
            inst_lines.append(
                f"        _{fname}_from_fb(tab.__class__(tab.Bytes, tab.Indirect(_{fname}_offset + tab.Pos))){suffix},"
            )
        elif fname in list_table_fields:
            _, type, slot_idx, is_optional = list_table_fields[fname]
            hook = hook_factory(type)
            globs[f"_{fname}_from_fb"] = hook
            lines.append(f"    _{fname}_offset = tab.Offset({4 + slot_idx * 2})")
            lines.append(
                f"    _{fname}_vector = tab.Vector(_{fname}_offset) if _{fname}_offset != 0 else None"
            )
            for_ = f"for i in range(tab.VectorLen(_{fname}_offset) if _{fname}_offset != 0 else 0)"
            line = f"        [_{fname}_from_fb(tab.__class__(tab.Bytes, tab.Indirect(_{fname}_vector + 4 * i))) {for_}]"

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
            slot_idx = inline[2]
            globs[f"_{fname}_type"] = SCALAR_TYPE_TO_PYTHON[inline[1]]
            globs[f"_{fname}_flags"] = SCALAR_TYPES_TO_FLAGS[inline[1]]
            if inline[3] is not NOTHING:
                globs[f"_{fname}_default"] = inline[3]
                default = f"_{fname}_default"
            else:
                default = SCALAR_TYPE_TO_DEFAULT[inline[1]]
            inst_lines.append(
                f"        _{fname}_type(tab.Get(_{fname}_flags, tab.Pos + o)) if (o := tab.Offset({4 + slot_idx * 2})) != 0 else {default},"
            )
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
                hook = hook_factory(attr_model)

                def _load_from_content(table: Table, o, hook=hook):
                    obj = Table(bytearray(), 0)
                    table.Union(obj, o)
                    return hook(obj)

                union_resolution_dict[ix] = _load_from_content

            globs[dn] = union_resolution_dict
            globs[f"_{fname}_flags"] = Uint8Flags
            lines.append(f"    _{fname}_offset = tab.Offset({4 + slot_idx * 2})")
            if NoneType in union_types:
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
            slot_idx = list_def[1]
            lines.append(f"    _{fname}_offset = tab.Offset({4 + slot_idx * 2})")
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
