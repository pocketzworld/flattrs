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

COMMENT: "//" /.*/ "\n"
         | "/*" /(.|\n|\r)+/ "*/"

NAMESPACE_NAME: LETTER (LETTER | DIGIT | "_" | ".")*
FILEPATH: (LETTER | DIGIT | "_" | "." | "/")+ ".fbs"

NAME: LETTER (LETTER | DIGIT | "_" )*
NAMESPACED_NAME: LETTER (LETTER | DIGIT | "_" | "." )* (LETTER | DIGIT | "_")+

root_type: "root_type" NAME ";"
include: "include \"" FILEPATH "\"" ";"

enum: "enum" NAME ":" INT_TYPES "{" [ enum_field ("," enum_field)*] ","? "}"
enum_field: NAME enum_field_default?
enum_field_default: "=" NUMBER

table: "table" NAME attributes? "{" table_field* "}"
table_field: NAME ":" (scalar_type | vector_type | NAMESPACED_NAME) table_field_default? attributes? ";"
table_field_default: "=" (NAMESPACED_NAME | NUMBER)
attributes: "(" [WORD ("," WORD)*] ")"

union: "union" NAME "{" [union_member (("," union_member ","?)* | ",")] "}"
union_member: NAMESPACED_NAME ("=" DECIMAL_POSITIVE_INTEGER)?

attribute: "attribute \"" NAME "\"" ";"

BOOL_TYPE: "bool"
INT_TYPES: "u"? "int" ("8"|"16"|"32"|"64")? | "ubyte" | "ushort" | "ulong"
           | "byte" | "short" | "long"
FLOAT_TYPES: "float" | "float32" | "double" | "float64"
STRING_TYPE: "string"
scalar_type: BOOL_TYPE | INT_TYPES | FLOAT_TYPES
vector_type: "[" NAMESPACED_NAME "]"

module: include* namespace? (table | enum | union | attribute)* root_type?

%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
%ignore COMMENT
""",
    start="module",
)
