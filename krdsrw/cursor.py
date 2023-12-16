from __future__ import annotations
import io
import struct
import typing

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
_BYTE_MAGIC_BYTE: typing.Final[int] = 7
_CHAR_MAGIC_BYTE: typing.Final[int] = 9
_OBJECT_BEGIN_INDICATOR: typing.Final[int] = 254
_OBJECT_END_INDICATOR: typing.Final[int] = 255


class Cursor:
    def __init__(self, data: None | typing.ByteString = None):
        self._saved_positions: typing.List[int] = []
        self._data: io.BytesIO = (
            io.BytesIO(bytes(data)) if data else io.BytesIO())

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
            'index of class "' + str(type(item)) + '" not supported')

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
                % len(self._data.getbuffer()))
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
                % len(self._data.getbuffer()))
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

    def startswith(self, data: int | typing.ByteString) -> bool:
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

    def _read_unpack(
            self,
            fmt: str,
            magic_byte: None | int = None) -> int | float | str | bytes:
        if magic_byte is not None and not self._eat_raw_byte(magic_byte):
            raise UnexpectedBytesError(
                self._data.tell(), magic_byte, self._peek_raw_byte())
        return struct.unpack_from(
            fmt, self._read_raw_bytes(struct.calcsize(fmt)))[0]

    def _write_pack(
            self,
            o: int | float | str,
            fmt: str,
            magic_byte: None | int = None):
        if magic_byte is not None:
            self.write(magic_byte)
        self.write(struct.pack(fmt, o))

    def read_byte(self, magic_byte: bool = True) -> int:
        from .types import Byte
        magic_byte_ = _BYTE_MAGIC_BYTE if magic_byte else None
        return Byte(self._read_unpack('>b', magic_byte_))

    def write_byte(self, value: int, magic_byte: bool = True):
        magic_byte_ = _BYTE_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>b', magic_byte_)

    def read_char(self, magic_byte: bool = True) -> int:
        from .types import Char
        magic_byte_ = _CHAR_MAGIC_BYTE if magic_byte else None
        return Char(self._read_unpack('>B', magic_byte_))

    def write_char(self, value: int, magic_byte: bool = True):
        magic_byte_ = _CHAR_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>B', magic_byte_)

    def read_bool(self, magic_byte: bool = True) -> bool | int:
        from .types import Bool
        magic_byte_ = _BOOL_MAGIC_BYTE if magic_byte else None
        return Bool(self._read_unpack('>?', magic_byte_))

    def write_bool(self, value: bool | int, magic_byte: bool = True):
        magic_byte_ = _BOOL_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>?', magic_byte_)

    def read_int(self, magic_byte: bool = True) -> int:
        from .types import Int
        magic_byte_ = _INT_MAGIC_BYTE if magic_byte else None
        return Int(self._read_unpack('>l', magic_byte_))

    def write_int(self, value: int, magic_byte: bool = True):
        magic_byte_ = _INT_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>l', magic_byte_)

    def read_long(self, magic_byte: bool = True) -> int:
        from .types import Long
        magic_byte_ = _LONG_MAGIC_BYTE if magic_byte else None
        return Long(self._read_unpack('>q', magic_byte_))

    def write_long(self, value: int, magic_byte: bool = True):
        magic_byte_ = _LONG_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>q', magic_byte_)

    def read_short(self, magic_byte: bool = True) -> int:
        from .types import Short
        magic_byte_ = _SHORT_MAGIC_BYTE if magic_byte else None
        return Short(self._read_unpack('>h', magic_byte_))

    def write_short(self, value: int, magic_byte: bool = True):
        magic_byte_ = _SHORT_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>h', magic_byte_)

    def read_float(self, magic_byte: bool = True) -> float:
        from .types import Float
        magic_byte_ = _FLOAT_MAGIC_BYTE if magic_byte else None
        return Float(self._read_unpack('>f', magic_byte_))

    def write_float(self, value: float, magic_byte: bool = True):
        magic_byte_ = _FLOAT_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>f', magic_byte_)

    def read_double(self, magic_byte: bool = True) -> float:
        from .types import Double
        magic_byte_ = _DOUBLE_MAGIC_BYTE if magic_byte else None
        return Double(self._read_unpack('>d', magic_byte_))

    def write_double(self, value: float, magic_byte: bool = True):
        magic_byte_ = _DOUBLE_MAGIC_BYTE if magic_byte else None
        self._write_pack(value, '>d', magic_byte_)

    def read_utf8str(self, magic_byte: bool = True) -> str:
        if magic_byte and not self._eat_raw_byte(_UTF8STR_MAGIC_BYTE):
            raise UnexpectedBytesError(
                self._data.tell(), _UTF8STR_MAGIC_BYTE, self._peek_raw_byte())

        if self._read_raw_byte() > 0:  # true if empty string
            return ''

        from .types import Utf8Str
        # NOTE even if the is_empty byte is false, the actual str
        #   length can still be 0
        read_len = struct.unpack_from(
            ">H", self._read_raw_bytes(struct.calcsize(">H")))[0]
        return Utf8Str(self._read_raw_bytes(read_len).decode("utf-8"))

    def write_utf8str(self, value: None | str, magic_byte: bool = True):
        if magic_byte:
            self._write_raw_byte(_UTF8STR_MAGIC_BYTE)

        is_str_null = value is None
        self._write_raw_byte(int(is_str_null))
        if not is_str_null:
            encoded = value.encode("utf-8")
            self._write_raw_bytes(struct.pack(">H", len(encoded)))
            self._write_raw_bytes(encoded)

    def peek_basic_type(self) -> None | type:
        from . import types
        b = self._peek_raw_byte()

        for t in [types.Bool, types.Byte, types.Char, types.Short, types.Int,
                  types.Long, types.Float, types.Double, types.Utf8Str]:
            if b == t.magic_byte:
                return t

        return None

    def peek_object_schema(self, magic_byte: bool = True) -> None | str:
        schema = None
        self.save()
        if not magic_byte or self._eat_raw_byte(_OBJECT_BEGIN_INDICATOR):
            schema = self.read_utf8str(False)
        self.restore()
        return schema

    def peek_object_type(self, magic_byte: bool = True) -> None | type:
        from . import schemas
        cls_ = None
        self.save()

        if not magic_byte or self._eat_raw_byte(_OBJECT_BEGIN_INDICATOR):
            schema = self.read_utf8str(False)
            fct = schemas.get_spec_by_name(schema)
            assert fct, f'Unsupported schema \"{schema}\".'
            cls_ = fct.cls_

        self.restore()
        return cls_

    def read_object(self, name: None | str = None) -> tuple[typing.Any, str]:
        assert name is None or name, 'expected either null or non-empty name'
        from . import schemas

        name_ = self.peek_object_schema()
        if not name_:
            raise UnexpectedStructureError('Failed to read name for object.')
        if name is not None and name_ != name:
            raise UnexpectedStructureError(
                f'Object name "{name_}" does not match expected name "{name}"')
        maker = schemas.get_spec_by_name(name_)
        if not maker:
            raise UnexpectedStructureError(f'Unsupported schema \"{name_}\".')
        o = maker.read(self, name_)
        return o, name_

    def write_object(self, o: typing.Any, name: str):
        assert name, 'expected non-empty name'
        self._write_raw_byte(_OBJECT_BEGIN_INDICATOR)
        self.write_utf8str(name, False)
        o.write(self)
        self._write_raw_byte(_OBJECT_END_INDICATOR)
