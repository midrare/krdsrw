import inspect
import struct
import typing

from .cursor import Cursor
from .error import UnexpectedBytesError
from .error import UnexpectedStructureError


class Value:
    pass


class Basic(Value):
    builtin: type[int | float | str] = NotImplemented  # type: ignore
    magic_byte: int = NotImplemented

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        raise NotImplementedError("Must be implemented by the subclass.")

    def write(self, cursor: Cursor, magic_byte: bool = True):
        raise NotImplementedError("Must be implemented by the subclass.")

    @classmethod
    def _read_unpack(
            cls,
            cursor: Cursor,
            fmt: str,
            magic_byte: None | int = None) -> int | float | str | bytes:
        if magic_byte is not None and not cursor.eat(magic_byte):
            raise UnexpectedBytesError(cursor.tell(), magic_byte, cursor.peek())
        return struct.unpack_from(fmt, cursor.read(struct.calcsize(fmt)))[0]

    @classmethod
    def _write_pack(
            cls,
            cursor: Cursor,
            o: int | float | str,
            fmt: str,
            magic_byte: None | int = None):
        if magic_byte is not None:
            cursor.write(magic_byte)
        cursor.write(struct.pack(fmt, o))

    def to_bytes(self) -> bytes:
        raise NotImplementedError("Must be implemented by the subclass.")


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

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>b', magic_byte_))

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>b', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>b', self)

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

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>B', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>B', self)

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

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, int(self), '>?', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>?', self)

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

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>h', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>h', self)

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

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>l', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>l', self)

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

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>q', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>q', self)

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

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>f', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>f', self)

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

    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>d', magic_byte_)

    def to_bytes(self) -> bytes:
        return struct.pack('>d', self)

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

    def __new__(
        cls,
        *args,
        prefer_null: typing.Optional[bool] = None,
        **kwargs,
    ) -> typing.Self:
        o = super().__new__(cls, *args, *kwargs)
        if prefer_null is None:
            for e in args:
                if isinstance(e, cls):
                    prefer_null = e.prefer_null
                    break
        o.prefer_null: bool = prefer_null if prefer_null is not None else True
        return o

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{\"{str(self)}\"}}"

    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        if magic_byte and not cursor.eat(cls.magic_byte):
            raise UnexpectedBytesError(
                cursor.tell(), cls.magic_byte, cursor.peek())

        value = ''
        prefer_null = True

        if cursor.read() > 0:  # 1-byte bool, true if str is empty
            return cls(value, prefer_null=prefer_null)

        # NOTE actual str length can still be 0
        string_len = struct.unpack_from(
            ">H", cursor.read(struct.calcsize(">H")))[0]
        value = cursor.read(string_len).decode("utf-8")

        if string_len <= 0:
            prefer_null = False

        return cls(value, prefer_null=prefer_null)

    def write(self, cursor: Cursor, magic_byte: bool = True):
        if magic_byte:
            cursor.write(self.magic_byte)

        if not self and self.prefer_null:
            cursor.write(1)
        else:
            cursor.write(0)

        if self or not self.prefer_null:
            encoded = self.encode("utf-8")
            cursor.write(struct.pack(">H", len(encoded)))
            cursor.write(encoded)

    def to_bytes(self) -> bytes:
        return self.encode("utf-8")

    def __add__(self, other: str) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o, prefer_null=self.prefer_null)

    def __mul__(self, other: typing.SupportsIndex) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o, prefer_null=self.prefer_null)

    def __mod__(self, other: str) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o, prefer_null=self.prefer_null)

    def __rmul__(self, other: typing.SupportsIndex) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o, prefer_null=self.prefer_null)

    def __copy__(self) -> typing.Self:
        return self.__class__(self, prefer_null=self.prefer_null)

    def __deepcopy__(self) -> typing.Self:
        return self.__class__(self, prefer_null=self.prefer_null)


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
    def read(self, cursor: Cursor):
        raise NotImplementedError("Must be implemented by the subclass.")

    def write(self, cursor: Cursor):
        raise NotImplementedError("Must be implemented by the subclass.")

    def __eq__(self, other: typing.Self) -> bool:
        raise NotImplementedError("Must be implemented by the subclass.")


