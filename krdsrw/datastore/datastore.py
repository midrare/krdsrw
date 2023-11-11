from __future__ import annotations
import typing

from .types import *
from .cursor import Cursor
from .error import *
from .value import Value


class DataStore(Value):
    SIGNATURE: typing.Final[bytes] = b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
    FIXED_MYSTERY_NUM: typing.Final[int] = (
        1  # present after the signature; unknown what this number means
    )

    def __init__(self):
        self.value: NameMap = NameMap()

    def read(self, cursor: Cursor):
        self.value = NameMap()
        self._eat_signature_or_error(cursor)
        self._eat_fixed_mystery_num_or_error(cursor)
        self.value.read(cursor)

    @staticmethod
    def _eat_signature_or_error(cursor):
        if not cursor.eat(DataStore.SIGNATURE):
            raise MagicStrNotFoundError(
                "Expected signature 0x%s at pos %d but got 0x%s" % (
                    DataStore.SIGNATURE.hex(),
                    cursor.tell(),
                    cursor.peek(len(DataStore.SIGNATURE)),
                )
            )

    @staticmethod
    def _eat_fixed_mystery_num_or_error(cursor):
        cursor.save()
        value = cursor.read_long()
        if value != DataStore.FIXED_MYSTERY_NUM:
            cursor.restore()
            raise MagicStrNotFoundError(
                "Expected fixed num 0x%08x at pos %d but got 0x%08x" %
                (DataStore.FIXED_MYSTERY_NUM, cursor.tell(), value)
            )
        cursor.unsave()

    def write(self, cursor: Cursor):
        cursor.write(DataStore.SIGNATURE)
        cursor.write_long(DataStore.FIXED_MYSTERY_NUM)
        self.value.write(cursor)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return super().__eq__(other)

    def __str__(self) -> str:
        return "%s{%s}" % (self.__class__.__name__, str(self.value))
