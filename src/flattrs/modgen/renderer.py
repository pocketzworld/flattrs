from enum import Enum as PythonEnum
from keyword import iskeyword
from pathlib import Path
from traceback import print_exception
from typing import Final, Mapping, Sequence, Set, TypeAlias

from attrs import define, evolve, field, frozen
from immutables import Map
from lark import ParseTree, Token, Tree
from lark.visitors import Interpreter

from .._types import FieldName, Optionality
from .parser import parser

ImportableName: TypeAlias = str
NamespacePrefix: TypeAlias = str
Imports: TypeAlias = Mapping[str, Set[str]]
UnresolvedImports: TypeAlias = Set[tuple[NamespacePrefix, ImportableName]]
Script: TypeAlias = list[str]
MISSING: Final = "$MISSING"


@frozen
class Attribute:
    name: str
    value: str | None = None
    namespace: str | None = MISSING


BUILTIN_ATTRS = {"required", "deprecated", "key"}
NO_REPR = Attribute("norepr", namespace="flattrs")
FROZEN = Attribute("immutable", namespace="flattrs")


@frozen
class Table:
    @frozen
    class Field:
        name: FieldName
        type: str
        default: str
        is_optional: Optionality
        namespace_prefix: str | None = None
        attrs: Sequence[Attribute] = field(factory=tuple, converter=tuple)

    name: ImportableName
    field_defs: Sequence[Field] = field(converter=tuple)
    imports: Imports = field(converter=Map)
    attrs: Sequence[Attribute] = field(converter=tuple)
    unresolved_imports: UnresolvedImports = field(converter=frozenset)

    def adjust_enums(self, enums: set[str]) -> "Table":
        """
        Table fields that are enums must not be optional.

        Also, we adjust the default values for enums, if present.

        In addition, we apply the keyword remap to the default, if needed.
        """
        field_defs = [
            f
            if f.type not in enums
            else evolve(
                f,
                is_optional=False,
                default=f"{f.type}.{map_python_keywords(f.default)}"
                if f.default
                else f.default,
            )
            for f in self.field_defs
        ]
        return evolve(self, field_defs=field_defs)

    def adjust_defaults(self) -> "Table":
        """Insert default values as possible, starting from the back.

        This is to preserve backwards comp when optional fields are added.

        This needs to run after `adjust_enums`, since it depends on the
        optionality of fields.
        """
        new_field_defs = []
        can_add_defaults = True
        for field_def in reversed(self.field_defs):
            if can_add_defaults:
                if field_def.is_optional:
                    if not field_def.default:
                        field_def = evolve(field_def, default="None")
                elif not field_def.default:
                    # We need to stop adding defaults.
                    can_add_defaults = False
            new_field_defs.append(field_def)
        return evolve(self, field_defs=list(reversed(new_field_defs)))

    def adjust_attribute_namespaces(
        self, namespace_map: dict[str, set[str]]
    ) -> "Table":
        new_table_attrs = []
        for attr in self.attrs:
            if attr.namespace == MISSING:
                for n, ats in namespace_map.items():
                    if attr.name in ats:
                        attr = evolve(attr, namespace=n)
                        break
                else:
                    raise Exception(f"Couldn't resolve attribute {attr}")
                new_table_attrs.append(attr)
        new_field_defs = []
        for field_def in self.field_defs:
            new_attrs = []
            for attr in field_def.attrs:
                if attr.namespace == MISSING:
                    for n, ats in namespace_map.items():
                        if attr.name in ats:
                            attr = evolve(attr, namespace=n)
                            break
                    else:
                        raise Exception(
                            f"{self.name}: Couldn't resolve attribute {attr}"
                        )
                new_attrs.append(attr)
            new_field_defs.append(evolve(field_def, attrs=new_attrs))
        return evolve(self, attrs=new_table_attrs, field_defs=new_field_defs)

    def adjust_imports(self) -> "Table":
        """This needs to be called after `adjust_attribute_namespace` for correctness."""
        is_frozen = FROZEN in self.attrs
        imports = merge_imports(
            self.imports, {"attrs": {"define"} if not is_frozen else {"frozen"}}
        )
        for f in self.field_defs:
            has_repr = True
            if f.type == "bytes" or NO_REPR in f.attrs:
                has_repr = False
            needs_field = not has_repr
            if needs_field:
                imports = merge_imports(imports, {"attrs": {"field"}})
        return evolve(self, imports=imports)

    def render(self) -> Script:
        # This can be a little tricky, since we need to use `attrs.field`
        # in case we need to supress the repr.
        is_frozen = FROZEN in self.attrs
        lines = [
            "@define" if not is_frozen else "@frozen",
            f"class {self.name}:",
        ]
        field_lines = []
        for f in self.field_defs:
            def_str = ""
            has_repr = True
            if f.type == "bytes" or NO_REPR in f.attrs:
                has_repr = False

            needs_field = not has_repr

            if needs_field:
                field_args = []
                if f.default:
                    field_args.append(("default", f.default))
                if not has_repr:
                    field_args.append(("repr", "False"))
                field_str = ", ".join(f"{k}={v}" for k, v in field_args)
                def_str = f" = field({field_str})"
            elif f.default:
                def_str = f" = {f.default}"

            line = (
                f"    {f.name}: {f.type}{' | None' if f.is_optional else ''}{def_str}"
            )
            field_lines.append(line)

        if not self.field_defs:
            field_lines.append("    pass")
        script = lines + field_lines
        return script


