from __future__ import annotations
import collections
import struct
import typing

from .cursor import Cursor
from .error import UnexpectedDataTypeError


class Value:
    @classmethod
    def create(cls, cursor: Cursor) -> typing.Self:
        raise NotImplementedError("Must be implemented by the subclass.")

    @classmethod
    def write(cls, cursor: Cursor, o: typing.Self):
        raise NotImplementedError("Must be implemented by the subclass.")


class Basic(Value):
    builtin: type[int | float | str] = NotImplemented  # type: ignore
    magic_byte: int = NotImplemented

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        raise NotImplementedError("Must be implemented by the subclass.")

    @classmethod
    def write(cls, cursor: Cursor, o: typing.Self, magic_byte: bool = True):
        raise NotImplementedError("Must be implemented by the subclass.")

    @staticmethod
    def _read_unpack(
            cursor: Cursor,
            fmt: str,
            magic_byte: None | int = None) -> int | float | str | bytes:
        if magic_byte is not None and not cursor.eat(magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), magic_byte, cursor.peek())
        return struct.unpack_from(fmt, cursor.read(struct.calcsize(fmt)))[0]

    @staticmethod
    def _write_pack(
            cursor: Cursor,
            o: int | float | str,
            fmt: str,
            magic_byte: None | int = None):
        if magic_byte is not None:
            cursor.write(magic_byte)
        cursor.write(struct.pack(fmt, o))


class Byte(int, Basic):
    # signed byte
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>b')
    magic_byte: int = 0x07

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __str__(self) -> str:
        return f"0x{hex(self)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self)}}}"

    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: int) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: int) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>b', magic_byte_))

    @classmethod
    def write(
            cls, cursor: Cursor, o: int | typing.Self, magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, o, '>b', magic_byte_)


class Char(int, Basic):
    # unsigned (?) char
    builtin: typing.Final[type[int | float | str]] = int
    size: int = struct.calcsize('>B')
    magic_byte: int = 0x09

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __str__(self) -> str:
        return str(chr(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self)}}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>B', magic_byte_))

    @classmethod
    def write(
            cls, cursor: Cursor, o: int | typing.Self, magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, o, '>B', magic_byte_)

    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: int) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: int) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Bool(int, Basic):
    # 1-byte bool 0=false, 1=true
    builtin: typing.Final[type[int | float | str]] = int
    size: int = struct.calcsize('>?')
    magic_byte: int = 0x00

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __str__(self) -> str:
        return str(bool(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self)}}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>?', magic_byte_))

    @classmethod
    def write(
            cls,
            cursor: Cursor,
            o: bool | int | typing.Self,
            magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, int(o), '>?', magic_byte_)

    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: int) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: int) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Short(int, Basic):
    # 2 byte signed integer
    builtin: typing.Final[type[int | float | str]] = int
    size: int = struct.calcsize('>h')
    magic_byte: int = 0x05

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>h', magic_byte_))

    @classmethod
    def write(
            cls, cursor: Cursor, o: int | typing.Self, magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, o, '>h', magic_byte_)

    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: int) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: int) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Int(int, Basic):
    # 4-byte signed integer
    builtin: typing.Final[type[int | float | str]] = int
    size: int = struct.calcsize('>l')
    magic_byte: int = 0x01

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>l', magic_byte_))

    @classmethod
    def write(
            cls, cursor: Cursor, o: int | typing.Self, magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, o, '>l', magic_byte_)

    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: int) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: int) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Long(int, Basic):
    # 8-byte signed integer
    builtin: typing.Final[type[int | float | str]] = int
    size: int = struct.calcsize('>q')
    magic_byte: int = 0x02

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>q', magic_byte_))

    @classmethod
    def write(
            cls, cursor: Cursor, o: int | typing.Self, magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, o, '>q', magic_byte_)

    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: int) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: int) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Float(float, Basic):
    # 4-byte float
    builtin: typing.Final[type[int | float | str]] = float
    size: int = struct.calcsize('>f')
    magic_byte: int = 0x06

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>f', magic_byte_))

    @classmethod
    def write(
            cls,
            cursor: Cursor,
            o: float | typing.Self,
            magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, o, '>f', magic_byte_)

    def __add__(self, other: float) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: float) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: float) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: float) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: float) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: float) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: float) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __radd__(self, other: float) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: float) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: float) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: float) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: float) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: float) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: float) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)


