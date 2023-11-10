from __future__ import annotations
from .constants import *
from .primitives import *
from .value import Value


def read_auto(
    cursor: Cursor,
) -> Byte | Char | Bool | Short | Int | Long | Float | Double | Utf8Str:
    type_byte = cursor.peek()
    cls = None

    if type_byte == BYTE_TYPE_INDICATOR:
        cls = Byte
    elif type_byte == CHAR_TYPE_INDICATOR:
        cls = Char
    elif type_byte == BOOL_TYPE_INDICATOR:
        cls = Bool
    elif type_byte == SHORT_TYPE_INDICATOR:
        cls = Short
    elif type_byte == INT_TYPE_INDICATOR:
        cls = Int
    elif type_byte == LONG_TYPE_INDICATOR:
        cls = Long
    elif type_byte == FLOAT_TYPE_INDICATOR:
        cls = Float
    elif type_byte == DOUBLE_TYPE_INDICATOR:
        cls = Double
    elif type_byte == UTF8STR_TYPE_INDICATOR:
        cls = Utf8Str

    assert cls is not None, "Unrecognized type"
    value = cls()
    value.read(cursor)

    return value


def write_auto(cursor: Cursor, value: Value):
    value.write(cursor)
