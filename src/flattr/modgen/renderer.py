from enum import Enum as PythonEnum
from pathlib import Path
from traceback import print_exception
from typing import Final, TypeAlias

from attrs import define, evolve
from lark import ParseTree, Token, Tree
from lark.visitors import Interpreter

from .._types import Optionality
from .parser import parser

Imports: TypeAlias = dict[str, set[str]]
Script: TypeAlias = list[str]
ImportableName: TypeAlias = str
MISSING: Final = "$MISSING"


@define
class Table:
    @define
    class Field:
        name: str
        type: str
        default: str
        is_optional: Optionality
        namespace_prefix: str | None = None

    name: ImportableName
    field_defs: list[Field]
    imports: Imports

    def adjust_enums(self, enums: set[str]) -> None:
        """
        Table fields that are enums must not be optional.

        Also, we adjust the default values for enums, if present.
        """
        self.field_defs = [
            f
            if f.type not in enums
            else evolve(
                f,
                is_optional=False,
                default=f"{f.type}.{f.default}" if f.default else f.default,
            )
            for f in self.field_defs
        ]

    def adjust_defaults(self) -> None:
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
        self.field_defs = list(reversed(new_field_defs))

    def render(self) -> Script:
        # This can be a little tricky, since we need to use `attrs.field`
        # in case we need to supress the repr.
        lines = [
            "@define",
            f"class {self.name}:",
        ]
        self.imports = merge_imports(self.imports, {"attrs": {"define"}})
        field_lines = []
        for f in self.field_defs:
            def_str = ""
            has_repr = True
            if f.type == "bytes":
                has_repr = False

            needs_field = not has_repr

            if needs_field:
                self.imports = merge_imports(self.imports, {"attrs": {"field"}})
                field_args = []
                if f.default:
                    field_args.append(("default", f.default))
                if not has_repr:
                    field_args.append(("repr", "False"))
                field_str = f", ".join(f"{k}={v}" for k, v in field_args)
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


@define
class Module:
    namespace: str | None
    filename: Path
    imports: Imports
    importables: list[tuple[ImportableName, Script | Table | Enum]]

    def render(self) -> str:
        body = ""
        imports = self.imports
        for item in self.importables:
            if isinstance(item[1], Table):
                body += "\n".join(item[1].render())
                imports = merge_imports(imports, item[1].imports)
            elif isinstance(item[1], Enum):
                body += "\n".join(item[1].render())
            else:
                body += "\n".join(item[1])
            body += "\n\n\n"

        imports = self.imports
        for _, item in self.importables:
            if isinstance(item, Table):
                imports = merge_imports(imports, item.imports)
        self.imports = imports
        self.imports.pop(MISSING, None)

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


class FlatbufferRenderer(Interpreter):
    """Transform FlatBuffer code into Python code.

    The rendering needs to be done in several phases, since imports
    need to be resolved after the initial parsing pass and types
    may need to be adjusted based on the actual types.
    """

    def module(self, tree: ParseTree, filename: Path) -> Module:
        namespace = None
        for t in tree.find_data("namespace"):
            namespace = str(t.children[0])
        importables: list[tuple[ImportableName, Script | Table | Enum, Imports]] = [
            self.visit(t)
            for t in tree.find_pred(lambda t: t.data in ("table", "enum", "union"))
        ]
        imports = {}
        lines = []

        local_names = {i[0] for i in importables}

        for name, script_or_table, imps in importables:
            lines.append((name, script_or_table))
            for k, v in imps.items():
                if k == MISSING:
                    for val in v:
                        if val in local_names:
                            continue
                        imports.setdefault(k, set()).add(val)
                else:
                    if k not in imports:
                        imports[k] = set()
                    imports[k] |= v

        return Module(namespace, filename, imports, lines)

    def namespace(self, _: ParseTree) -> tuple[list[str], Imports]:
        return [], {}

    def union(self, tree: ParseTree) -> tuple[ImportableName, Script, Imports]:
        name = str(tree.children[0])
        member_names = []
        to_resolve = set()
        imports = {}
        for member in tree.children[1:]:
            member_name = str(member.children[0]).split(".")[-1]
            to_resolve.add(member_name)
            if len(member.children) > 1:
                # This has a union tag attached.
                imports["typing"] = {"Annotated"}
                imports["flattr"] = {"UnionVal"}
                member_name = (
                    f"Annotated[{member_name}, UnionVal({str(member.children[1])})]"
                )
            member_names.append(member_name)
        member_string = " | ".join(member_names)
        return (
            name,
            [f"{name} = {member_string}"],
            {MISSING: to_resolve} | imports,
        )

    def enum(self, tree: ParseTree) -> tuple[ImportableName, Enum, Imports]:
        enum_name = str(tree.children[0])
        type = ENUM_TYPE_MAP[tree.children[1]]
        if type == "IntEnum":
            imports = {"enum": {"IntEnum"}}
        else:
            imports = {"flattr": {type}}
        fields = []
        next_val = 0
        for child in tree.children[2:]:
            name, val = self.visit(child)
            if val is None:
                val = next_val
                next_val += 1
            else:
                next_val = val + 1
            fields.append(f"    {name} = {val}")
        return enum_name, Enum(enum_name, type, fields), imports

    def enum_field(self, tree: ParseTree) -> tuple[str, int | None]:
        val = None
        for enum_val in tree.find_data("enum_field_default"):
            val = int(enum_val.children[0])
        return tree.children[0], val

    def table(self, tree: ParseTree) -> tuple[ImportableName, Table, Imports]:
        name = str(tree.children[0])
        field_defs = [self.table_field(c) for c in tree.children[1:]]
        imports = {}
        for _, _, _, _, field_imports, _ in field_defs:
            imports = merge_imports(imports, field_imports)

        return (
            name,
            Table(
                name,
                [Table.Field(f[0], f[1], f[2], f[3], f[5] or None) for f in field_defs],
                imports,
            ),
            imports,
        )

    def table_field(
        self, tree: ParseTree
    ) -> tuple[str, str, str, Optionality, Imports, str]:
        imports = {}
        name = str(tree.children[0])
        full_type = tree.children[1]
        is_required = False
        for attr_tree in tree.find_data("table_field_attributes"):
            if "required" in attr_tree.children:
                is_required = True
                break

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
            imports.setdefault(MISSING, []).append(str(type))
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
                            imports["flattr"] = {inner_type}
                    else:
                        namespace_prefix, inner_type = (
                            inner_type.rsplit(".", 1)
                            if "." in inner_type
                            else ("", inner_type)
                        )
                        imports.setdefault(MISSING, []).append(str(inner_type))
                    type = f"list[{inner_type}]"
                default = ""
            elif full_type.data == "string":
                pass
            else:
                # A scalar.
                is_required = True
                type = full_type.children[0]
                if type.lower() in TYPE_MAP:
                    is_scalar = True
                    type = TYPE_MAP[type]
                    if type not in ("int", "float", "bool", "str", "float"):
                        imports["flattr"] = {type}

                default = ""
                for def_tree in tree.find_data("table_field_default"):
                    def_val = def_tree.children[0]
                    if type == "bool":
                        def_val = def_val.capitalize()
                    elif not is_scalar:
                        # This has to be an enum
                        def_val = f"{type}.{def_val}"
                    default = def_val

        return name, type, default, not is_required, imports, namespace_prefix

    def table_field_default(self):
        pass


