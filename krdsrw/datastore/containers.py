from __future__ import annotations
import base64
import collections
import collections.abc
import copy
import inspect
import json
import typing

from . import schemas
from .cursor import Cursor
from .error import FieldNotFoundError
from .error import UnexpectedBytesError
from .error import UnexpectedNameError
from .error import UnexpectedFieldError
from .types import ALL_BASIC_TYPES
from .types import Object
from .types import Value
from .types import ValueFactory
from .types import Basic
from .types import Byte
from .types import Char
from .types import Bool
from .types import Short
from .types import Int
from .types import Long
from .types import Float
from .types import Double
from .types import Utf8Str

K = typing.TypeVar("K", bound=int | float | str)
T = typing.TypeVar("T", bound=Byte | Char | Bool | Short | Int | Long \
    | Float | Double | Utf8Str | Object)


def _to_ctype(o: typing.Any, cls_: type) -> typing.Any:
    if isinstance(o, dict):
        for key in list(o.keys()):
            o[key] = _to_ctype(o[key], cls_)
        return o

    if isinstance(o, list):
        for i in range(len(o)):
            o[i] = _to_ctype(o[i], cls_)
        return o

    if issubclass(cls_, Basic) and isinstance(o, cls_.builtin):
        return cls_(o)

    if issubclass(cls_, Object) and isinstance(o, Object):
        return o

    if issubclass(cls_, (bool, int, float, str)) \
    and isinstance(o, cls_):
        return o

    raise TypeError(f"Unexpected type \"{type(o).__name__}\".")


def _is_val_compatible(o: typing.Any, cls_: type) -> bool:
    if issubclass(cls_, Basic) and isinstance(o, cls_.builtin):
        return True
    return isinstance(o, cls_)


def _is_type_compatible(t: type, cls_: type) -> bool:
    if issubclass(cls_, Basic) and issubclass(t, cls_.builtin):
        return True
    return issubclass(t, cls_)


def _read_basic(cursor: Cursor) \
-> None|Bool|Char|Byte|Short|Int|Long|Float|Double|Utf8Str:
    for t in [ Bool, Byte, Char, Short, Int, Long, Float, Double, Utf8Str ]:
        if cursor._peek_raw_byte() == t.magic_byte:
            return t.create(cursor)

    return None


def _read_object(
    cursor: Cursor
) -> tuple[Bool | Char | Byte | Short | Int | Long | Float | Double | Utf8Str
           | Object, None | str]:
    # named object data structure (schema utf8str + data)
    OBJECT_BEGIN: typing.Final[int] = 0xfe
    # end of data for object
    OBJECT_END: typing.Final[int] = 0xff

    if not cursor.eat(OBJECT_BEGIN):
        raise UnexpectedBytesError(cursor.tell(), OBJECT_BEGIN, cursor.peek())

    schema = cursor.read_utf8str(False)
    if not schema:
        raise UnexpectedNameError('Failed to read schema for object.')

    if maker := schemas.get_maker_by_schema(schema):
        assert maker, f"Unsupported schema {schema}"
        value = maker.create()
        value.read(cursor)
    else:
        value = _read_basic(cursor)

    assert isinstance(
        value,
        (Bool, Char, Byte, Short, Int, Long, Float, Double, Utf8Str,
         Object)), 'Value is of unsupported type'

    if not cursor.eat(OBJECT_END):
        raise UnexpectedBytesError(cursor.tell(), OBJECT_END, cursor.peek())

    return value, schema