@define
class Enum:
    name: str
    type: type[PythonEnum]
    fields: list[str]

    def render(self) -> Script:
        lines = [f"class {self.name}({self.type}):", *self.fields]
        return lines


@frozen
class Union:
    name: str
    members: Sequence[tuple[str, int | None]] = field(converter=tuple)

    def render(self) -> Script:
        member_names = []
        if len(self.members) == 1:
            # Special case when there is only one union member.
            member_name, union_val = self.members[0]
            if union_val is not None:
                # This has a union tag attached.
                member_name = f"Annotated[{member_name}, UnionVal({union_val})]"
            else:
                member_name = f"Annotated[{member_name}, UnionVal(1)]"
            member_names.append(member_name)
        else:
            for member_name, union_val in self.members:
                if union_val is not None:
                    # This has a union tag attached.
                    member_name = f"Annotated[{member_name}, UnionVal({union_val})]"
                member_names.append(member_name)
        member_string = " | ".join(member_names)
        return [f"{self.name} = {member_string}"]


@define
class Module:
    namespace: str | None
    path: Path
    imports: Imports
    importables: list[tuple[ImportableName, Union | Table | Enum | Attribute]]
    unresolved_imports: UnresolvedImports

    def render(self) -> str:
        body = ""
        # We potentially need to reorder since unions must refer to existing
        # names.
        tables_to_indices = {}
        for ix, item in enumerate(self.importables):
            if isinstance(item[1], Table):
                tables_to_indices[item[0]] = ix

        render_after: dict[Table, list[tuple[ImportableName, Union]]] = {}

        for ix, item in enumerate(list(self.importables)):
            if isinstance(item[1], Union):
                member_indices = [
                    tables_to_indices.get(n[0], -1) for n in item[1].members
                ]
                if member_indices:
                    largest_child_idx = max(member_indices)
                    if largest_child_idx > ix:
                        render_after.setdefault(
                            self.importables[largest_child_idx][1], []
                        ).append(item)
                        self.importables.remove(item)

        for item in self.importables:
            if isinstance(item[1], Table):
                body += "\n".join(item[1].render())
                post_unions = render_after.get(item[1], [])
                if post_unions:
                    body += "\n\n\n"
                for union in post_unions:
                    rendered = "\n".join(union[1].render())
                    body += rendered
                    body += "\n\n\n"
            elif isinstance(item[1], Enum):
                body += "\n".join(item[1].render())
                body += "\n"
            elif isinstance(item[1], Attribute):
                # Attributes don't get rendered.
                pass
            else:
                body += "\n".join(item[1].render())
            body += "\n\n\n"
        if not body.strip():
            # We don't render empty files.
            return ""

        imports = self.imports
        for _, item in self.importables:
            if isinstance(item, Table):
                imports = merge_imports(imports, item.imports)
        imports = {k: v for k, v in imports.items() if k != MISSING}

        script = (
            "from __future__ import annotations\n\n"
            + "\n".join(
                f"from {source} import {', '.join(sorted(targets))}"
                for source, targets in imports.items()
            )
            + "\n"
            + body
        )
        return script


