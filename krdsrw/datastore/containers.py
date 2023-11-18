from __future__ import annotations
import base64
import collections
import collections.abc
import copy
import inspect
import json
import typing

from . import names
from .cursor import Cursor
from .error import FieldNotFoundError
from .error import UnexpectedDataTypeError
from .error import UnexpectedNameError
from .error import UnexpectedFieldError
from .types import Object
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


def _convert_value(o: typing.Any, cls_: type) -> typing.Any:
    if isinstance(o, dict):
        for key in list(o.keys()):
            o[key] = _convert_value(o[key], cls_)
        return o

    if isinstance(o, list):
        for i in range(len(o)):
            o[i] = _convert_value(o[i], cls_)
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


def _read_by_magic_byte(cursor: Cursor) \
-> None|Bool|Char|Byte|Short|Int|Long|Float|Double|Utf8Str|Object:
    for t in [ Bool, Byte, Char, Short, Int, Long, Float, Double, Utf8Str ]:
        if cursor._peek_raw_byte() == t.magic_byte:
            return t.create(cursor)

    if cursor._peek_raw_byte() == Object.object_begin:
        cursor._eat_raw_byte(Object.object_begin)

        name = cursor.read_utf8str(False)
        fct = names.get_maker_by_name(name)
        assert fct, f'Unsupported name \"{name}\".'
        o = fct.create(cursor)
        assert o.name == name, 'mismatched object name'
        if not cursor._eat_raw_byte(Object.object_end):
            raise UnexpectedDataTypeError(
                cursor._data.tell(), Object.object_end, cursor._peek_raw_byte())
        return o

    return None


class _TypeCheckedList(list[T]):
    def __init__(self, cls_: type[T]):
        super().__init__()
        self._cls: typing.Final[type[T]] = cls_

    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls and list(self) == list(o)
        return super().__eq__(o)

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
            o = _convert_value(o, self._cls)
            assert isinstance(o, self._cls)
            super().__setitem__(i, o)
        else:
            assert isinstance(o, collections.abc.Iterable)
            o = [_convert_value(e, self._cls) for e in o]  # type: ignore
            super().__setitem__(i, o)  # type: ignore

    def __add__(
            self, other: typing.Iterable[int | float | str | T]) -> typing.Self:
        o = self.copy()
        o.extend(_convert_value(other, self._cls))
        return o

    def __iadd__(
            self, other: typing.Iterable[int | float | str | T]) -> typing.Self:
        self.extend(_convert_value(other, self._cls))
        return self

    def append(self, o: int | float | str | T):
        super().append(_convert_value(o, self._cls))

    def insert(self, i: int, o: int | float | str | T):
        super().insert(i, _convert_value(o, self._cls))

    def copy(self) -> typing.Self:
        return copy.copy(self)

    def extend(self, other: typing.Iterable[int | float | str | T]):
        super().extend(_convert_value(other, self._cls))

    def count(self, o: typing.Any) -> int:
        return super().count(o)


class Array(_TypeCheckedList[T], Object):
    def __init__(
            self, maker: type[T] | ValueFactory[T], name: None | str = None):
        if not isinstance(maker, ValueFactory):
            maker = ValueFactory(maker)
        _TypeCheckedList.__init__(self, maker.cls_)
        Object.__init__(self, name=name)
        self._maker: typing.Final[ValueFactory[T]] = maker

    def read(self, cursor: Cursor):
        if self.name:
            self._read_header(cursor)

        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            self.append(self._maker.create(cursor))

        if self.name:
            self._read_footer(cursor)

    def write(self, cursor: Cursor):
        if self.name:
            self._write_header(cursor)

        cursor.write_int(len(self))
        for e in self:
            e.write(cursor)

        if self.name:
            self._write_footer(cursor)

    @property
    def cls_(self) -> type[T]:
        return self._maker.cls_


