from __future__ import annotations
import re

from .cursor import Cursor
from .value import Value


class Byte(Value):
    def __init__(self, value: None | int = None):
        self.value: int = value if value is not None else 0

    def read(self, cursor: Cursor):
        self.value = cursor.read_byte()

    def write(self, cursor: Cursor):
        cursor.write_byte(self.value)

    def __eq__(self, other: Byte) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self.value)}}}"

    def __str__(self) -> str:
        return f"0x{hex(self.value)}"


class Char(Value):
    def __init__(self, value: None | int = None):
        self.value: int = value if value is not None else 0

    def read(self, cursor: Cursor):
        self.value = cursor.read_char()

    def write(self, cursor: Cursor):
        cursor.write_char(self.value)

    def __eq__(self, other: Bool) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return str(chr(self.value))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self.value)}}}"


class Bool(Value):
    def __init__(self, value: None | bool = None):
        self.value: bool = value if value is not None else False

    def read(self, cursor: Cursor):
        self.value = cursor.read_bool()

    def write(self, cursor: Cursor):
        cursor.write_bool(self.value)

    def __eq__(self, other: Bool) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return str(bool(self.value))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self.value)}}}"


class Short(Value):
    def __init__(self, value: None | int = None):
        self.value: int = value if value is not None else 0

    def read(self, cursor: Cursor):
        self.value = cursor.read_short()

    def write(self, cursor: Cursor):
        cursor.write_short(self.value)

    def __eq__(self, other: Short) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self.value}}}"


class Int(Value):
    def __init__(self, value: None | int = None):
        self.value: int = value if value is not None else 0

    def read(self, cursor: Cursor):
        self.value = cursor.read_int()

    def write(self, cursor: Cursor):
        cursor.write_int(self.value)

    def __eq__(self, other: Int) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self.value}}}"


class Long(Value):
    def __init__(self, value: None | int = None):
        self.value: int = value if value is not None else 0

    def read(self, cursor: Cursor):
        self.value = cursor.read_long()

    def write(self, cursor: Cursor):
        cursor.write_long(self.value)

    def __eq__(self, other: Long) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self.value}}}"


class Float(Value):
    def __init__(self, value: None | float = None):
        self.value: float = value if value is not None else 0.0

    def read(self, cursor: Cursor):
        self.value = cursor.read_float()

    def write(self, cursor: Cursor):
        cursor.write_float(self.value)

    def __eq__(self, other: Float) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self.value}}}"


class Double(Value):
    def __init__(self, value: None | float = None):
        self.value: float = value if value is not None else 0.0

    def read(self, cursor: Cursor):
        self.value = cursor.read_double()

    def write(self, cursor: Cursor):
        cursor.write_double(self.value)

    def __eq__(self, other: Double) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self.value}}}"


class Utf8Str(Value):
    def __init__(self, value: None | str = None):
        self.value: None | str = value if value is not None else None

    def read(self, cursor: Cursor):
        self.value = cursor.read_utf8str()

    def write(self, cursor: Cursor):
        cursor.write_utf8str(self.value)

    def __eq__(self, other: Utf8Str) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        return self.value if self.value is not None else ""

    def __repr__(self) -> str:
        s = re.sub(r"\\s+", " ", self.value) if self.value is not None else None
        s2 = f'"{s.strip()}"' if s is not None else ""
        return f"{self.__class__.__name__}{{{s2}}}"