class FlatbufferInterpreter(Interpreter):
    """Transform FlatBuffer code into Python code.

    The rendering needs to be done in several phases, since imports
    need to be resolved after the initial parsing pass and types
    may need to be adjusted based on the actual types.
    """

    def module(self, tree: ParseTree, filename: Path) -> Module:
        namespace = None
        for t in tree.find_data("namespace"):
            namespace = str(t.children[0])
        importables: list[
            tuple[ImportableName, Union | Table | Enum | Attribute, Imports]
        ] = [
            self.visit(t)
            for t in tree.find_pred(
                lambda t: t.data in ("table", "enum", "union", "attribute")
            )
        ]
        imports = {}
        unresolved_imports = frozenset()
        res = []

        local_names = {i[0] for i in importables}

        for name, importable, imps in importables:
            if isinstance(importable, Attribute):
                importable = evolve(importable, namespace=namespace)
            res.append((name, importable))
            for k, v in imps.items():
                if k != MISSING:
                    if k not in imports:
                        imports[k] = set()
                    imports[k] |= v - local_names
            if isinstance(importable, Union):
                for k, v in imps.items():
                    if k == MISSING:
                        for val in v:
                            if val in local_names:
                                continue
                            parts = val.rsplit(".", 1)
                            if len(parts) == 1:
                                unresolved_imports |= {("", val)}
                            else:
                                unresolved_imports |= {tuple(parts)}
            if isinstance(importable, Table):
                unresolved_imports |= {
                    i for i in importable.unresolved_imports if i[1] not in local_names
                }
        return Module(namespace, filename, imports, res, unresolved_imports)

    def namespace(self, _: ParseTree) -> tuple[list[str], Imports]:
        return [], {}

    def attribute(self, tree: ParseTree) -> tuple[ImportableName, Attribute, Imports]:
        name = str(tree.children[0])
        return (name, Attribute(name), {})

    def union(self, tree: ParseTree) -> tuple[ImportableName, Union, Imports]:
        name = str(tree.children[0])
        member_names = []
        to_resolve = set()
        imports = {}
        members = tree.children[1:]
        if len(members) == 1:
            # Special case when there is only one union member.
            member = members[0]
            member_name = str(member.children[0])
            to_resolve.add(member_name)
            member_name = member_name.split(".")[-1]

            imports["typing"] = {"Annotated"}
            imports["flattrs"] = {"UnionVal"}
            if len(member.children) > 1:
                # This has a union tag attached.
                member_names.append((member_name, int(member.children[1])))
            else:
                member_names.append((member_name, None))
        else:
            for member in tree.children[1:]:
                member_name = str(member.children[0])
                to_resolve.add(member_name)
                member_name = member_name.split(".")[-1]
                if len(member.children) > 1:
                    # This has a union tag attached.
                    imports["typing"] = {"Annotated"}
                    imports["flattrs"] = {"UnionVal"}
                    member_names.append((member_name, int(member.children[1])))
                else:
                    member_names.append((member_name, None))
        return (
            name,
            Union(name, member_names),
            {MISSING: to_resolve} | imports,
        )

    def enum(self, tree: ParseTree) -> tuple[ImportableName, Enum, Imports]:
        enum_name = str(tree.children[0])
        type = ENUM_TYPE_MAP[tree.children[1]]
        if type == "IntEnum":
            imports = {"enum": {"IntEnum"}}
        else:
            imports = {"flattrs": {type}}
        fields = []
        next_val = 0
        for child in tree.children[2:]:
            name, val = self.visit(child)
            if val is None:
                val = next_val
                next_val += 1
            else:
                next_val = val + 1
            fields.append(f"    {map_python_keywords(name)} = {val}")
        return enum_name, Enum(enum_name, type, fields), imports

    def enum_field(self, tree: ParseTree) -> tuple[str, int | None]:
        val = None
        for enum_val in tree.find_data("enum_field_default"):
            val = int(enum_val.children[0])
        return tree.children[0], val

    def table(self, tree: ParseTree) -> tuple[ImportableName, Table, Imports]:
        name = str(tree.children[0])
        table_attributes = []
        for child in tree.children:
            if isinstance(child, Tree) and child.data == "attributes":
                table_attributes.extend(
                    Attribute(c, namespace=None if c in BUILTIN_ATTRS else MISSING)
                    for c in child.children
                )
        field_defs = [self.table_field(c) for c in tree.find_data("table_field")]
        imports = Map()
        urs = set()
        for _, _, _, _, field_imports, unresolved_imports, _ in field_defs:
            imports = merge_imports(imports, field_imports)
            urs |= unresolved_imports
        fields = []
        for f in field_defs:
            is_optional = Attribute("required", namespace=None) not in f[3]
            fields.append(
                Table.Field(
                    f[0],
                    f[1],
                    f[2],
                    is_optional,
                    f[6] or None,
                    f[3],
                )
            )

        table = Table(name, fields, imports, table_attributes, urs)
        return (
            name,
            table,
            imports,
        )

    def table_field(
        self, tree: ParseTree
    ) -> tuple[FieldName, str, str, list[Attribute], Imports, UnresolvedImports, str]:
        imports = {}
        unresolved_imports = set()
        name = str(tree.children[0])
        full_type = tree.children[1]
        attributes = []
        for attr_tree in tree.find_data("attributes"):
            for c in attr_tree.children:
                attr_name = str(c)
                if attr_name in BUILTIN_ATTRS:
                    attr_namespace = None
                else:
                    attr_namespace = MISSING
                attributes.append(Attribute(attr_name, namespace=attr_namespace))
        is_scalar = False
        namespace_prefix = ""
        if full_type == "string":
            type = "str"
            default = ""
        elif isinstance(full_type, Token):
            # This is a name, so probably a table field.
            default = ""
            namespace_prefix, type = (
                full_type.rsplit(".", 1) if "." in full_type else ("", full_type)
            )
            unresolved_imports.add((namespace_prefix, type))
            for def_child in tree.find_data("table_field_default"):
                default = str(def_child.children[0])
        else:
            if full_type.data == "vector_type":
                inner_type = full_type.children[0]
                if inner_type.lower() in ("uint8", "ubyte"):
                    type = "bytes"
                else:
                    if inner_type.lower() in TYPE_MAP:
                        inner_type = TYPE_MAP[inner_type]
                        if inner_type not in ("int", "float", "bool", "str", "float"):
                            imports["flattrs"] = {inner_type}
                    else:
                        namespace_prefix, inner_type = (
                            inner_type.rsplit(".", 1)
                            if "." in inner_type
                            else ("", inner_type)
                        )
                        unresolved_imports.add((namespace_prefix, str(inner_type)))
                    type = f"list[{inner_type}]"
                default = ""
            elif full_type.data == "string":
                pass
            else:
                # A scalar.
                attributes.append(Attribute("required", namespace=None))
                type = full_type.children[0]
                if type.lower() in TYPE_MAP:
                    is_scalar = True
                    type = TYPE_MAP[type]
                    if type not in ("int", "float", "bool", "str", "float"):
                        imports["flattrs"] = frozenset([type])

                default = ""
                for def_tree in tree.find_data("table_field_default"):
                    def_val = def_tree.children[0]
                    if type == "bool":
                        def_val = def_val.capitalize()
                    elif not is_scalar:
                        # This has to be an enum
                        def_val = f"{type}.{def_val}"
                    default = def_val

        return (
            name,
            type,
            default,
            attributes,
            imports,
            unresolved_imports,
            namespace_prefix,
        )

    def table_field_default(self):
        pass