class _TypeCheckedList(list[T]):
    def __init__(self):
        super().__init__()

    def _is_write_allowed(self, o: typing.Any) -> bool:
        return True

    def _transform_write(self, o: typing.Any) -> T:
        return o

    @typing.overload
    def __setitem__(self, i: typing.SupportsIndex, o: int | float | str | T):
        ...

    @typing.overload
    def __setitem__(
        self,
        i: slice,
        o: typing.Iterable[int | float | str | T],
    ):
        ...

    def __setitem__(
            self, i: typing.SupportsIndex | slice, o: int | float | str
        | T | typing.Iterable[int | float | str | T]):
        if not isinstance(i, slice):
            if not self._is_write_allowed(o):
                raise ValueError(f"Value \"{o}\" is not allowed.")
            o = self._transform_write(o)
            super().__setitem__(i, o)
        else:
            assert isinstance(o, collections.abc.Iterable)
            o = list(o)  # type: ignore
            for e in o:
                if not self._is_write_allowed(e):
                    raise ValueError(f"Value \"{e}\" is not allowed.")
            o = [self._transform_write(e) for e in o]
            super().__setitem__(i, o)

    def __add__(
            self, other: typing.Iterable[int | float | str | T]) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._is_write_allowed(e):
                raise ValueError(f"Value \"{e}\" is not allowed.")
        o = self.copy()
        o.extend(self._transform_write(e) for e in other)
        return o

    def __iadd__(
            self, other: typing.Iterable[int | float | str | T]) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._is_write_allowed(e):
                raise ValueError(f"Value \"{e}\" is not allowed.")
        self.extend(self._transform_write(e) for e in other)
        return self

    def append(self, o: int | float | str | T):
        if not self._is_write_allowed(o):
            raise ValueError(f"Value \"{o}\" is not allowed.")
        super().append(self._transform_write(o))

    def insert(self, i: int, o: int | float | str | T):
        if not self._is_write_allowed(o):
            raise ValueError(f"Value \"{o}\" is not allowed.")
        super().insert(i, self._transform_write(o))

    def copy(self) -> typing.Self:
        return copy.copy(self)

    def extend(self, other: typing.Iterable[int | float | str | T]):
        other = list(other)
        for e in other:
            if not self._is_write_allowed(e):
                raise ValueError(f"Value \"{e}\" is not allowed.")
        super().extend(self._transform_write(e) for e in other)

    def count(self, o: bool | int | float | str | T) -> int:
        return super().count(o)  # type: ignore


class Vector(_TypeCheckedList[T], Object):
    # Array can contain Basic and other containers

    def __init__(self, maker: type[T] | ValueFactory[T]):
        super().__init__()
        if not isinstance(maker, ValueFactory):
            maker = ValueFactory(maker)
        self._maker: typing.Final[ValueFactory[T]] = maker

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            self.append(self._maker.create(cursor))

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_int(len(self))
        for e in self:
            e.write(cursor)

    @property
    def cls_(self) -> type[T]:
        return self._maker.cls_

    @typing.override
    def _is_write_allowed(self, o: typing.Any) -> bool:
        return isinstance(o, self._maker.cls_)

    @typing.override
    def _transform_write(self, o: typing.Any) -> T:
        return o