class Double(float, Basic):
    # 8-byte float
    builtin: typing.Final[type[int | float | str]] = float
    size: int = struct.calcsize('>d')
    magic_byte: int = 0x04

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>d', magic_byte_))

    @classmethod
    def write(
            cls,
            cursor: Cursor,
            o: float | typing.Self,
            magic_byte: bool = True):
        magic_byte_ = cls.magic_byte if magic_byte else None
        cls._write_pack(cursor, o, '>d', magic_byte_)

    def __add__(self, other: float) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __sub__(self, other: float) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    def __mul__(self, other: float) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __truediv__(self, other: float) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: float) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    def __mod__(self, other: float) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __divmod__(self, other: float) -> typing.Self:
        o = super().__divmod__(other)
        return self.__class__(o)

    def __pow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    def __radd__(self, other: float) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    def __rsub__(self, other: float) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    def __rmul__(self, other: float) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __rtruediv__(self, other: float) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    def __rfloordiv__(self, other: float) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    def __rmod__(self, other: float) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    def __rdivmod__(self, other: float) -> typing.Self:
        o = super().__rdivmod__(other)
        return self.__class__(o)

    def __rpow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)


class Utf8Str(str, Basic):
    # 1-byte bool true if str is empty
    # then 2-byte str length (may be 0)
    # then UTF-8 str bytes of aforementioned length (empty if bool is True)
    builtin: typing.Final[type[int | float | str]] = str
    magic_byte: int = 0x03

    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{\"{str(self)}\"}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        if magic_byte and not cursor.eat(cls.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), cls.magic_byte, cursor.peek())

        if cursor.read() > 0:  # 1-byte bool, true if str is empty
            return cls()

        # NOTE even if the is_empty byte is false, the actual str
        #   length can still be 0
        string_len = struct.unpack_from(
            ">H", cursor.read(struct.calcsize(">H")))[0]
        return cls(cursor.read(string_len).decode("utf-8"))

    @classmethod
    def write(
            cls, cursor: Cursor, o: str | typing.Self, magic_byte: bool = True):
        if magic_byte:
            cursor.write(cls.magic_byte)

        is_str_null = o is None
        cursor.write(int(is_str_null))
        if not is_str_null:
            encoded = o.encode("utf-8")
            cursor.write(struct.pack(">H", len(encoded)))
            cursor.write(encoded)

    def __add__(self, other: str) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    def __mul__(self, other: typing.SupportsIndex) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    def __mod__(self, other: str) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    def __rmul__(self, other: typing.SupportsIndex) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)


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


class Object(Value):
    # named object data structure (name utf8str + data)
    object_begin: int = 0xfe
    # end of data for object
    object_end: int = 0xff

    def __init__(self, *args, _name: None | str = None, **kwargs):
        super().__init__()
        self._name: str = _name or ''

    @classmethod
    def create(cls, cursor: Cursor, *init_args, **init_kwargs) -> typing.Self:
        init_kwargs = init_kwargs.copy()
        name = init_kwargs.pop('_name')
        o = cls(*init_args, **init_kwargs)
        o._name = name or ''
        cls.read(cursor, o)
        return o

    @classmethod
    def read(cls, cursor: Cursor, o: typing.Self):
        raise NotImplementedError("Must be implemented by the subclass.")

    @classmethod
    def write(cls, cursor: Cursor, o: typing.Self):
        raise NotImplementedError("Must be implemented by the subclass.")

    def __eq__(self, other: typing.Self) -> bool:
        raise NotImplementedError("Must be implemented by the subclass.")

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{self._name}}}"


T = typing.TypeVar("T", bound=Byte | Char | Bool | Short | Int | Long \
    | Float | Double | Utf8Str | Object)