def parse_module(module_tree: Tree, file: Path) -> Module:
    r = FlatbufferInterpreter()
    parsed_module = r.module(module_tree, file)
    return parsed_module


def render_directory(
    input: Path, output: Path, gen_namespace_imports: bool = False
) -> None:
    """
    Render a directory of Flatbuffers into a directory of Python.

    """
    # First we parse, then we resolve imports, then we write.
    per_namespace: dict[str | None, list[Module]] = {}
    importables_to_module: dict[str, list[Module]] = {}
    namespace_to_attributes: dict[str, set[str]] = {}
    enums = set()
    modules: list[Module] = []
    for file in input.rglob("*.fbs"):
        rel_path = file.relative_to(input).with_suffix(".py")
        try:
            pm = parse_module(parser.parse(file.read_text()), rel_path)
        except Exception as exc:
            print(f"While parsing {file}: {exc}")
            print_exception(exc)
        modules.append(pm)
        # Gather importables so we can resolve them later.
        for name, importable in pm.importables:
            importables_to_module.setdefault(name, []).append(pm)
            if isinstance(importable, Enum):
                enums.add(importable.name)
            elif isinstance(importable, Attribute):
                namespace_to_attributes.setdefault(pm.namespace or "", set()).add(
                    importable.name
                )
        per_namespace.setdefault(pm.namespace, []).append(pm)

    # We can resolve attribute namespaces now.
    # At this point, we know which importables are enums.
    # Tables referencing those need to have their types adjusted.
    # For each table, add defaults as much as possible,
    # starting from backwards. This is so fields added at the end
    # keep backwards comp.
    for module in modules:
        module.importables = [
            (
                name,
                i.adjust_attribute_namespaces(namespace_to_attributes)
                .adjust_enums(enums)
                .adjust_defaults()
                .adjust_imports()
                if isinstance(i, Table)
                else i,
            )
            for name, i in module.importables
        ]

    # Now we write the modules to disk.
    output.mkdir(exist_ok=True, parents=True)
    (output / "__init__.py").write_text("")
    for pm_list in per_namespace.values():
        for pm in pm_list:
            pm_path = pm.path
            for ns, importable in pm.unresolved_imports:
                for module in importables_to_module[importable]:
                    if pm.namespace == module.namespace:
                        # Referencing a symbol in the same namespace.
                        break
                    if not ns:
                        if not module.namespace:
                            break
                    else:
                        # A namespace is referenced.
                        if module.namespace is not None:
                            if module.namespace.endswith(ns):
                                break
                else:
                    raise Exception(f"Cannot resolve {ns}.{importable} in {pm_path}")

                if module.path.parent == pm_path.parent:
                    rel_path = f".{module.path.stem}"
                else:
                    pm_parents = set(pm_path.parents)
                    target_parents = set(module.path.parents)
                    common_parent = sorted(
                        pm_parents & target_parents, key=lambda p: -len(str(p))
                    )[0]
                    num_dots = len(pm_path.relative_to(common_parent).parent.parts) + 1

                    target_rel_path = module.path.relative_to(common_parent)
                    fname = target_rel_path.stem
                    if target_rel_path.parent == Path("."):
                        rel_path = f"{'.' * num_dots}{fname}"
                    else:
                        rel_path = f"{'.' * num_dots}{str(target_rel_path.parent).replace('/', '.')}.{fname}"
                pm.imports.setdefault(str(rel_path), set()).add(importable)
            try:
                target_file = output / pm.path
                rendered = pm.render()
                if not rendered:
                    continue
                target_file.parent.mkdir(exist_ok=True, parents=True)
                (target_file.parent / "__init__.py").write_text("")
                target_file.write_text(rendered)
            except Exception as exc:
                print(f"While parsing or rendering {file}: {exc}")
                print_exception(exc)
    if gen_namespace_imports:
        for namespace, pm_list in per_namespace.items():
            importables: list[tuple[str, Path]] = []
            for module in pm_list:
                importables.extend(
                    [
                        (i[0], module.path)
                        for i in module.importables
                        if not isinstance(i[1], Attribute)
                    ]
                )
            if not importables:
                continue
            namespace_dir = Path(
                namespace.replace(".", "/") if namespace is not None else "."
            )
            namespace_fn = namespace_dir / "__init__.py"
            (output / namespace_dir).mkdir(parents=True, exist_ok=True)
            (output / namespace_fn).write_text(
                render_exports(namespace_fn, importables)
            )