def parse_module(module_tree: Tree, file: Path) -> Module:
    r = FlatbufferRenderer()
    parsed_module = r.module(module_tree, file)
    return parsed_module


def render_directory(input: Path, output: Path) -> None:
    # First we parse, then we resolve imports, then we write.
    per_namespace: dict[str, list[Module]] = {}
    importables_to_module: dict[str, Module] = {}
    enums = set()
    tables: list[Table] = []
    for file in input.rglob("*.fbs"):
        rel_path = file.relative_to(input).with_suffix(".py")
        try:
            pm = parse_module(parser.parse(file.read_text()), rel_path)
        except Exception as exc:
            print(f"While parsing {file}: {exc}")
            print_exception(exc)
        for name, importable in pm.importables:
            importables_to_module[name] = pm
            if isinstance(importable, Enum):
                enums.add(importable.name)
            elif isinstance(importable, Table):
                tables.append(importable)
        per_namespace.setdefault(pm.namespace, []).append(pm)

    # At this point, we know which importables are enums.
    # Tables referencing those need to have their types adjusted.
    for table in tables:
        table.adjust_enums(enums)

    # For each table, add defaults as much as possible,
    # starting from backwards. This is so fields added at the end
    # keep backwards comp.
    for table in tables:
        table.adjust_defaults()

    # Now we write the modules to disk.
    output.mkdir(exist_ok=True, parents=True)
    (output / "__init__.py").write_text("")
    for pm_list in per_namespace.values():
        for pm in pm_list:
            pm_path = pm.filename
            missing_imports = pm.imports.pop(MISSING, set())
            for importable in missing_imports:
                module = importables_to_module[importable]

                if module.filename.parent == pm_path.parent:
                    rel_path = f".{module.filename.stem}"
                else:
                    pm_parents = set(pm_path.parents)
                    target_parents = set(module.filename.parents)
                    common_parent = sorted(
                        pm_parents & target_parents, key=lambda p: -len(str(p))
                    )[0]
                    num_dots = len(pm_path.relative_to(common_parent).parent.parts) + 1

                    target_rel_path = module.filename.relative_to(common_parent)
                    fname = target_rel_path.stem
                    if target_rel_path.parent == Path("."):
                        rel_path = f"{'.' * num_dots}{fname}"
                    else:
                        rel_path = f"{'.' * num_dots}{str(target_rel_path.parent).replace('/', '.')}.{fname}"
                pm.imports.setdefault(str(rel_path), set()).add(importable)
            try:
                target_file = output / pm.filename
                target_file.parent.mkdir(exist_ok=True, parents=True)
                (target_file.parent / "__init__.py").write_text("")
                target_file.write_text(pm.render())
            except Exception as exc:
                print(f"While parsing or rendering {file}: {exc}")
                print_exception(exc)


def render(input: Path, output: Path) -> None:
    if input.is_file():
        output.parent.mkdir(exist_ok=True, parents=True)
        output.write_text(parse_module(parser.parse(input.read_text()), output))
    else:
        render_directory(input, output)


def merge_imports(a: Imports, b: Imports) -> Imports:
    res: Imports = {}
    for k, v in a.items():
        res.setdefault(k, set()).update(v)
    for k, v in b.items():
        res.setdefault(k, set()).update(v)
    return res


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
