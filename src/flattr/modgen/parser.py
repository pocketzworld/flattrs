from lark import Lark

parser = Lark(
    r"""
namespace : "namespace" NAMESPACE_NAME ";"

LCASE_LETTER: "a".."z"
UCASE_LETTER: "A".."Z"
DIGIT: "0".."9"
DECIMAL_POSITIVE_INTEGER: "1".."9" DIGIT*

LETTER: UCASE_LETTER | LCASE_LETTER
WORD: LETTER+

NAMESPACE_NAME: LETTER (LETTER | "_" | ".")*
FILEPATH: LETTER (LETTER | "_" | "." | "/")* ".fbs"

NAME: LETTER (LETTER | DIGIT | "_" )*
NAMESPACED_NAME: LETTER (LETTER | DIGIT | "_" | "." )* (LETTER | DIGIT)+

root_type: "root_type" NAME ";"
include: "include \"" FILEPATH "\"" ";"

enum: "enum" NAME ":" TYPE_INTS "{" enum_field* "}"
enum_field: NAME enum_field_default? ","
enum_field_default: "=" NUMBER

table: "table" NAME "{" table_field* "}"
table_field: NAME ":" (scalar_type | vector_type | NAME) table_field_default? table_field_attributes? ";"
table_field_default: "=" (WORD | NUMBER)
table_field_attributes: "(" [WORD ("," WORD)*] ")"

union: "union" NAME "{" [union_member (", " union_member)*] "}"
union_member: NAMESPACED_NAME ("=" DECIMAL_POSITIVE_INTEGER)?

TYPE_BOOL: "bool"
TYPE_INTS: "u"? "int" ("8"|"16"|"32"|"64")? | "ubyte" | "ushort" | "ulong"
           | "byte" | "short" | "long"
FLOAT_TYPES: "float" | "float32" | "double" | "float64"
STRING_TYPE: "string"
scalar_type: TYPE_BOOL | TYPE_INTS | FLOAT_TYPES
vector_type: "[" NAME "]"

module: include* namespace (table | enum | union)* root_type?

%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
""",
    start="module",
)