def make_import_path(importing_from: Path, import_target: Path) -> str:
    if importing_from.parent == import_target.parent:
        rel_path = f".{import_target.stem}"
    else:
        active_parents = set(importing_from.parents)
        target_parents = set(import_target.parents)
        common_parent = sorted(
            active_parents & target_parents, key=lambda p: -len(str(p))
        )[0]
        num_dots = len(importing_from.relative_to(common_parent).parent.parts) + 1

        target_rel_path = import_target.relative_to(common_parent)
        fname = target_rel_path.stem
        if target_rel_path.parent == Path("."):
            rel_path = f"{'.' * num_dots}{fname}"
        else:
            rel_path = f"{'.' * num_dots}{str(target_rel_path.parent).replace('/', '.')}.{fname}"
    return rel_path


def render_exports(importing_from: Path, importables: list[tuple[str, Path]]) -> str:
    return (
        "\n".join(
            f"from {make_import_path(importing_from, p)} import {i}"
            for i, p in importables
        )
        + "\n\n__all__ = ["
        + "\n".join(f'"{i[0]}",' for i in sorted(importables))
        + "]\n"
    )


def render(input: Path, output: Path, gen_namespace_exports: bool = False) -> None:
    if input.is_file():
        output.parent.mkdir(exist_ok=True, parents=True)
        output.write_text(parse_module(parser.parse(input.read_text()), output))
    else:
        render_directory(input, output, gen_namespace_exports)