T = typing.TypeVar("T", bound=Byte | Char | Bool | Short | Int | Long \
    | Float | Double | Utf8Str | Object)


class Spec(typing.Generic[T]):
    # named object data structure (schema utf8str + data)
    _OBJECT_BEGIN: typing.Final[int] = 0xfe
    # end of data for object
    _OBJECT_END: typing.Final[int] = 0xff

    def __init__(self, cls_: type[T], *args, **kwargs):
        super().__init__()

        if not issubclass(cls_, ALL_BASIC_TYPES) \
        and not issubclass(cls_, Object):
            raise TypeError(f"Unsupported type \"{cls_.__name__}\".")

        self._cls: typing.Final[type[T]] = cls_
        self._args: typing.Final[list] = list(args)
        self._kwargs: typing.Final[dict] = dict(kwargs)

    @property
    def cls_(self) -> type[T]:
        return self._cls

    def read(self, cursor: Cursor, name: None | str = None) -> T:
        o = None

        if name:
            if not cursor.eat(self._OBJECT_BEGIN):
                raise UnexpectedBytesError(
                    cursor.tell(), self._OBJECT_BEGIN, cursor.peek())

            name_ = cursor.read_utf8str(False)
            if not name_:
                raise UnexpectedStructureError('Object has blank name.')
            if name_ != name:
                raise UnexpectedStructureError(
                    f"Expected object name \"{name}\""
                    + f" but got \"{name_}\".")

        if issubclass(self._cls, Basic):
            o = self._cls.create(cursor, *self._args, **self._kwargs)
        elif issubclass(self._cls, Object):
            o = self._cls(*self._args, **self._kwargs)
            o.read(cursor)

        assert isinstance(o, (Basic, Object)), 'Value is of unsupported type'

        if name and not cursor.eat(self._OBJECT_END):
            raise UnexpectedBytesError(
                cursor.tell(), self._OBJECT_END, cursor.peek())

        assert o is not None, 'Failed to create object'
        return o

    def make(self) -> T:
        return self._cls(*self._args, **self._kwargs)

    def write(self, cursor: Cursor, o: T, name: None | str = None):
        if name:
            cursor.write(self._OBJECT_BEGIN)
            cursor.write_utf8str(name, False)
        o.write(cursor)
        if name:
            cursor.write(self._OBJECT_END)

    def is_basic(self) -> bool:
        return issubclass(self._cls, Basic)

    def is_container(self) -> bool:
        return issubclass(self._cls, (tuple, list, dict))

    def is_object(self) -> bool:
        return issubclass(self._cls, Object)

    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls \
            and self._args == o._args \
            and self._kwargs == o._kwargs
        return super().__eq__(o)

    def is_instance(self, o: typing.Any) -> bool:
        return isinstance(o, self._cls)

    def is_subclass(self, cls_: type) -> bool:
        return issubclass(cls_, self._cls)

    def is_castable(self, o: typing.Any) -> bool:
        return isinstance(o, self._cls) \
        or (issubclass(self._cls, Basic) \
            and (builtin := getattr(self._cls, 'builtin'))
            and isinstance(o, builtin))

    def is_compatible(self, o: typing.Any) -> bool:
        if inspect.isclass(o):
            return issubclass(o, self._cls) \
            or ((builtin := getattr(self._cls, 'builtin')) \
            and inspect.isclass(builtin) and issubclass(o, builtin))
        return isinstance(o, self._cls) \
        or ((builtin := getattr(self._cls, 'builtin')) \
        and inspect.isclass(builtin) and isinstance(o, builtin))

    def cast(self, o: typing.Any) -> T:
        if issubclass(self._cls, list):
            o2 = self._cls(*self._args, *self._kwargs)
            o2.extend(o)
            return o2

        if issubclass(self._cls, dict):
            o2 = self._cls(*self._args, *self._kwargs)
            o2.update(o)
            return o2

        return self._cls(o, *self._args, **self._kwargs)

    def default(self) -> T:
        return self._cls()
