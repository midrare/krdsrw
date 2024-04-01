import abc
import struct
import typing

from .builtins import _Bool
from .builtins import _Byte
from .builtins import _Char
from .builtins import _Short
from .builtins import _Int
from .builtins import _Long
from .builtins import _Float
from .builtins import _Double
from .builtins import _Utf8Str
from .cursor import Cursor
from .error import UnexpectedBytesError
from .error import UnexpectedStructureError

_BYTE_SIZE: typing.Final[int] = 1
_BOOL_SIZE: typing.Final[int] = 1
_CHAR_SIZE: typing.Final[int] = 1
_SHORT_SIZE: typing.Final[int] = 2
_INT_SIZE: typing.Final[int] = 4
_LONG_SIZE: typing.Final[int] = 8
_FLOAT_SIZE: typing.Final[int] = 4
_DOUBLE_SIZE: typing.Final[int] = 8
_BOOL_MAGIC_BYTE: typing.Final[int] = 0
_INT_MAGIC_BYTE: typing.Final[int] = 1
_LONG_MAGIC_BYTE: typing.Final[int] = 2
_UTF8STR_MAGIC_BYTE: typing.Final[int] = 3
_DOUBLE_MAGIC_BYTE: typing.Final[int] = 4
_SHORT_MAGIC_BYTE: typing.Final[int] = 5
_FLOAT_MAGIC_BYTE: typing.Final[int] = 6
_BYTE_MAGIC_BYTE: typing.Final[int] = 0x07
_CHAR_MAGIC_BYTE: typing.Final[int] = 9


def _read_unpack(
        csr: Cursor,
        fmt: str,
        magic_byte: None | int = None) -> int | float | str | bytes:
    if magic_byte is not None and not csr.eat(magic_byte):
        raise UnexpectedBytesError(csr.tell(), magic_byte, csr.peek())
    return struct.unpack_from(fmt, csr.read(struct.calcsize(fmt)))[0]


def _write_pack(
        csr: Cursor,
        o: int | float | str,
        fmt: str,
        magic_byte: None | int = None):
    if magic_byte is not None:
        csr.write(magic_byte)
    csr.write(struct.pack(fmt, o))


def read_byte(csr: Cursor, magic_byte: bool = True) -> int:
    from .basics import Byte
    magic_byte_ = _BYTE_MAGIC_BYTE if magic_byte else None
    return Byte(_read_unpack(csr, '>b', magic_byte_))


def write_byte(csr: Cursor, value: int, magic_byte: bool = True):
    magic_byte_ = _BYTE_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>b', magic_byte_)


def read_char(csr: Cursor, magic_byte: bool = True) -> int:
    from .basics import Char
    magic_byte_ = _CHAR_MAGIC_BYTE if magic_byte else None
    return Char(_read_unpack(csr, '>B', magic_byte_))


def write_char(csr: Cursor, value: int, magic_byte: bool = True):
    magic_byte_ = _CHAR_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>B', magic_byte_)


def read_bool(csr: Cursor, magic_byte: bool = True) -> bool | int:
    from .basics import Bool
    magic_byte_ = _BOOL_MAGIC_BYTE if magic_byte else None
    return Bool(_read_unpack(csr, '>?', magic_byte_))


def write_bool(csr: Cursor, value: bool | int, magic_byte: bool = True):
    magic_byte_ = _BOOL_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>?', magic_byte_)


def read_int(csr: Cursor, magic_byte: bool = True) -> int:
    from .basics import Int
    magic_byte_ = _INT_MAGIC_BYTE if magic_byte else None
    return Int(_read_unpack(csr, '>l', magic_byte_))


def write_int(csr: Cursor, value: int, magic_byte: bool = True):
    magic_byte_ = _INT_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>l', magic_byte_)


def read_long(csr: Cursor, magic_byte: bool = True) -> int:
    from .basics import Long
    magic_byte_ = _LONG_MAGIC_BYTE if magic_byte else None
    return Long(_read_unpack(csr, '>q', magic_byte_))


def write_long(csr: Cursor, value: int, magic_byte: bool = True):
    magic_byte_ = _LONG_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>q', magic_byte_)


def read_short(csr: Cursor, magic_byte: bool = True) -> int:
    from .basics import Short
    magic_byte_ = _SHORT_MAGIC_BYTE if magic_byte else None
    return Short(_read_unpack(csr, '>h', magic_byte_))


def write_short(csr: Cursor, value: int, magic_byte: bool = True):
    magic_byte_ = _SHORT_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>h', magic_byte_)


def read_float(csr: Cursor, magic_byte: bool = True) -> float:
    from .basics import Float
    magic_byte_ = _FLOAT_MAGIC_BYTE if magic_byte else None
    return Float(_read_unpack(csr, '>f', magic_byte_))


