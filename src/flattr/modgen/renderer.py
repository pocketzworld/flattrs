from pathlib import Path
from typing import Final, TypeAlias

from attrs import define
from lark import ParseTree, Token, Tree
from lark.visitors import Interpreter
from rich import print

from .parser import parser

Imports: TypeAlias = dict[str, set[str]]
Script: TypeAlias = list[str]
ImportableName: TypeAlias = str
MISSING: Final = "$MISSING"


@define
class ParsedModule:
    namespace: str
    filename: Path
    imports: Imports
    importables: list[tuple[ImportableName, Script]]

    def render(self) -> str:
        script = (
            "from __future__ import annotations\n"
            + "\n".join(
                f"from {source} import {', '.join(targets)}"
                for source, targets in self.imports.items()
            )
            + "\n"
            + "\n".join(line for item in self.importables for line in item[1])
        )
        return script


class FlatbufferRenderer(Interpreter):
    """Transform FlatBuffer code into Python code.

    The rendering needs to be done in two phases, since imports
    need to be resolved after the initial parsing pass.
    """

    def module(self, tree: ParseTree, filename: Path) -> ParsedModule:
        namespace = str(next(tree.find_data("namespace")).children[0])
        importables: list[tuple[ImportableName, list[str], Imports]] = [
            self.visit(t)
            for t in tree.find_pred(lambda t: t.data in ("table", "enum", "union"))
        ]
        imports = {}
        lines = []

        local_names = {i[0] for i in importables}

        for name, script, imps in importables:
            lines.append((name, script))
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

        return ParsedModule(namespace, filename, imports, lines)

    def namespace(self, _: ParseTree) -> tuple[list[str], Imports]:
        return [], {}

    def union(self, tree: ParseTree) -> tuple[ImportableName, list[str], Imports]:
        name = str(tree.children[0])
        members = [str(c.children[0]).split(".")[-1] for c in tree.children[1:]]
        member_string = " | ".join(members)
        return name, [f"{name} = {member_string}"], {MISSING: set(members)}

    def enum(self, tree: ParseTree) -> tuple[ImportableName, list[str], Imports]:
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
        return enum_name, [f"class {enum_name}({type}):", *fields], imports

    def enum_field(self, tree: ParseTree) -> tuple[str, int | None]:
        val = None
        for enum_val in tree.find_data("enum_field_default"):
            val = int(enum_val.children[0])
        return tree.children[0], val

    def table(self, tree: ParseTree) -> tuple[ImportableName, list[str], Imports]:
        name = str(tree.children[0])
        field_defs = [self.visit(c) for c in tree.children[1:]]
        lines = ["@flattrs", f"class {name}:", *[f"    {f[0]}" for f in field_defs]]
        imports = {"flattr": {"flattrs"}}
        for _, field_imports in field_defs:
            imports = merge_imports(imports, field_imports)

        return name, lines, imports

    def table_field(self, tree: ParseTree) -> tuple[str, Imports]:
        imports = {}
        name = tree.children[0]
        type = tree.children[1]
        is_required = False
        for attr_tree in tree.find_data("table_field_attributes"):
            if "required" in attr_tree.children:
                is_required = True
                break
        is_scalar = False
        if type == "string":
            if is_required:
                type = "str"
            else:
                type = "str | None"
            default = ""
        elif isinstance(type, Token):
            # This is a name, so probably a table field.
            default = ""
            imports.setdefault(MISSING, []).append(str(type))
            if not is_required:
                type = f"{type} | None"
        else:
            if type.data == "vector_type":
                inner_type = type.children[0]
                if inner_type.lower() in ("uint8", "ubyte"):
                    type = "bytes"
                else:
                    if inner_type.lower() in TYPE_MAP:
                        inner_type = TYPE_MAP[inner_type]
                        if inner_type not in ("int", "float", "bool", "str", "float"):
                            imports["flattr"] = {inner_type}
                    else:
                        imports.setdefault(MISSING, []).append(str(inner_type))
                    type = f"list[{inner_type}]"
                if not is_required:
                    type = f"{type} | None"
                default = ""
            elif type.data == "string":
                pass
            else:
                # A scalar.
                type = type.children[0]
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
                    default = f" = {def_val}"

        return f"{name}: {type}{default}", imports

    def table_field_default(self):
        pass


def parse_module(module_tree: Tree, file: Path) -> ParsedModule:
    r = FlatbufferRenderer()
    parsed_module = r.module(module_tree, file)
    return parsed_module


def render_directory(input: Path, output: Path) -> None:
    # First we parse, then we resolve imports, then we write.
    per_namespace: dict[str, list[ParsedModule]] = {}
    importables_to_module: dict[str, ParsedModule] = {}
    for file in input.rglob("*.fbs"):
        rel_path = file.relative_to(input).with_suffix(".py")
        pm = parse_module(parser.parse(file.read_text()), rel_path)
        for importable, _ in pm.importables:
            importables_to_module[importable] = pm
        per_namespace.setdefault(pm.namespace, []).append(pm)

    # Now we need to fill in the missing imports.

    # Now we write the modules to disk.
    output.mkdir(exist_ok=True, parents=True)
    (output / "__init__.py").write_text("")
    for pm_list in per_namespace.values():
        for pm in pm_list:
            print(pm)
            missing_imports = pm.imports.pop(MISSING, set())
            for m in missing_imports:
                module = importables_to_module[m]
                if module.filename.parent == pm.filename.parent:
                    rel_path = f".{module.filename.stem}"
                else:
                    full_rel_path = module.filename.relative_to(pm.filename.parent)
                    fname = full_rel_path.stem
                    rel_path = f".{str(full_rel_path.parent).replace('/', '.')}.{fname}"
                pm.imports.setdefault(str(rel_path), set()).add(m)
            # try:
            target_file = output / pm.filename
            target_file.parent.mkdir(exist_ok=True, parents=True)
            (target_file.parent / "__init__.py").write_text("")
            target_file.write_text(pm.render())
            # except Exception as exc:
            #    print(f"While parsing or rendering {file}: {exc}")


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
