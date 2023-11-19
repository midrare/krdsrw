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

    @classmethod
    def _eat_signature_or_error(cls, cursor: Cursor):
        if not cursor.eat(cls.MAGIC_STR):
            raise UnexpectedBytesError(
                cursor.tell(),
                cls.MAGIC_STR,
                cursor.peek(len(cls.MAGIC_STR)),
            )

    @classmethod
    def _eat_fixed_mystery_num_or_error(cls, cursor: Cursor):
        cursor.save()
        value = cursor.read_long()
        if value != cls.FIXED_MYSTERY_NUM:
            cursor.restore()
            raise UnexpectedBytesError(
                cursor.tell(),
                Long(cls.FIXED_MYSTERY_NUM).to_bytes(),
                Long(value).to_bytes(),
            )
        cursor.unsave()

    def read(self, cursor: Cursor):
        self.clear()
        self._eat_signature_or_error(cursor)
        self._eat_fixed_mystery_num_or_error(cursor)
        self.read(cursor)

    def write(self, cursor: Cursor):
        cursor.write(self.MAGIC_STR)
        cursor.write_long(self.FIXED_MYSTERY_NUM)
        self.write(cursor)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{str(self)}}}"