def write_float(csr: Cursor, value: float, magic_byte: bool = True):
    magic_byte_ = _FLOAT_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>f', magic_byte_)


def read_double(csr: Cursor, magic_byte: bool = True) -> float:
    from .basics import Double
    magic_byte_ = _DOUBLE_MAGIC_BYTE if magic_byte else None
    return Double(_read_unpack(csr, '>d', magic_byte_))


def write_double(csr: Cursor, value: float, magic_byte: bool = True):
    magic_byte_ = _DOUBLE_MAGIC_BYTE if magic_byte else None
    _write_pack(csr, value, '>d', magic_byte_)


def read_utf8str(csr: Cursor, magic_byte: bool = True) -> str:
    if magic_byte and not csr.eat(_UTF8STR_MAGIC_BYTE):
        raise UnexpectedBytesError(csr.tell(), _UTF8STR_MAGIC_BYTE, csr.peek())

    if csr.read() > 0:  # true if empty string
        return ''

    from .basics import Utf8Str
    # NOTE even if the is_empty byte is false, the actual str
    #   length can still be 0
    read_len = struct.unpack_from(">H", csr.read(struct.calcsize(">H")))[0]
    return Utf8Str(csr.read(read_len).decode("utf-8"))


def write_utf8str(csr: Cursor, value: None | str, magic_byte: bool = True):
    if magic_byte:
        csr.write(_UTF8STR_MAGIC_BYTE)

    is_str_null = value is None
    csr.write(int(is_str_null))
    if not is_str_null:
        encoded = value.encode("utf-8")
        csr.write(struct.pack(">H", len(encoded)))
        csr.write(encoded)


def peek_basic_type(csr) -> None | type:
    from .basics import Bool
    from .basics import Byte
    from .basics import Char
    from .basics import Short
    from .basics import Int
    from .basics import Long
    from .basics import Float
    from .basics import Double
    from .basics import Utf8Str
    b = csr.peek()

    for t in [ Bool, Byte, Char, Short, Int, Long, Float, Double, Utf8Str ]:
        if b == t.magic_byte:
            return t

    return None


class Basic(metaclass=abc.ABCMeta):
    builtin: type[int | float | str] = NotImplemented  # type: ignore
    magic_byte: int = NotImplemented

    @classmethod
    @abc.abstractmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        raise NotImplementedError("Must be implemented by the subclass.")

    @abc.abstractmethod
    def _write(self, cursor: Cursor, magic_byte: bool = True):
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
    def __bytes__(self) -> bytes:
        raise NotImplementedError("Must be implemented by the subclass.")


class Byte(_Byte, Basic):
    # signed byte
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>b')
    magic_byte: int = 0x07

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>b', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>b', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>b', self)


class Char(_Char, Basic):
    # unsigned (?) char
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>B')
    magic_byte: int = 0x09

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>B', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>B', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>B', self)


class Bool(_Bool, Basic):
    # 1-byte bool 0=false, 1=true
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>?')
    magic_byte: int = 0x00

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>?', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, int(self), '>?', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>?', self)


class Short(_Short, Basic):
    # 2 byte signed integer
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>h')
    magic_byte: int = 0x05

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>h', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>h', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>h', self)


class Int(_Int, Basic):
    # 4-byte signed integer
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>l')
    magic_byte: int = 0x01

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>l', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>l', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>l', self)


class Long(_Long, Basic):
    # 8-byte signed integer
    builtin: type[int | float | str] = int
    size: int = struct.calcsize('>q')
    magic_byte: int = 0x02

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>q', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>q', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>q', self)


class Float(_Float, Basic):
    # 4-byte float
    builtin: type[int | float | str] = float
    size: int = struct.calcsize('>f')
    magic_byte: int = 0x06

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>f', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>f', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>f', self)


class Double(_Double, Basic):
    # 8-byte float
    builtin: type[int | float | str] = float
    size: int = struct.calcsize('>d')
    magic_byte: int = 0x04

    @typing.override
    @classmethod
    def create(cls, cursor: Cursor, magic_byte: bool = True) -> typing.Self:
        magic_byte_ = cls.magic_byte if magic_byte else None
        return cls(cls._read_unpack(cursor, '>d', magic_byte_))

    @typing.override
    def _write(self, cursor: Cursor, magic_byte: bool = True):
        magic_byte_ = self.magic_byte if magic_byte else None
        self._write_pack(cursor, self, '>d', magic_byte_)

    @typing.override
    def __bytes__(self) -> bytes:
        return struct.pack('>d', self)


class Utf8Str(_Utf8Str, Basic):
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
    def _write(self, cursor: Cursor, magic_byte: bool = True):
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
    def __bytes__(self) -> bytes:
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