class _TypeCheckedDict(collections.OrderedDict[K, T]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _is_read_allowed(self, key: typing.Any) -> bool:
        return True

    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        return True

    def _transform_read(self, key: typing.Any) -> K:
        return key

    def _transform_write(self, key: typing.Any,
                         value: typing.Any) -> tuple[K, T]:
        return value

    @classmethod
    def fromkeys(
        cls,
        iterable: typing.Iterable[bool | int | float | str],
        value: T,
    ) -> typing.Self:
        keys = list(iterable)

        def cast(key, val) -> tuple[K, T]:
            if not key in keys:
                raise ValueError(f"Key \"{key}\" is not allowed.")

            if val is None:
                val = copy.deepcopy(value)

            val = _to_ctype(val, value.__class__)
            if not isinstance(val, value.__class__):
                raise ValueError(f"Value \"{value}\" is not allowed.")

            return key, val

        o = cls(cast)
        for key in keys:
            o[key] = value  # type: ignore

        return o

    @typing.override
    def setdefault(self, key: K, default: None | T = None) -> T:
        if not self._is_write_allowed(key, default):
            raise ValueError(
                f"Write to key \"{key}\" of"
                + f" value \"{default}\" is not allowed.")

        key, default = self._transform_write(key, default)
        return super().setdefault(key, default)

    @typing.override
    def update(self, *args: typing.Mapping[K, T], **kwargs: T):
        d = collections.OrderedDict()
        for key, value in collections.OrderedDict(*args, **kwargs).items():
            if not self._is_write_allowed(key, value):
                raise ValueError(
                    f"Write to key \"{key}\" of"
                    + f" value \"{value}\" is not allowed.")
            key, value = self._transform_write(key, value)
            d[key] = value
        super().update(d)

    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return dict(o) == dict(self)
        return super().__eq__(o)

    def __contains__(self, key: typing.Any) -> bool:
        key = self._transform_read(key)
        return super().__contains__(key)

    def __delitem__(self, key: K):
        if not self._is_read_allowed(key):
            raise KeyError(f"Key \"{key}\" cannot be read.")
        key = self._transform_read(key)
        return super().__delitem__(key)

    def __getitem__(self, key: K) -> T:
        if not self._is_read_allowed(key):
            raise KeyError(f"Key \"{key}\" cannot be read.")

        key = self._transform_read(key)
        return super().__getitem__(key)

    def __setitem__(self, key: K, item: int | float | str | T):
        if not self._is_write_allowed(key, item):
            raise ValueError(
                f"Write to key \"{key}\" of"
                + f" value \"{item}\" is not allowed.")
        key, item = self._transform_write(key, item)
        super().__setitem__(key, item)


class Record(_TypeCheckedDict[str, T], Object):
    # Record can contain basics and other containers
    # keys are just arbitrary aliases for convenience. values are
    # hardcoded and # telling the difference between what is what
    # is determined # by their order of appearance

    def __init__(
        self,
        required: typing.Dict[str, ValueFactory[T]],
        optional: None | typing.Dict[str, ValueFactory[T]] = None,
    ):
        super().__init__()

        self._required: typing.Final[typing.Dict[str, ValueFactory[T]]] \
            = collections.OrderedDict(required)
        self._optional: typing.Final[typing.Dict[str, ValueFactory[T]]] \
            = collections.OrderedDict(optional or {})

        for k, v in self._required.items():
            self[k] = v.create()

    @typing.override
    def _is_read_allowed(self, key: typing.Any) -> bool:
        return isinstance(key, str) \
        and (key in self._required or key in self._optional)

    @typing.override
    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        if not key in self._required and not key in self._optional:
            return False
        if value is not None:
            maker = self._required.get(key) or self._optional.get(key)
            if maker and not isinstance(value, maker.cls_):
                return False
        return True

    @typing.override
    def _transform_read(self, key: typing.Any) -> str:
        return key

    @typing.override
    def _transform_write(self, key: typing.Any,
                         value: typing.Any) -> tuple[str, T]:
        if value is None:
            maker = self._required.get(key) or self._optional.get(key)
            if not maker:
                raise Exception(f"No default value for key \"{key}\".")
            value = maker.create()
            assert value is not None, 'Maker failed to create value'
        return key, value

    @property
    def required(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._required.items() }

    @property
    def optional(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._optional.items() }

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()

        for schema, val_maker in self._required.items():
            if not self._read_next(cursor, schema, val_maker):
                raise FieldNotFoundError(
                    'Expected field with schema "%s" but was not found'
                    % schema)

        for schema, val_maker in self._optional.items():
            if not self._read_next(cursor, schema, val_maker):
                break

    def _read_next(
        self,
        cursor: Cursor,
        schema: str,
        val_maker: ValueFactory[T],
    ) -> bool:
        cursor.save()
        try:
            self[schema] = val_maker.create(cursor)
            cursor.unsave()
            return True
        except UnexpectedBytesError:
            cursor.restore()
            return False

    @typing.override
    def write(self, cursor: Cursor):
        for schema, val_maker in self._required.items():
            assert isinstance(self[schema], val_maker.cls_)
            self[schema].write(cursor)

        for schema, val_maker in self._optional.items():
            value = self.get(schema)
            if value is None:
                break
            assert isinstance(value, val_maker.cls_)
            value.write(cursor)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._required == other._required
                and self._optional == other._optional
                and collections.OrderedDict(self) \
                == collections.OrderedDict(other)
            )
        return super().__eq__(other)

    def __str__(self) -> str:
        d = { k: v for k, v in self.items() if v is not None }
        return f"{self.__class__.__name__}{str(d)}"


class IntMap(_TypeCheckedDict[int, Bool | Char | Byte | Short | Int | Long
                              | Float | Double | Utf8Str | Object], Object):
    # named object data structure (schema utf8str + data)
    _OBJECT_BEGIN: typing.Final[int] = 0xfe
    # end of data for object
    _OBJECT_END: typing.Final[int] = 0xff

    def __init__(
        self,
        idx_to_schema: None | dict[int | str, str],
        idx_to_type: None | dict[int | str, type[Basic | Object]],
        idx_to_alias: None | dict[int | str, str],
    ):
        super().__init__()

        self._idx_to_schema: dict[int|str, str] = \
        copy.deepcopy(idx_to_schema or {})
        self._idx_to_type: dict[int|str, type[Basic|Object]] = \
        copy.deepcopy(idx_to_type or {})
        self._idx_to_alias: dict[int|str, str] = \
        copy.deepcopy(idx_to_alias or {})

    @typing.override
    def _is_read_allowed(self, key: typing.Any) -> bool:
        return key in self._idx_to_schema \
        or key in self._idx_to_type \
        or key in self._idx_to_alias \
        or key in self._idx_to_alias.values()

    @typing.override
    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        if not key in self._idx_to_schema \
        and not key in self._idx_to_type \
        and not key in self._idx_to_alias \
        and not key in self._idx_to_alias.values():
            return False

        if not isinstance(value, self._idx_to_type[key]):
            return False

        return True

    @typing.override
    def _transform_read(self, key: typing.Any) -> int | str:
        return next((k for k, v in self._idx_to_alias.items() if v == key), key)

    @typing.override
    def _transform_write(
        self, key: typing.Any, value: typing.Any
    ) -> tuple[int | str, Bool | Char | Byte | Short | Int | Long | Float
               | Double | Utf8Str | Object]:
        key = next((k for k, v in self._idx_to_alias.items() if v == key), key)
        return key, value

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            idxnum = cursor.read_int()

            if not idxnum in self._idx_to_schema \
            and not idxnum in self._idx_to_type \
            and not idxnum in self._idx_to_alias:
                raise UnexpectedNameError(
                    f"Object index number {idxnum} not recognized")

            value, schema = _read_object(cursor)
            assert schema == self._idx_to_schema[idxnum], 'Schema mismatch'
            self[idxnum] = value

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_int(len(self))

        for idx, value in self.items():
            cursor.write_int(idx)
            cursor.write_byte(self._OBJECT_BEGIN)

            schema = self._idx_to_schema[idx]
            cursor.write_utf8str(schema, False)
            value.write(cursor)
            cursor.write_byte(self._OBJECT_END, False)