def merge_imports(a: Imports, b: Imports) -> Imports:
    res: Imports = {}
    for k, v in a.items():
        res[k] = frozenset(res.get(k, frozenset()) | v)
    for k, v in b.items():
        res[k] = frozenset(res.get(k, frozenset()) | v)
    return Map(res)


def map_python_keywords(name: str) -> str:
    """If an identifier is a Python keyword, we adjust it by adding an underscore.

    Like flatc.
    """
    return f"{name}_" if iskeyword(name) else name


TYPE_MAP: Final = {
    "string": "str",
    "bool": "bool",
    "uint8": "Uint8",
    "ubyte": "Uint8",
    "uint16": "Uint16",
    "ushort": "Uint16",
    "uint32": "Uint32",
    "uint": "Uint32",
    "uint64": "Uint64",
    "ulong": "Uint64",
    "int8": "Int8",
    "byte": "Int8",
    "int16": "Int16",
    "short": "Int16",
    "int32": "Int32",
    "int": "Int32",
    "int64": "int",
    "long": "int",
    "float": "Float32",
    "float32": "Float32",
    "double": "float",
    "float64": "float",
}
ENUM_TYPE_MAP: Final = {
    "uint8": "Uint8Enum",
    "ubyte": "Uint8Enum",
    "uint16": "Uint16Enum",
    "ushort": "Uint16Enum",
    "uint32": "Uint32Enum",
    "uint": "Uint32Enum",
    "uint64": "Uint64Enum",
    "ulong": "Uint64Enum",
    "int8": "Int8Enum",
    "byte": "Int8Enum",
    "int16": "Int16Enum",
    "short": "Int16Enum",
    "int32": "Int32Enum",
    "int": "Int32Enum",
    "int64": "IntEnum",
    "long": "IntEnum",
}