class _TypeCheckedDict(collections.OrderedDict[K, T]):
    def __init__(
            self, key_cls: type[K],
            val_maker: type[T] | ValueFactory[T] | dict[K, ValueFactory[T]]):
        if not isinstance(val_maker, (ValueFactory, dict)):
            val_maker = ValueFactory(val_maker)
        super().__init__()
        self._key_cls: type[K] = key_cls
        self._val_maker: ValueFactory[T] \
        | dict[K, ValueFactory[T]] \
        | typing.Callable[[K], None|ValueFactory[T]] \
        = copy.copy(val_maker)

    @property
    def key_cls(self) -> type[K]:
        return self._key_cls

    @property
    def val_cls(self) -> type[T] | dict[K, type[T]]:
        if isinstance(self._val_maker, dict):
            return { k: v.cls_ for k, v in self._val_maker.items() }
        return self._val_maker.cls_

    def _key_to_val_cls(self, key: K) -> type[T]:
        if isinstance(self._val_maker, dict):
            return self._val_maker[key].cls_
        if callable(self._val_maker):
            maker = self._val_maker(key)
            assert maker, f'no factory for \"{key}\".'
            return maker.cls_

        return self._val_maker.cls_

    def __setitem__(self, key: K, item: int | float | str | T):
        key = _convert_value(key, self._key_cls)
        item = _convert_value(item, self._key_to_val_cls(key))
        super().__setitem__(key, item)  # type: ignore

    def _is_key_allowed(self, key: K) -> bool:
        if isinstance(self._val_maker, dict):
            return key in self._val_maker
        if callable(self._val_maker):
            return bool(self._val_maker(key))
        return True

    def _make_val(self, key: K) -> T:
        if isinstance(self._val_maker, dict):
            return self._val_maker[key].create()
        if callable(self._val_maker):
            maker = self._val_maker(key)
            assert maker, f'no factory for \"{key}\".'
            return maker.create()
        return self._val_maker.create()

    @classmethod
    def fromkeys(
            cls, iterable: typing.Iterable[int | float | str],
            value: T) -> dict:
        raise NotImplementedError("Unsupported for this container")

    def setdefault(self, key: K, default: T) -> T:
        key = _convert_value(key, self._key_cls)
        default = _convert_value(default, self._key_to_val_cls(key))
        return super().setdefault(key, default)

    def update(self, *args: typing.Mapping[K, T], **kwargs: T):
        d = {}
        d.update(*args, **kwargs)

        if not all(_is_val_compatible(e, self._key_cls) for e in d.keys()):
            raise TypeError(f'Key(s) is of wrong type for this container')

        if not all(_is_val_compatible(e, self._key_to_val_cls(e))
                   for e in d.values()):
            raise TypeError(f"Value(s) is of wrong class for this container")

        for key in list(d.keys()):
            d[key] = _convert_value(d[key], self._key_to_val_cls(key))

        super().update(d)

    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return (
                o._key_cls == self._key_cls \
                and o._val_maker == self._val_maker \
                and dict(o) == dict(self)
            )
        return super().__eq__(o)

    def compute_if_absent(self, key: K) -> T:
        if self._is_key_allowed(key):
            raise KeyError(f'Key "{key}" is invalid for this container')
        if key not in self:
            self[key] = self._make_val(key)
        return self[key]


class DynamicMap(_TypeCheckedDict[str, T], Object):
    # DynamicMap contains only Basics, no Objects.

    def __init__(
        self,
        key_cls: type[str],
        val_maker: ValueFactory[T] | dict[K, ValueFactory[T]],
        name: None | str = None,
    ):
        _TypeCheckedDict.__init__(self, key_cls, val_maker)
        Object.__init__(self, name=name)

    def read(self, cursor: Cursor):
        if self.name:
            self._read_header(cursor)

        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            key = cursor.read_utf8str()
            value = _read_by_magic_byte(cursor)
            assert value, 'value not found'
            self[key] = value

        if self.name:
            self._read_footer(cursor)

    def write(self, cursor: Cursor):
        if self.name:
            self._write_header(cursor)

        cursor.write_int(len(self))
        for key, value in self.items():
            cursor.write_utf8str(key)
            value.write(cursor)

        if self.name:
            self._write_footer(cursor)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return dict(self) == dict(other)
        return super().__eq__(other)


class Record(_TypeCheckedDict[str, T], Object):
    def __init__(
        self,
        required: typing.Dict[str, ValueFactory[T]],
        optional: None | typing.Dict[str, ValueFactory[T]] = None,
        name: None | str = None,
    ):
        _TypeCheckedDict.__init__(self, str, required | (optional or {}))
        Object.__init__(self, name=name)

        self._required: typing.Final[typing.Dict[str, ValueFactory[T]]] \
            = collections.OrderedDict(required)
        self._optional: typing.Final[typing.Dict[str, ValueFactory[T]]] \
            = collections.OrderedDict(optional or {})

        for k, v in self._required.items():
            self[k] = v.create()

    @property
    def required(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._required.items() }

    @property
    def optional(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._optional.items() }

    def read(self, cursor: Cursor):
        if self.name:
            self._read_header(cursor)

        self.clear()

        for name, val_maker in self._required.items():
            if not self._read_next(cursor, name, val_maker):
                raise FieldNotFoundError(
                    'Expected field with name "%s" but was not found' % name)

        for name, val_maker in self._optional.items():
            if not self._read_next(cursor, name, val_maker):
                break

        if self.name:
            self._read_footer(cursor)

    def _read_next(
            self, cursor: Cursor, name: str,
            val_maker: ValueFactory[T]) -> bool:
        cursor.save()
        try:
            self[name] = val_maker.create(cursor)
            cursor.unsave()
            return True
        except UnexpectedDataTypeError:
            cursor.restore()
            return False

    def write(self, cursor: Cursor):
        if self.name:
            self._write_header(cursor)

        for name, val_maker in self._required.items():
            assert isinstance(self[name], val_maker.cls_)
            self[name].write(cursor)

        for name, val_maker in self._optional.items():
            value = self.get(name)
            if value is None:
                break
            assert isinstance(value, val_maker.cls_)
            value.write(cursor)

        if self.name:
            self._write_footer(cursor)

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


