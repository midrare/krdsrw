from __future__ import annotations
import base64
import collections
import collections.abc
import copy
import json
import typing

from . import schemas
from .cursor import Cursor
from .error import UnexpectedBytesError
from .error import UnexpectedStructureError
from .types import Object
from .types import Spec
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


def _read_basic(cursor: Cursor) \
-> None|Bool|Char|Byte|Short|Int|Long|Float|Double|Utf8Str:
    for t in [ Bool, Byte, Char, Short, Int, Long, Float, Double, Utf8Str ]:
        if cursor._peek_raw_byte() == t.magic_byte:
            return t.create(cursor)

    return None


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
                raise TypeError(f"Value \"{o}\" is not allowed.")
            o = self._transform_write(o)
            super().__setitem__(i, o)
        else:
            assert isinstance(o, collections.abc.Iterable)
            o = list(o)  # type: ignore
            for e in o:
                if not self._is_write_allowed(e):
                    raise TypeError(f"Value \"{e}\" is not allowed.")
            o = [self._transform_write(e) for e in o]
            super().__setitem__(i, o)

    def __add__(
            self, other: typing.Iterable[int | float | str | T]) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._is_write_allowed(e):
                raise TypeError(f"Value \"{e}\" is not allowed.")
        o = self.copy()
        o.extend(self._transform_write(e) for e in other)
        return o

    def __iadd__(
            self, other: typing.Iterable[int | float | str | T]) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._is_write_allowed(e):
                raise TypeError(f"Value \"{e}\" is not allowed.")
        self.extend(self._transform_write(e) for e in other)
        return self

    def append(self, o: int | float | str | T):
        if not self._is_write_allowed(o):
            raise TypeError(f"Value \"{o}\" is not allowed.")
        super().append(self._transform_write(o))

    def insert(self, i: int, o: int | float | str | T):
        if not self._is_write_allowed(o):
            raise TypeError(f"Value \"{o}\" is not allowed.")
        super().insert(i, self._transform_write(o))

    def copy(self) -> typing.Self:
        return copy.copy(self)

    def extend(self, other: typing.Iterable[int | float | str | T]):
        other = list(other)
        for e in other:
            if not self._is_write_allowed(e):
                raise TypeError(f"Value \"{e}\" is not allowed.")
        super().extend(self._transform_write(e) for e in other)

    def count(self, o: bool | int | float | str | T) -> int:
        return super().count(o)  # type: ignore


class Array(_TypeCheckedList[T], Object):
    # Array can contain Basic and other containers
    def __init__(self, elmt_spec: Spec[T], elmt_name: None | str = None):
        super().__init__()
        self._elmt_spec: typing.Final[Spec[T]] = elmt_spec
        self._elmt_name: typing.Final[str] = elmt_name or ''

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            e = self._elmt_spec.read(cursor, self._elmt_name)
            self.append(e)

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_int(len(self))
        for e in self:
            self._elmt_spec.write(cursor, e, self._elmt_name)

    @property
    def elmt_cls(self) -> type[T]:
        return self._elmt_spec.cls_

    @property
    def elmt_name(self) -> str:
        return self._elmt_name

    @typing.override
    def _is_write_allowed(self, o: typing.Any) -> bool:
        return self._elmt_spec.is_castable(o)

    @typing.override
    def _transform_write(self, o: typing.Any) -> T:
        return self._elmt_spec.cast(o)


