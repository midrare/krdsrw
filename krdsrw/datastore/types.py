import re


class Byte(int):
    def __str__(self) -> str:
        return f"0x{hex(self)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self)}}}"


class Char(int):
    def __str__(self) -> str:
        return str(chr(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self)}}}"


class Bool(int):
    def __str__(self) -> str:
        return str(bool(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self)}}}"


class Short(int):
    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Int(int):
    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Long(int):
    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Float(float):
    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Double(float):
    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self}}}"


class Utf8Str(str):
    def __repr__(self) -> str:
        s = re.sub(r"\\s+", " ", self) if self is not None else None
        s2 = f'"{s.strip()}"' if s is not None else ""
        return f"{self.__class__.__name__}{{{s2}}}"
