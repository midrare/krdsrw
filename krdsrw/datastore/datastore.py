from __future__ import annotations
import typing

from .containers import NameMap
from .cursor import Cursor
from .error import UnexpectedBytesError
from .types import Long
from .types import Object


class DataStore(NameMap):
    MAGIC_STR: typing.Final[bytes] = b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
    FIXED_MYSTERY_NUM: typing.Final[int] = (
        1  # present after the signature; unknown what this number means
    )

    def __init__(self):
        super().__init__()

    @staticmethod
    def _eat_signature_or_error(cursor: Cursor):
        if not cursor.eat(DataStore.MAGIC_STR):
            raise UnexpectedBytesError(
                cursor.tell(),
                DataStore.MAGIC_STR,
                cursor.peek(len(DataStore.MAGIC_STR)),
            )

    @staticmethod
    def _eat_fixed_mystery_num_or_error(cursor: Cursor):
        cursor.save()
        value = cursor.read_long()
        if value != DataStore.FIXED_MYSTERY_NUM:
            cursor.restore()
            raise UnexpectedBytesError(
                cursor.tell(),
                Long.to_bytes(DataStore.FIXED_MYSTERY_NUM),
                Long.to_bytes(value),
            )
        cursor.unsave()

    def read(self, cursor: Cursor):
        self.clear()
        self._eat_signature_or_error(cursor)
        self._eat_fixed_mystery_num_or_error(cursor)
        self.read(cursor)

    def write(self, cursor: Cursor):
        cursor.write(DataStore.MAGIC_STR)
        cursor.write_long(DataStore.FIXED_MYSTERY_NUM)
        self.write(cursor)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{str(self)}}}"