class _TypeCheckedDict(dict[K, T]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _is_read_allowed(self, key: typing.Any) -> bool:
        return True

    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        return True

    def _is_del_allowed(self, key: typing.Any) -> bool:
        return True

    def _transform_read(self, key: typing.Any) -> K:
        return key

    def _transform_write(self, key: typing.Any,
                         value: typing.Any) -> tuple[K, T]:
        return key, value

    def _transform_del(self, key: typing.Any) -> K:
        return key

    @classmethod
    def fromkeys(
        cls,
        iterable: typing.Iterable[bool | int | float | str],
        value: T,
    ) -> typing.Self:
        keys = list(iterable)

        def cast(key, val) -> tuple[K, T]:
            if key not in keys:
                raise TypeError(f"Key \"{key}\" is not allowed.")

            if val is None:
                val = copy.deepcopy(value)

            val = _to_ctype(val, value.__class__)
            if not isinstance(val, value.__class__):
                raise TypeError(f"Value \"{value}\" is not allowed.")

            return key, val

        o = cls(cast)
        for key in keys:
            o[key] = value  # type: ignore

        return o

    @typing.override
    def setdefault(self, key: K, default: None | T = None) -> T:
        if not self._is_write_allowed(key, default):
            raise TypeError(
                f"Write to key \"{key}\" of"
                + f" value \"{default}\" is not allowed.")

        key, default = self._transform_write(key, default)
        return super().setdefault(key, default)

    @typing.override
    def update(self, *args: typing.Mapping[K, T], **kwargs: T):
        d = dict()
        for key, value in dict(*args, **kwargs).items():
            if not self._is_write_allowed(key, value):
                raise TypeError(
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
        if not self._is_del_allowed(key):
            raise KeyError(f"Key \"{key}\" cannot be read.")
        key = self._transform_del(key)
        return super().__delitem__(key)

    def __getitem__(self, key: K) -> T:
        if not self._is_read_allowed(key):
            raise KeyError(f"Key \"{key}\" cannot be read.")

        key = self._transform_read(key)
        return super().__getitem__(key)

    def __setitem__(self, key: K, item: int | float | str | T):
        if not self._is_write_allowed(key, item):
            raise TypeError(
                f"Write to key \"{key}\" of"
                + f" value \"{item}\" is not allowed.")
        key, item = self._transform_write(key, item)
        super().__setitem__(key, item)


class Record(_TypeCheckedDict[str, T], Object):
    # Record can contain basics and other containers
    # keys are just arbitrary aliases for convenience. values are
    # hardcoded and knowing what value is where is determined by
    # the order of their appearance

    def __init__(
        self,
        required: dict[str, Spec[T]],
        optional: None | dict[str, Spec[T]] = None,
    ):
        super().__init__()

        self._required: typing.Final[dict[str, Spec[T]]] \
            = dict(required)
        self._optional: typing.Final[dict[str, Spec[T]]] \
            = dict(optional or {})

        for k, v in self._required.items():
            self[k] = v.make()

    @typing.override
    def _is_read_allowed(self, key: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        return key in self._required or key in self._optional

    @typing.override
    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        maker = self._required.get(key) or self._optional.get(key)
        if not maker or not maker.is_instance(value):
            return False
        return True

    @typing.override
    def _is_del_allowed(self, key: typing.Any) -> bool:
        return key not in self._required

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
            value = maker.make()
        return key, value

    @typing.override
    def _transform_del(self, key: typing.Any) -> str:
        return key

    @property
    def required(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._required.items() }

    @property
    def optional(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._optional.items() }

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()

        for alias, spec in self._required.items():
            val = self._read_next(cursor, spec)
            if val is None:
                raise UnexpectedStructureError(
                    f'Value for field "{alias}" but was not found')
            self[alias] = val

        for alias, spec in self._optional.items():
            val = self._read_next(cursor, spec)
            if val is None:
                break
            self[alias] = val

    def _read_next(self, cursor: Cursor, spec: Spec[T]) -> None | T:
        # objects in a Record have no OBJECT_BEGIN OBJECT_END demarcating
        # bytes. the demarcation is implied by the ordering of the elements

        cursor.save()
        try:
            val = spec.read(cursor)
            cursor.unsave()
            return val
        except UnexpectedBytesError:
            cursor.restore()
            return None

    @typing.override
    def write(self, cursor: Cursor):
        for alias, spec in self._required.items():
            assert isinstance(self[alias], spec.cls_), 'Invalid state'
            self[alias].write(cursor)

        for alias, spec in self._optional.items():
            value = self.get(alias)
            if value is None:
                break
            assert isinstance(value, spec.cls_), 'Invalid state'
            value.write(cursor)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._required == other._required
                and self._optional == other._optional
                and dict(self) \
                == dict(other)
            )
        return super().__eq__(other)

    def __str__(self) -> str:
        d = { k: v for k, v in self.items() if v is not None }
        return f"{self.__class__.__name__}{str(d)}"


class IntMap(_TypeCheckedDict[int, Bool | Char | Byte | Short | Int | Long
                              | Float | Double | Utf8Str | Object], Object):
    def __init__(self, idx_alias_name_spec: list[tuple[int, str, str, Spec]]):
        super().__init__()

        self._idx_to_spec: dict[int, Spec] = {}
        self._idx_to_name: dict[int, str] = {}
        self._idx_to_alias: dict[int, str] = {}

        for idx, alias, name, spec in idx_alias_name_spec:
            self._idx_to_alias[idx] = alias
            self._idx_to_name[idx] = name
            self._idx_to_spec[idx] = spec

        for idx, _, _, spec in idx_alias_name_spec:
            self[idx] = spec.make()

    @typing.override
    def _is_read_allowed(self, key: typing.Any) -> bool:
        return key in self._idx_to_spec \
        or key in self._idx_to_name \
        or key in self._idx_to_alias \
        or key in self._idx_to_alias.values()

    @typing.override
    def _is_del_allowed(self, key: typing.Any) -> bool:
        return False

    @typing.override
    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        if key not in self._idx_to_spec \
        and key not in self._idx_to_name \
        and key not in self._idx_to_alias \
        and key not in self._idx_to_alias.values():
            return False

        idx = self._alias_to_idx(key) if isinstance(key, str) else key
        assert idx >= 0, 'failed to find index'
        if not self._idx_to_spec[idx].is_instance(value):
            return False

        return True

    @typing.override
    def _transform_read(self, key: typing.Any) -> int | str:
        return self._alias_to_idx(key, key)

    @typing.override
    def _transform_write(
        self, key: typing.Any, value: typing.Any
    ) -> tuple[int | str, Bool | Char | Byte | Short | Int | Long | Float
               | Double | Utf8Str | Object]:
        key = self._alias_to_idx(key, key)
        return key, value

    @typing.override
    def _transform_del(self, key: typing.Any) -> int | str:
        return self._alias_to_idx(key, key)

    def _alias_to_idx(self, alias: str, default: None | int = None) -> int:
        if default is None:
            default = -1
        return next((k for k, v in self._idx_to_alias.items() if v == alias),
                    default)

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            idxnum = cursor.read_int()

            if idxnum not in self._idx_to_spec \
            and idxnum not in self._idx_to_alias:
                raise UnexpectedStructureError(
                    f"Object index number {idxnum} not recognized")
            name = self._idx_to_name[idxnum]
            self[idxnum] = self._idx_to_spec[idxnum].read(cursor, name)

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_int(len(self))

        for idx, value in self.items():
            name = self._idx_to_name[idx]
            cursor.write_int(idx)
            self._idx_to_spec[idx].write(cursor, value, name)


class DynamicMap(_TypeCheckedDict[str, Bool | Char | Byte | Short | Int | Long
                                  | Float | Double | Utf8Str], Object):
    def __init__(self):
        super().__init__()

    @typing.override
    def _is_read_allowed(self, key: typing.Any) -> bool:
        return isinstance(key, str)

    @typing.override
    def _is_write_allowed(self, key: typing.Any, value: typing.Any) -> bool:
        return isinstance(key, str) and isinstance(value, Basic)

    @typing.override
    def _is_del_allowed(self, key: typing.Any) -> bool:
        return True

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
    def _transform_del(self, key: typing.Any) -> str:
        return key

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
        for key, value in self.items():
            assert isinstance(key, str)
            cursor.write_utf8str(key)
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

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{self._value}}}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{self._value}}}"

    def __json__(self) -> None | bool | int | float | str | tuple | list | dict:
        return { "epoch_ms": self._value }


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

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{str(self._value)}}}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{str(self._value)}}}"

    def __json__(self) -> None | bool | int | float | str | tuple | list | dict:
        return self._value


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
            raise UnexpectedBytesError([Utf8Str.magic_byte, Byte.magic_byte],
                                       type_byte)

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
        d = {
            "lpr_version": self._lpr_version,
            "timestamp": self._timestamp,
            "pos": self._pos,
        }
        return f"{self.__class__.__name__}{{{str(d)}}}"

    def __repr__(self) -> str:
        d = {
            "lpr_version": self._lpr_version,
            "timestamp": self._timestamp,
            "pos": self._pos,
        }
        return f"{self.__class__.__name__}{{{str(d)}}}"

    def __json__(self) -> None | bool | int | float | str | tuple | list | dict:
        return {
            "lpr_version": max(1, self._lpr_version),
            "timestamp": self._timestamp,
            "pos": self._pos,
        }


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

    def __json__(self) -> None | bool | int | float | str | tuple | list | dict:
        return {
            "chunk_eid": self._chunk_eid,
            "chunk_pos": self._chunk_pos,
            "char_pos": self._value,
        }

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
        return f"{self.__class__.__name__}{{{str(d)}}}"

    def __repr__(self) -> str:
        d = {
            "chunk_eid": self._chunk_eid,
            "chunk_pos": self._chunk_pos,
            "char_pos": self._value,
        }
        return f"{self.__class__.__name__}{{{str(d)}}}"


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

    def __str__(self) -> str:
        d = { "offset": self._value }
        return f"{self.__class__.__name__}{{{str(d)}}}"

    def __repr__(self) -> str:
        d = { "offset": self._value }
        return f"{self.__class__.__name__}{{{str(d)}}}"

    def __json__(self) -> None | bool | int | float | str | tuple | list | dict:
        return { "offset": self._value }


