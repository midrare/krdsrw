import typing


class Basic:
    builtin: type[int | float | str] = int


class Byte(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int

    def __str__(self) -> str:
        return f"0x{hex(self)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self)}}}"


class Char(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int

    def __str__(self) -> str:
        return str(chr(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self)}}}"


class Bool(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int

    def __str__(self) -> str:
        return str(bool(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self)}}}"


class Short(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"


class Int(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"


class Long(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"


class Float(float, Basic):
    builtin: typing.Final[type[int | float | str]] = float

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"


class Double(float, Basic):
    builtin: typing.Final[type[int | float | str]] = float

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"


class Utf8Str(str, Basic):
    builtin: typing.Final[type[int | float | str]] = str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{\"{str(self)}\"}}"


ALL_BASIC_TYPES: typing.Final[tuple[type, ...]] = (
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