class DynamicMap(_TypeCheckedDict[str, Bool | Char | Byte | Short | Int | Long
                                  | Float | Double | Utf8Str | Object], Object):
    def __init__(self):
        super().__init__()

    @typing.override
    def _is_read_allowed(self, key: typing.Any) -> bool:
        return isinstance(key, str)

    @typing.override
    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        return isinstance(key, str) and isinstance(value, (Basic, Object))

    @typing.override
    def _transform_read(self, key: typing.Any) -> str:
        return key

    @typing.override
    def _transform_write(
        self, key: typing.Any, value: typing.Any
    ) -> tuple[str, Bool | Char | Byte | Short | Int | Long | Float | Double
               | Utf8Str | Object]:
        return key, value

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            key = cursor.read_utf8str()
            value = _read_basic(cursor)
            assert value is not None, 'Value not found'
            self[key] = value

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_int(len(self))
        for idx, value in self.items():
            assert isinstance(idx, str)
            cursor.write_utf8str(idx)
            value.write(cursor)


class DateTime(Object):
    def __init__(self):
        super().__init__()
        self._value: int = -1  # -1 is null

    @property
    def epoch_ms(self) -> int:
        return self._value

    @epoch_ms.setter
    def epoch_ms(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Value must be an {int.__name__}")
        self._value = max(-1, value)

    @typing.override
    def read(self, cursor: Cursor):
        self._value = cursor.read_long()

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_long(max(-1, self._value))

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value
        return super().__eq__(other)


class Json(Object):
    def __init__(self):
        super().__init__()
        self._value: None | bool | int | float | str | list | dict = None

    @property
    def value(self) -> None | bool | int | float | str | list | dict:
        return self._value

    @value.setter
    def value(self, value: None | bool | int | float | str | list | dict):
        allowed = (bool, int, float, str, list, dict)
        if value is not None and not isinstance(value, allowed):
            class_names = ', '.join([c.__name__ for c in allowed])
            raise TypeError(f"value is must be one of {class_names}")
        self._value = value

    @typing.override
    def read(self, cursor: Cursor):
        s = cursor.read_utf8str()
        self._value = json.loads(s) if s is not None and s else None

    @typing.override
    def write(self, cursor: Cursor):
        s = json.dumps(self._value) if self._value is not None else ""
        cursor.write_utf8str(s)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value
        return super().__eq__(other)


class LastPageRead(Object):  # aka LPR. this is kindle reading pos info
    EXTENDED_LPR_VERSION: typing.Final[int] = 2

    def __init__(self):
        super().__init__()
        self._pos: Position = Position()
        self._timestamp: int = -1
        self._lpr_version: int = -1

    @property
    def pos(self) -> Position:
        return self._pos

    @property
    def lpr_version(self) -> int:
        return self._lpr_version

    @lpr_version.setter
    def lpr_version(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._lpr_version = value

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._timestamp = value

    @typing.override
    def read(self, cursor: Cursor):
        self._pos.char_pos = -1
        self._pos.chunk_eid = -1
        self._pos.chunk_pos = -1
        self._timestamp = -1
        self._lpr_version = -1

        type_byte = cursor.peek()
        if type_byte == Utf8Str.magic_byte:
            # old LPR version'
            self._pos.read(cursor)
        elif type_byte == Byte.magic_byte:
            # new LPR version
            self._lpr_version = cursor.read_byte()
            self._pos.read(cursor)
            self._timestamp = int(cursor.read_long())
        else:
            raise UnexpectedFieldError(
                f"Expected Utf8Str or byte but got {type_byte}")

    @typing.override
    def write(self, cursor: Cursor):
        # XXX may cause problems if kindle expects the original LPR format
        #   version when datastore file is re-written
        if self._timestamp is None or self._timestamp < 0:
            # old LPR version
            self._pos.write(cursor)
        else:
            # new LPR version
            lpr_version = max(self.EXTENDED_LPR_VERSION, self._lpr_version)
            cursor.write_byte(lpr_version)
            self._pos.write(cursor)
            cursor.write_long(self._timestamp)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._pos == other._pos and self._timestamp == other.timestamp
                and self._lpr_version == other._lpr_version)
        return super().__eq__(other)

    def __str__(self) -> str:
        return (
            self.__class__.__name__ + ":" + str({
                "lpr_version": self._lpr_version,
                "timestamp": self._timestamp,
                "pos": self._pos,
            }))


class Position(Object):
    PREFIX_VERSION1: typing.Final[int] = 0x01

    def __init__(self):
        super().__init__()
        self._chunk_eid: int = -1
        self._chunk_pos: int = -1
        self._value: int = -1

    @property
    def chunk_eid(self) -> int:
        return self._chunk_eid

    @chunk_eid.setter
    def chunk_eid(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._chunk_eid = value

    @property
    def chunk_pos(self) -> int:
        return self._chunk_pos

    @chunk_pos.setter
    def chunk_pos(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._chunk_pos = value

    @property
    def char_pos(self) -> int:
        return self._value

    @char_pos.setter
    def char_pos(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value is not of type {int.__name__}")
        self._value = value

    @typing.override
    def read(self, cursor: Cursor):
        s = cursor.read_utf8str()
        split = s.split(":", 2)
        if len(split) > 1:
            b = base64.b64decode(split[0])
            version = b[0]
            if version == self.PREFIX_VERSION1:
                self._chunk_eid = int.from_bytes(b[1:5], "little")
                self._chunk_pos = int.from_bytes(b[5:9], "little")
            else:
                # TODO throw a proper exception
                raise Exception(
                    "Unrecognized position version 0x%02x" % version)
            self._value = int(split[1])
        else:
            self._value = int(s)

    @typing.override
    def write(self, cursor: Cursor):
        s = ""
        if self._chunk_eid >= 0 and self._chunk_pos >= 0:
            b_version = self.PREFIX_VERSION1.to_bytes(1, "little", signed=False)
            b_eid = self._chunk_eid.to_bytes(4, "little", signed=False)
            b_pos = self._chunk_pos.to_bytes(4, "little", signed=False)
            s += base64.b64encode(b_version + b_eid + b_pos).decode("ascii")
            s += ":"
        s += str(
            self._value if self._value is not None and self._value >= 0 else -1)
        cursor.write_utf8str(s)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value \
            and self._chunk_eid == other._chunk_eid \
            and self._chunk_pos == other._chunk_pos
        return super().__eq__(other)

    def __str__(self) -> str:
        d = {
            "chunk_eid": self._chunk_eid,
            "chunk_pos": self._chunk_pos,
            "char_pos": self._value,
        }
        d = { k: v for k, v in d.items() if v >= 0 }
        return f"{self.__class__.__name__}{str(d)}"


class TimeZoneOffset(Object):
    def __init__(self):
        super().__init__()
        self._value: int = -1  # -1 is null

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value must be an {int.__name__}")
        self._value = value

    @typing.override
    def read(self, cursor: Cursor):
        self._value = cursor.read_long()

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_long(max(-1, self._value))

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value

        return super().__eq__(other)


class DataStore(_TypeCheckedDict[str, Bool | Char | Byte | Short | Int | Long
                                 | Float | Double | Utf8Str | Object], Object):
    MAGIC_STR: typing.Final[bytes] = b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
    FIXED_MYSTERY_NUM: typing.Final[int] = (
        1  # present after the signature; unknown what this number means
    )

    # named object data structure (schema utf8str + data)
    _OBJECT_BEGIN: typing.Final[int] = 0xfe
    # end of data for object
    _OBJECT_END: typing.Final[int] = 0xff

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

        size = cursor.read_int()
        for _ in range(size):
            value, schema = _read_object(cursor)
            assert schema, 'Object has blank schema.'
            self[schema] = value

    def write(self, cursor: Cursor):
        cursor.write(self.MAGIC_STR)
        cursor.write_long(self.FIXED_MYSTERY_NUM)
        cursor.write_int(len(self))
        for _, value in self.items():
            value.write(cursor)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{dict(self)}}}"
