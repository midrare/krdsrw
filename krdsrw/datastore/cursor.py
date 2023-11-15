from __future__ import annotations
import abc
import collections
import io
import struct
import typing

from . import names
from .constants import BOOL_TYPE_INDICATOR
from .constants import INT_TYPE_INDICATOR
from .constants import LONG_TYPE_INDICATOR
from .constants import UTF8STR_TYPE_INDICATOR
from .constants import DOUBLE_TYPE_INDICATOR
from .constants import SHORT_TYPE_INDICATOR
from .constants import FLOAT_TYPE_INDICATOR
from .constants import BYTE_TYPE_INDICATOR
from .constants import CHAR_TYPE_INDICATOR
from .constants import OBJECT_BEGIN_INDICATOR
from .constants import OBJECT_END_INDICATOR
from .error import MagicStrNotFoundError
from .error import UnexpectedDataTypeError
from .error import DemarcationError


class Cursor:
    def __init__(self, data: None | typing.ByteString = None):
        self._saved_positions: typing.List[int] = []
        self._data: io.BytesIO = (
            io.BytesIO(bytes(data)) if data else io.BytesIO()
        )

    def load(self, data: typing.ByteString):
        self._data = io.BytesIO(bytes(data))

    def dump(self) -> bytes:
        return self._data.getvalue()

    def seek(self, pos: int):
        self._data.seek(pos, io.SEEK_SET)

    def skip(self, length: int):
        self._data.seek(length, io.SEEK_CUR)

    def tell(self) -> int:
        return self._data.tell()

    def __len__(self) -> int:
        return len(self._data.getbuffer())

    def __getitem__(self, item: int | slice) -> int | bytes:
        if isinstance(item, int):
            old_pos = self._data.tell()
            self._data.seek(item)
            b = self._data.read(1)
            self._data.seek(old_pos, io.SEEK_SET)
            return b
        elif isinstance(item, slice):
            old_pos = self._data.tell()
            b = bytearray()
            step = item.step if item.step is not None else 1
            self.seek((item.start if item.start is not None else 0) + step)
            while (item.stop is None or self._data.tell()
                   < item.stop) and self._data.tell() < len(
                       self._data.getbuffer()):
                b.extend(self._data.read(1))
                self._data.seek(step, io.SEEK_CUR)
            self._data.seek(old_pos, io.SEEK_SET)
            return b

        raise IndexError(
            'index of class "' + str(type(item)) + '" not supported'
        )

    def __str__(self) -> str:
        return "%s{@%d of %db}" % (
            self.__class__.__name__,
            self._data.tell(),
            len(self._data.getbuffer()),
        )

    def __getslice__(self, i: int, j: int) -> bytes:
        b = bytearray()
        old_pos = self._data.tell()
        self._data.seek(i, io.SEEK_SET)
        b.extend(self._data.read(j - i))
        self._data.seek(old_pos)
        return b

    def _read_raw_byte(self) -> int:
        b = self._data.read(1)
        if b is None or len(b) <= 0:
            raise IndexError(
                "Cannot read next byte; buffer of length %d has reached its end"
                % len(self._data.getbuffer())
            )
        return b[0]

    def _read_raw_bytes(self, length: int) -> bytes:
        return self._data.read(length)

    @typing.overload
    def read(self, length: None = None) -> int:
        ...

    @typing.overload
    def read(self, length: int) -> bytes:
        ...

    def read(self, length: None | int = None) -> int | bytes:
        if length is None:
            return self._read_raw_byte()

        return self._data.read(length)

    def _eat_raw_byte(self, expected: int) -> bool:
        old_pos = self._data.tell()
        actual = self._data.read(1)
        if len(actual) > 0 and actual[0] == expected:
            return True
        self._data.seek(old_pos, io.SEEK_SET)
        return False

    def _eat_raw_bytes(self, expected: typing.ByteString) -> bool:
        old_pos = self._data.tell()
        actual = self._data.read(len(expected))
        if actual == expected:
            return True
        self._data.seek(old_pos, io.SEEK_SET)
        return False

    def eat(self, expected: int | typing.ByteString) -> bool:
        if isinstance(expected, int):
            return self._eat_raw_byte(expected)
        else:
            return self._eat_raw_bytes(expected)

    def _peek_raw_byte(self) -> int:
        old_pos = self._data.tell()
        b = self._data.read(1)
        self._data.seek(old_pos, io.SEEK_SET)
        if len(b) <= 0:
            raise IndexError(
                "Cannot peek next byte; buffer of length %d has reached its end"
                % len(self._data.getbuffer())
            )
        return b[0]

    def _peek_raw_bytes(self, length: int) -> bytes:
        old_pos = self._data.tell()
        b = self._data.read(length)
        self._data.seek(old_pos, io.SEEK_SET)
        return b

    @typing.overload
    def peek(self, length: None = None) -> int:
        ...

    @typing.overload
    def peek(self, length: int) -> bytes:
        ...

    def peek(self, length: None | int = None) -> None | int | bytes:
        if length is None:
            return self._peek_raw_byte()
        return self._peek_raw_bytes(length)

    def peek_matches(self, data: int | typing.ByteString) -> bool:
        if isinstance(data, int):
            return self._peek_raw_byte() == data
        return self._peek_raw_bytes(len(data)) == data

    def _extend_from_current_pos(self, length: int):
        min_size = self._data.tell() + length + 1
        if len(self._data.getbuffer()) <= min_size:
            self._data.truncate(min_size)

    def _write_raw_byte(self, value: int):
        self._extend_from_current_pos(1)
        self._data.write(value.to_bytes(1, "big"))

    def _write_raw_bytes(self, value: typing.ByteString):
        self._extend_from_current_pos(len(value))
        self._data.write(value)

    def write(self, value: int | typing.ByteString):
        if isinstance(value, int):
            self._write_raw_byte(value)
        else:
            self._write_raw_bytes(value)

    def is_at_end(self) -> bool:
        return self._data.tell() + 1 >= len(self._data.getbuffer())

    def save(self):
        self._saved_positions.append(self._data.tell())

    def unsave(self):
        self._saved_positions.pop()

    def restore(self):
        pos = self._saved_positions.pop()
        self._data.seek(pos, io.SEEK_SET)

    def read_byte(self, type_byte: bool = True) -> Byte:
        if type_byte and not self._eat_raw_byte(BYTE_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), BYTE_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Byte(self._read_raw_byte())

    def write_byte(self, value: int, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(BYTE_TYPE_INDICATOR)

        self._write_raw_byte(value)

    def read_char(self, type_byte: bool = True) -> Char:
        if type_byte and not self._eat_raw_byte(CHAR_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), CHAR_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Char(self._read_raw_byte())

    def write_char(self, value: int, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(CHAR_TYPE_INDICATOR)

        self._write_raw_byte(value)

    def read_bool(self, type_byte: bool = True) -> Bool:
        if type_byte and not self._eat_raw_byte(BOOL_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), BOOL_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Bool(bool(self._read_raw_byte()))

    def write_bool(self, value: bool | int, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(BOOL_TYPE_INDICATOR)

        self._write_raw_byte(int(bool(value)))

    def read_int(self, type_byte: bool = True) -> Int:
        if type_byte and not self._eat_raw_byte(INT_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), INT_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Int(
            struct.unpack_from(
                ">l", self._read_raw_bytes(struct.calcsize(">l"))
            )[0]
        )

    def write_int(self, value: int, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(INT_TYPE_INDICATOR)

        self._write_raw_bytes(struct.pack(">l", value))

    def read_long(self, type_byte: bool = True) -> Long:
        if type_byte and not self._eat_raw_byte(LONG_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), LONG_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Long(
            struct.unpack_from(
                ">q", self._read_raw_bytes(struct.calcsize(">q"))
            )[0]
        )

    def write_long(self, value: int, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(LONG_TYPE_INDICATOR)

        self._write_raw_bytes(struct.pack(">q", value))

    def read_short(self, type_byte: bool = True) -> Short:
        if type_byte and not self._eat_raw_byte(SHORT_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), SHORT_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Short(
            struct.unpack_from(
                ">h", self._read_raw_bytes(struct.calcsize(">h"))
            )[0]
        )

    def write_short(self, value: int, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(SHORT_TYPE_INDICATOR)

        self._write_raw_bytes(struct.pack(">h", value))

    def read_float(self, type_byte: bool = True) -> Float:
        if type_byte and not self._eat_raw_byte(FLOAT_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), FLOAT_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Float(
            struct.unpack_from(
                ">f", self._read_raw_bytes(struct.calcsize(">f"))
            )[0]
        )

    def write_float(self, value: float, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(FLOAT_TYPE_INDICATOR)

        self._write_raw_bytes(struct.pack(">f", value))

    def read_double(self, type_byte: bool = True) -> Double:
        if type_byte and not self._eat_raw_byte(DOUBLE_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), DOUBLE_TYPE_INDICATOR, self._peek_raw_byte()
            )

        return Double(
            struct.unpack_from(
                ">d", self._read_raw_bytes(struct.calcsize(">d"))
            )[0]
        )

    def write_double(self, value: float, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(DOUBLE_TYPE_INDICATOR)

        self._write_raw_bytes(struct.pack(">d", value))

    def read_utf8str(self, type_byte: bool = True) -> Utf8Str:
        if type_byte and not self._eat_raw_byte(UTF8STR_TYPE_INDICATOR):
            raise UnexpectedDataTypeError(
                self._data.tell(), UTF8STR_TYPE_INDICATOR, self._peek_raw_byte()
            )
        is_empty = bool(self._read_raw_byte())
        if is_empty:
            return Utf8Str()

        # NOTE even if the is_empty byte is false, the actual str
        #   length can still be 0
        string_len = struct.unpack_from(
            ">H", self._read_raw_bytes(struct.calcsize(">H"))
        )[0]
        return Utf8Str(self._read_raw_bytes(string_len).decode("utf-8"))

    def write_utf8str(self, value: None | str, type_byte: bool = True):
        if type_byte:
            self._write_raw_byte(UTF8STR_TYPE_INDICATOR)

        is_str_null = value is None
        self._write_raw_byte(int(is_str_null))
        if not is_str_null:
            encoded = value.encode("utf-8")
            self._write_raw_bytes(struct.pack(">H", len(encoded)))
            self._write_raw_bytes(encoded)


    def read_auto(self, cls_: None|typing.Type[Byte]| typing.Type[Char] \
        | typing.Type[Bool] | typing.Type[Short] | typing.Type[Int] \
        | typing.Type[Long] | typing.Type[Float] | typing.Type[Double] \
        | typing.Type[Utf8Str] = None) -> Byte | Char | Bool | Short | Int \
        | Long | Float | Double | Utf8Str:

        if isinstance(cls_, Byte):
            return self.read_byte()
        elif isinstance(cls_, Char):
            return self.read_char()
        elif isinstance(cls_, Bool):
            return self.read_bool()
        elif isinstance(cls_, Short):
            return self.read_short()
        elif isinstance(cls_, Int):
            return self.read_int()
        elif isinstance(cls_, Long):
            return self.read_long()
        elif isinstance(cls_, Float):
            return self.read_float()
        elif isinstance(cls_, Double):
            return self.read_double()
        elif isinstance(cls_, Utf8Str):
            return self.read_utf8str()

        type_byte = self.peek()
        if type_byte == BYTE_TYPE_INDICATOR:
            return self.read_byte()
        elif type_byte == CHAR_TYPE_INDICATOR:
            return self.read_char()
        elif type_byte == BOOL_TYPE_INDICATOR:
            return self.read_bool()
        elif type_byte == SHORT_TYPE_INDICATOR:
            return self.read_short()
        elif type_byte == INT_TYPE_INDICATOR:
            return self.read_int()
        elif type_byte == LONG_TYPE_INDICATOR:
            return self.read_long()
        elif type_byte == FLOAT_TYPE_INDICATOR:
            return self.read_float()
        elif type_byte == DOUBLE_TYPE_INDICATOR:
            return self.read_double()
        elif type_byte == UTF8STR_TYPE_INDICATOR:
            return self.read_utf8str()

        raise MagicStrNotFoundError(
            f"Unrecognized type indicator byte \"{type_byte}\"."
        )

    def write_auto(
        self, value: Byte | Char | Bool | Short
        | Int | Long | Float | Double | Utf8Str
    ):
        if isinstance(value, Byte):
            self.write_byte(value)
        elif isinstance(value, Char):
            self.write_char(value)
        elif isinstance(value, Bool):
            self.write_bool(value)
        elif isinstance(value, Short):
            self.write_short(value)
        elif isinstance(value, Int):
            self.write_int(value)
        elif isinstance(value, Long):
            self.write_long(value)
        elif isinstance(value, Float):
            self.write_float(value)
        elif isinstance(value, Double):
            self.write_double(value)
        elif isinstance(value, Utf8Str):
            self.write_utf8str(value)
        else:
            raise TypeError(
                f"Value of type \"{type(value).__name__}\" "
                + " is not supported."
            )

    def peek_demarcated_name(self) -> None | str:
        name = None
        self.save()
        ch = self.read()
        if ch == OBJECT_BEGIN_INDICATOR:
            name = self.read_utf8str(False)
        self.restore()
        return name

    def peek_demarcated_type(self) -> None | type[Object]:
        cls_ = None
        self.save()
        ch = self.read()
        if ch == OBJECT_BEGIN_INDICATOR:
            name = self.read_utf8str(False)
            fct = names.get_maker_by_name(name)
            assert fct, f'Unsupported name \"{name}\".'
            cls_ = fct.cls_
        self.restore()
        return cls_

    def read_demarcated_value(self) -> Object:
        if not self.eat(OBJECT_BEGIN_INDICATOR):
            raise DemarcationError(f"Object start not found @{self.tell()}")

        name = self.read_utf8str(False)
        fct = names.get_maker_by_name(name)
        assert fct, f'Unsupported name \"{name}\".'
        value = fct.create(self)
        value._name = name  # TODO do not access private members

        if not self.eat(OBJECT_END_INDICATOR):
            raise DemarcationError(f"Object end not found @{self.tell()}")

        return value

    def write_demarcated_value(self, o: Object):
        assert o.name, 'Value must be named'
        self.write(OBJECT_BEGIN_INDICATOR)
        self.write_utf8str(o.name, False)
        o.write(self, o)
        self.write(OBJECT_END_INDICATOR)


class Value:
    @staticmethod
    def read(cursor: Cursor, *args, **kwargs) -> Value:
        raise NotImplementedError("Must be implemented by the subclass.")

    @staticmethod
    def write(cursor: Cursor, o: Value):
        raise NotImplementedError("Must be implemented by the subclass.")


class Basic(Value):
    builtin: type[int | float | str] = NotImplemented  # type: ignore
    magic_byte: int = NotImplemented

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Basic:
        raise NotImplementedError("Must be implemented by the subclass.")

    @staticmethod
    def write(cursor: Cursor, o: Basic, magic_byte: bool = True):
        raise NotImplementedError("Must be implemented by the subclass.")


class Object(Value):
    object_begin: typing.Final[int] = 0xfe
    object_end: typing.Final[int] = 0xff

    def __init__(self, _name: None | str = None):
        super().__init__()
        self._name: str = _name or ''

    @staticmethod
    def read(cursor: Cursor, *args, **kwargs) -> Object:
        raise NotImplementedError("Must be implemented by the subclass.")

    @staticmethod
    def write(cursor: Cursor, o: Object):
        raise NotImplementedError("Must be implemented by the subclass.")

    def __eq__(self, other: typing.Self) -> bool:
        raise NotImplementedError("Must be implemented by the subclass.")

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{self._name}}}"


class Byte(int, Basic):  # signed byte
    builtin: type[int | float | str] = int
    size: int = 1
    magic_byte: int = 0x07

    def __str__(self) -> str:
        return f"0x{hex(self)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Byte:
        if magic_byte and not cursor.eat(Byte.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Byte.magic_byte, cursor.peek()
            )
        return Byte(cursor.read())

    @staticmethod
    def write(cursor: Cursor, o: Byte, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Byte.magic_byte)
        cursor.write(o)


class Char(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int
    size: int = 2  # TODO check if char really is 2 bytes
    magic_byte: int = 0x09

    def __str__(self) -> str:
        return str(chr(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Char:
        if magic_byte and not cursor.eat(Char.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Char.magic_byte, cursor.peek()
            )
        return Char(cursor.read())

    @staticmethod
    def write(cursor: Cursor, o: Char, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Char.magic_byte)
        cursor.write(o)


class Bool(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int
    size: int = 1
    magic_byte: int = 0x00

    def __str__(self) -> str:
        return str(bool(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Bool:
        if magic_byte and not cursor.eat(Bool.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Bool.magic_byte, cursor.peek()
            )
        return Bool(bool(cursor.read()))

    @staticmethod
    def write(cursor: Cursor, o: Bool, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Bool.magic_byte)
        cursor.write(int(bool(o)))


class Short(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int
    size: int = 2
    magic_byte: int = 0x05

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Short:
        if magic_byte and not cursor.eat(Short.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Short.magic_byte, cursor.peek()
            )
        return Short(
            struct.unpack_from(">h", cursor.read(struct.calcsize(">h")))[0]
        )

    @staticmethod
    def write(cursor: Cursor, o: Short, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Short.magic_byte)
        cursor.write(struct.pack(">h", o))


class Int(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int
    size: int = 4
    magic_byte: int = 0x01

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Int:
        if magic_byte and not cursor.eat(Int.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Int.magic_byte, cursor.peek()
            )
        return Int(
            struct.unpack_from(">l", cursor.read(struct.calcsize(">l")))[0]
        )

    @staticmethod
    def write(cursor: Cursor, o: Int, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Int.magic_byte)
        cursor.write(struct.pack(">l", o))


class Long(int, Basic):
    builtin: typing.Final[type[int | float | str]] = int
    size: int = 8
    magic_byte: int = 0x02

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Long:
        if magic_byte and not cursor.eat(Long.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Long.magic_byte, cursor.peek()
            )
        return Long(
            struct.unpack_from(">q", cursor.read(struct.calcsize(">q")))[0]
        )

    @staticmethod
    def write(cursor: Cursor, o: Long, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Long.magic_byte)
        cursor.write(struct.pack(">q", o))


class Float(float, Basic):
    builtin: typing.Final[type[int | float | str]] = float
    size: int = 4
    magic_byte: int = 0x06

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Float:
        if magic_byte and not cursor.eat(Float.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Float.magic_byte, cursor.peek()
            )
        return Float(
            struct.unpack_from(">f", cursor.read(struct.calcsize(">f")))[0]
        )

    @staticmethod
    def write(cursor: Cursor, o: Float, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Float.magic_byte)
        cursor.write(struct.pack(">f", o))


class Double(float, Basic):
    builtin: typing.Final[type[int | float | str]] = float
    size: int = 8
    magic_byte: int = 0x04

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Double:
        if magic_byte and not cursor.eat(Double.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Double.magic_byte, cursor.peek()
            )
        return Double(
            struct.unpack_from(">d", cursor.read(struct.calcsize(">d")))[0]
        )

    @staticmethod
    def write(cursor: Cursor, o: Double, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Double.magic_byte)
        cursor.write(struct.pack(">d", o))


class Utf8Str(str, Basic):
    builtin: typing.Final[type[int | float | str]] = str
    magic_byte: int = 0x03

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{\"{str(self)}\"}}"

    @staticmethod
    def read(cursor: Cursor, magic_byte: bool = True) -> Utf8Str:
        if magic_byte and not cursor.eat(Utf8Str.magic_byte):
            raise UnexpectedDataTypeError(
                cursor.tell(), Utf8Str.magic_byte, cursor.peek()
            )

        is_empty = bool(cursor.read())
        if is_empty:
            return Utf8Str()

        # NOTE even if the is_empty byte is false, the actual str
        #   length can still be 0
        string_len = struct.unpack_from(
            ">H", cursor.read(struct.calcsize(">H"))
        )[0]
        return Utf8Str(cursor.read(string_len).decode("utf-8"))

    @staticmethod
    def write(cursor: Cursor, o: Utf8Str, magic_byte: bool = True):
        if magic_byte:
            cursor.write(Utf8Str.magic_byte)

        is_str_null = o is None
        cursor.write(int(is_str_null))
        if not is_str_null:
            encoded = o.encode("utf-8")
            cursor.write(struct.pack(">H", len(encoded)))
            cursor.write(encoded)


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
            return cursor.read_auto(self._cls)  # type: ignore
        if issubclass(self._cls, Object) and cursor:
            return self._cls.read(cursor, *self._args, **self._kwargs)
        return self._cls(*self._args, **self._kwargs)

    def is_basic(self) -> bool:
        return issubclass(self._cls, Basic)

    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls \
            and self._args == o._args \
            and self._kwargs == o._kwargs
        return super().__eq__(o)