class DataStore(_TypeCheckedDict[str, Bool | Char | Byte | Short | Int | Long
                                 | Float | Double | Utf8Str | Object], Object):
    MAGIC_STR: typing.Final[bytes] = b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
    FIXED_MYSTERY_NUM: typing.Final[int] = (
        1  # present after the signature; unknown what this number means
    )

    # named object data structure (name utf8str + data)
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
            value, name = self._read_object(cursor)
            assert name, 'Object has blank name.'
            self[name] = value

    def write(self, cursor: Cursor):
        cursor.write(self.MAGIC_STR)
        cursor.write_long(self.FIXED_MYSTERY_NUM)
        cursor.write_int(len(self))
        for name, value in self.items():
            self._write_object(cursor, name, value)

    @classmethod
    def _read_object(
        cls, cursor: Cursor
    ) -> tuple[Bool | Char | Byte | Short | Int | Long | Float
               | Double | Utf8Str | Object, None | str]:
        if not cursor.eat(cls._OBJECT_BEGIN):
            raise UnexpectedBytesError(
                cursor.tell(), cls._OBJECT_BEGIN, cursor.peek())

        name = cursor.read_utf8str(False)
        if not name:
            raise UnexpectedStructureError('Failed to read name for object.')

        maker = schemas.get_spec_by_name(name)
        assert maker, f"Unsupported spec name \"{name}\"."
        value = maker.read(cursor)

        if not cursor.eat(cls._OBJECT_END):
            raise UnexpectedBytesError(
                cursor.tell(), cls._OBJECT_END, cursor.peek())

        return value, name

    @classmethod
    def _write_object(
        cls,
        cursor: Cursor,
        name: str,
        value: Object,
    ) -> tuple[Bool | Char | Byte | Short | Int | Long | Float
               | Double | Utf8Str | Object, None | str]:
        cursor.write(cls._OBJECT_BEGIN)
        cursor.write_utf8str(name, False)
        value.write(cursor)
        cursor.write(cls._OBJECT_END)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{dict(self)}}}"


ALL_OBJECT_TYPES: typing.Final[tuple[type[Object], ...]] = (
    Array,
    Record,
    IntMap,
    DynamicMap,
    DateTime,
    Json,
    LastPageRead,
    Position,
    TimeZoneOffset,
    DataStore,
)
