from __future__ import annotations
import abc
import collections.abc
import io
import typing


class Cursor:
    def __init__(
        self, data: None | typing.ByteString | typing.BinaryIO = None
    ):
        self._saved_positions: typing.List[int] = []
        self._data: io.BytesIO = io.BytesIO()

        if isinstance(data, io.BytesIO):
            self._data = data
        elif isinstance(
            data,
            (
                collections.abc.Buffer,
                collections.abc.Sequence,
                collections.abc.MutableSequence,
            ),
        ):
            self._data = io.BytesIO(data)

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
            while (
                item.stop is None or self._data.tell() < item.stop
            ) and self._data.tell() < len(self._data.getbuffer()):
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
                "Cannot read next byte; buffer of length "
                + f"{len(self._data.getbuffer())} "
                + "has reached its end"
            )
        return b[0]

    def _read_raw_bytes(self, length: int) -> bytes:
        return self._data.read(length)

    @typing.overload
    def read(self, length: None = None) -> int: ...

    @typing.overload
    def read(self, length: int) -> bytes: ...

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
                "Cannot peek next byte; buffer of length "
                + f"{len(self._data.getbuffer())} "
                + "has reached its end"
            )
        return b[0]

    def _peek_raw_bytes(self, length: int) -> bytes:
        old_pos = self._data.tell()
        b = self._data.read(length)
        self._data.seek(old_pos, io.SEEK_SET)
        return b

    @typing.overload
    def peek(self, length: None = None) -> int: ...

    @typing.overload
    def peek(self, length: int) -> bytes: ...

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


class Serializable(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        raise NotImplementedError("Must be implemented by the subclass.")

    @abc.abstractmethod
    def _write(self, cursor: Cursor):
        raise NotImplementedError("Must be implemented by the subclass.")
