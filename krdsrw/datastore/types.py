import re
import typing


class Byte(int):
    base: typing.Final[typing.Type] = int

    def __str__(self) -> str:
        return f"0x{hex(self)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self)}}}"


class Char(int):
    base: typing.Final[typing.Type] = int

    def __str__(self) -> str:
        return str(chr(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self)}}}"


class Bool(int):
    base: typing.Final[typing.Type] = int

    def __str__(self) -> str:
        return str(bool(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self)}}}"


class Short(int):
    base: typing.Final[typing.Type] = int

    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Int(int):
    base: typing.Final[typing.Type] = int

    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Long(int):
    base: typing.Final[typing.Type] = int

    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Float(float):
    base: typing.Final[typing.Type] = float

    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Double(float):
    base: typing.Final[typing.Type] = float

    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Utf8Str(str):
    base: typing.Final[typing.Type] = str

    def __repr__(self) -> str:
        s = re.sub(r"\\s+", " ", self) if self is not None else None
        s2 = f'"{s.strip()}"' if s is not None else ""
        return f"{self.__class__.__name__}{{{s2}}}"


ALL_PRIMITIVE_TYPES: typing.Final[tuple[typing.Type, ...]] = (
    Byte,
    Char,
    Bool,
    Short,
    Int,
    Long,
    Float,
    Double,
    Utf8Str,
)
