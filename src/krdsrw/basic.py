import abc
import struct
import typing

from .cursor import Cursor
from .error import UnexpectedBytesError


class Basic(metaclass=abc.ABCMeta):
    builtin: type[int | float | str] = NotImplemented  # type: ignore
    magic_byte: int = NotImplemented

    @classmethod
    @abc.abstractmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        raise NotImplementedError("Must be implemented by the subclass.")

    @abc.abstractmethod
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

    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        raise NotImplementedError("Must be implemented by the subclass.")


class Byte(int, Basic):
    # signed byte
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>b')
    magic_byte: int = 0x07

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __str__(self) -> str:
        return f"0x{hex(self)}"

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>b', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>b', magic_byte_)

    @typing.override
    def to_bytes(self, *_unused, **_unused2) -> bytes:
        return struct.pack('>b', self)

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Char(int, Basic):
    # unsigned (?) char
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>B')
    magic_byte: int = 0x09

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __str__(self) -> str:
        return str(chr(self))

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>B', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>B', magic_byte_)

    @typing.override
    def to_bytes(self, *_unused, **_unused2) -> bytes:
        return struct.pack('>B', self)

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Bool(int, Basic):
    # 1-byte bool 0=false, 1=true
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>?')
    magic_byte: int = 0x00

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __str__(self) -> str:
        return str(bool(self))

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>?', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, int(self), '>?', magic_byte_)

    @typing.override
    def to_bytes(self, *_unused, **_unused2) -> bytes:
        return struct.pack('>?', self)

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Short(int, Basic):
    # 2 byte signed integer
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>h')
    magic_byte: int = 0x05

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>h', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>h', magic_byte_)

    @typing.override
    def to_bytes(self, *_unused, **_unused2) -> bytes:
        return struct.pack('>h', self)

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Int(int, Basic):
    # 4-byte signed integer
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>l')
    magic_byte: int = 0x01

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>l', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>l', magic_byte_)

    @typing.override
    def to_bytes(self, *_unused, **_unused2) -> bytes:
        return struct.pack('>l', self)

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Long(int, Basic):
    # 8-byte signed integer
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>q')
    magic_byte: int = 0x02

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>q', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>q', magic_byte_)

    @typing.override
    def to_bytes(self, *_unused, **_unused2) -> bytes:
        return struct.pack('>q', self)

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)


class Float(float, Basic):
    # 4-byte float
    builtin: type[int | float | str] = float
    size: int = struct.calcsize('>f')
    magic_byte: int = 0x06

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>f', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>f', magic_byte_)

    @typing.override
    def to_bytes(self) -> bytes:
        return struct.pack('>f', self)

    @typing.override
    def __add__(self, other: float) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: float) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: float) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: float) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: float) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: float) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: float) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: float) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: float) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: float) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: float) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: float) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)


class Double(float, Basic):
    # 8-byte float
    builtin: type[int | float | str] = float
    size: int = struct.calcsize('>d')
    magic_byte: int = 0x04

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>d', magic_byte_))

    @typing.override
    def write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>d', magic_byte_)

    @typing.override
    def to_bytes(self) -> bytes:
        return struct.pack('>d', self)

    @typing.override
    def __add__(self, other: float) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: float) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: float) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: float) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: float) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: float) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: float) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: float) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: float) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: float) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: float) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: float) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)


class Utf8Str(str, Basic):
    # 1-byte bool true if str is empty
    # then 2-byte str length (may be 0)
    # then UTF-8 str bytes of aforementioned length (empty if bool is True)
    builtin: type[int | float | str] = str
    magic_byte: int = 0x03

    @typing.override
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
        o.prefer_null = prefer_null if prefer_null is not None else True
        return o

    @typing.override
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.prefer_null: bool

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{\"{str(self)}\"}}"

    @typing.override
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

    @typing.override
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

    @typing.override
    def to_bytes(self) -> bytes:
        return self.encode("utf-8")

    @typing.override
    def __add__(self, other: str) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o, prefer_null=self.prefer_null)

    @typing.override
    def __mul__(self, other: typing.SupportsIndex) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o, prefer_null=self.prefer_null)

    @typing.override
    def __mod__(self, other: str) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o, prefer_null=self.prefer_null)

    @typing.override
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