class ValueFactory(typing.Generic[T]):
    def __init__(self, cls_: type[T], *args, **kwargs):
        super().__init__()

        if not any(issubclass(cls_, c) for c in ALL_BASIC_TYPES) \
        and issubclass(cls_, Object):
            raise TypeError(f"Unsupported type \"{type(cls_).__name__}\".")

        self._cls: typing.Final[type[T]] = cls_
        self._args: typing.Final[list] = list(args)
        self._kwargs: typing.Final[dict] = collections.OrderedDict(kwargs)

    @property
    def cls_(self) -> type[T]:
        return self._cls

    def create(self, cursor: None | Cursor = None) -> T:
        if issubclass(self._cls, Basic) and cursor:
            return self._cls.create(cursor, *self._args, **self._kwargs)
        if issubclass(self._cls, Object) and cursor:
            return self._cls.create(cursor, *self._args, **self._kwargs)
        return self._cls(*self._args, **self._kwargs)

    def is_basic(self) -> bool:
        return issubclass(self._cls, Basic)

    def is_object(self) -> bool:
        return issubclass(self._cls, Object)

    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls \
            and self._args == o._args \
            and self._kwargs == o._kwargs
        return super().__eq__(o)


# def read_value(self, cls_: None | type[
#     Byte|Char|Bool|Short|Int|Long|Float|Double|Utf8Str|Object] = None,
#     magic_byte: bool = True
# ) -> None | Byte | Char | Bool | Short | Int | Long \
# | Float | Double | Utf8Str | Object:
#     if cls_ and issubclass(cls_, Basic):
#         return cls_.read(self, magic_byte)

#     if magic_byte:
#         magic_byte_ = self.peek()
#         for cls_ in ALL_BASIC_TYPES:
#             assert issubclass(cls_, Basic)
#             if magic_byte_ == cls_.builtin:
#                 return cls_.read(self)  # type: ignore

#         if magic_byte_ == Object.object_begin:
#             self.save()

#             self.eat(Object.object_begin)
#             name = Utf8Str.read(self, False)
#             fct = names.get_maker_by_name(name)
#             assert fct, f'Unsupported name \"{name}\".'
#             value = fct.create(self)
#             value._name = name  # TODO do not access private members

#             if self.eat(Object.object_end):
#                 self.unsave()
#             else:
#                 value = None
#                 self.restore()

#             return value

#         raise MagicStrNotFoundError(
#             f"Unrecognized magic byte 0x{hex(magic_byte_)}.")

#     return None

# def write_value(
#         self,
#         cls_: type[Byte | Char | Bool | Short | Int | Long | Float | Double
#                    | Utf8Str | Object],
#         o: int | float | str | Byte | Char | Bool | Short
#     | Int | Long | Float | Double | Utf8Str | Object,
#         magic_byte: bool = True):
#     if issubclass(cls_, Basic):
#         assert isinstance(o, cls_)
#         cls_.write(self, o, magic_byte)
#     elif issubclass(cls_, Object):
#         assert isinstance(o, cls_)
#         assert o.name, 'Value must be named'
#         if magic_byte:
#             self.write(Object.object_begin)
#         Utf8Str.write(self, o.name, False)
#         cls_.write(self, o)
#         if magic_byte:
#             self.write(Object.object_end)
#     else:
#         raise TypeError(
#             f"Value of type \"{type(o).__name__}\" " + " is not supported.")

# def read_auto(self) -> int|float|str:
#     type_byte = self.peek()
#     if type_byte == _BYTE_MAGIC_BYTE:
#         return self.read_byte()
#     elif type_byte == _CHAR_MAGIC_BYTE:
#         return self.read_char()
#     elif type_byte == _BOOL_MAGIC_BYTE:
#         return self.read_bool()
#     elif type_byte == _SHORT_MAGIC_BYTE:
#         return self.read_short()
#     elif type_byte == _INT_MAGIC_BYTE:
#         return self.read_int()
#     elif type_byte == _LONG_MAGIC_BYTE:
#         return self.read_long()
#     elif type_byte == _FLOAT_MAGIC_BYTE:
#         return self.read_float()
#     elif type_byte == _DOUBLE_MAGIC_BYTE:
#         return self.read_double()
#     elif type_byte == _UTF8STR_MAGIC_BYTE:
#         return self.read_utf8str()

#     raise MagicStrNotFoundError(
#         f"Unrecognized type indicator byte \"{type_byte}\".")