class SwitchMap(_TypeCheckedDict[int, Object], Object):
    def __init__(
            self, id_to_name: typing.Dict[int, str], name: None | str = None):
        id_to_maker = {
            k: names.get_maker_by_name(v)
            for k, v in id_to_name.items()
        }

        _TypeCheckedDict.__init__(self, int, self._id_to_maker)
        Object.__init__(self, name=name)

        assert all(v is not None for v in id_to_maker.values())
        self._id_to_maker: typing.Final[dict[int, ValueFactory[Object]]] \
        = id_to_maker  # type: ignore
        self._id_to_name: typing.Final[typing.Dict[int, str]] \
            = dict(id_to_name)

    def read(self, cursor: Cursor):
        if self.name:
            self._read_header(cursor)

        self.clear()

        size = cursor.read_int()
        for _ in range(size):
            id_ = cursor.read_int()
            if id_ not in self._id_to_name:
                raise UnexpectedFieldError('Unrecognized field ID "%d"' % id_)

            if not (name := cursor.peek_object_name()) \
            or self._id_to_name[id_] != name:
                raise UnexpectedFieldError(
                    f'Expected name "{self._id_to_name[id_]}" '
                    + f'but got "{name}"')

            assert id_ in self._id_to_maker, f'no factory for id "{id_}"'
            self[id_] = self._id_to_maker[id_].create(cursor)

        if self.name:
            self._read_footer(cursor)

    def write(self, cursor: Cursor):
        if self.name:
            self._write_header(cursor)

        id_to_non_null_value = {
            k: v
            for k, v in self.items()
            if v is not None
        }
        cursor.write_int(len(id_to_non_null_value))
        for id_, val in id_to_non_null_value.items():
            cursor.write_int(id_)
            val.write(cursor)

        if self.name:
            self._write_footer(cursor)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            id_to_non_null_value1 = {
                k: v
                for k, v in self.items()
                if v is not None
            }
            id_to_non_null_value2 = {
                k: v
                for k, v in other.items()
                if v is not None
            }
            return (
                self._id_to_name == other._id_to_name
                and id_to_non_null_value1 == id_to_non_null_value2
                and self._id_to_maker == other._id_to_maker)
        return super().__eq__(other)


class NameMap(_TypeCheckedDict[str, Object], Object):
    def __init__(self, name: None | str = None):
        _TypeCheckedDict.__init__(self, str, names.get_maker_by_name)
        Object.__init__(self, name=name)

    def read(self, cursor: Cursor):
        if self.name:
            self._read_header(cursor)

        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            name = cursor.peek_object_name()
            assert name, 'object must have non-blank name'
            self[name] = cursor.read_object()

        if self.name:
            self._read_footer(cursor)

    def write(self, cursor: Cursor):
        if self.name:
            self._write_header(cursor)

        cursor.write_int(len(self))
        for name, value in self.items():
            assert name == value.name, "object name mismatch"
            value.write(cursor)

        if self.name:
            self._write_footer(cursor)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return dict(self) == dict(other)
        return super().__eq__(other)


class DateTime(Object):
    def __init__(self, name: None | str = None):
        Object.__init__(self, name=name)
        self._value: int = -1  # -1 is null

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"Value must be an {int.__name__}")
        self._value = max(-1, value)

    def read(self, cursor: Cursor):
        self._value = cursor.read_long()

    def write(self, cursor: Cursor):
        cursor.write_long(max(-1, self._value))

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value
        return super().__eq__(other)


class Json(Object):
    def __init__(self, name: None | str = None):
        Object.__init__(self, name=name)
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

    def read(self, cursor: Cursor):
        s = cursor.read_utf8str()
        self._value = json.loads(s) if s is not None and s else None

    def write(self, cursor: Cursor):
        s = json.dumps(self._value) if self._value is not None else ""
        cursor.write_utf8str(s)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value
        return super().__eq__(other)


class LastPageRead(Object):  # aka LPR. this is kindle reading pos info
    EXTENDED_LPR_VERSION: typing.Final[int] = 2

    def __init__(self, name: None | str = None):
        Object.__init__(self, name=name)
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

    def __init__(self, name: None | str = None):
        Object.__init__(self, name=name)
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
    def __init__(self, name: None | str = None):
        Object.__init__(self, name=name)
        self._value: int = -1  # -1 is null

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value must be an {int.__name__}")
        self._value = value

    def read(self, cursor: Cursor):
        self._value = cursor.read_long()

    def write(self, cursor: Cursor):
        cursor.write_long(max(-1, self._value))

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value

        return super().__eq__(other)
