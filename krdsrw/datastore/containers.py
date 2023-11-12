from __future__ import annotations
import base64
import collections
import copy
import json
import typing

from . import keys
from . import names
from .constants import UTF8STR_TYPE_INDICATOR
from .constants import BYTE_TYPE_INDICATOR
from .cursor import Cursor
from .error import *
from .types import ALL_BASIC_TYPES
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
from .value import Value

T = typing.TypeVar(
    "T",
    bound=Byte | Char | Bool | Short
    | Int | Long | Float | Double | Utf8Str | Value
)
K = typing.TypeVar("K", int, str)
V = typing.TypeVar(
    "V",
    bound=Byte | Char | Bool | Short
    | Int | Long | Float | Double | Utf8Str | Value
)


class ValFactory(typing.Generic[T]):
    def __init__(self, cls_: type[T], *args, **kwargs):
        super().__init__()

        if not any(issubclass(cls_, c) for c in ALL_BASIC_TYPES) \
        and issubclass(cls_, Value):
            raise TypeError(f"Unsupported type \"{type(cls_).__name__}\".")

        self._cls: typing.Final[type[T]] = cls_
        self._args: typing.Final[list] = list(args)
        self._kwargs: typing.Final[dict] = collections.OrderedDict(kwargs)
        self._is_primitive: typing.Final[bool] = any(
            issubclass(cls_, c) for c in ALL_BASIC_TYPES
        )

    @property
    def cls_(self) -> type[T]:
        return self._cls

    def create(self) -> T:
        return self._cls(*self._args, **self._kwargs)

    def create_from(self, cursor: Cursor) -> T:
        if self._is_primitive:
            return cursor.read_auto(self._cls)  # type: ignore

        val = self._cls(*self._args, **self._kwargs)
        assert (isinstance(val, Value))
        val.read(cursor)
        return val

    def is_cls_primitive(self) -> bool:
        return self._is_primitive

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls and self._args == o._args \
            and self._kwargs == o._kwargs
        return super().__eq__(o)


def _write_value(
    cursor: Cursor,
    value: Byte | Char | Bool | Short
    | Int | Long | Float | Double | Utf8Str | Value
):
    if any(isinstance(value, c) for c in ALL_BASIC_TYPES):
        cursor.write_auto(value)  # type: ignore
    else:
        value.write(cursor)  # type: ignore


# WIP
NameMap = dict
NamedValue = dict
DateTime = int
FixedMap = dict
Json = object
LastPageRead = int
Position = int
SwitchMap = dict
TimeZoneOffset = int


class _CheckedList(list[T]):
    def __init__(self, cls_: type[T]):
        super().__init__()
        self._cls: typing.Final[type[T]] = cls_

    def _is_instance(self, o: typing.Any) -> bool:
        if issubclass(self._cls, Basic) and isinstance(o, self._cls.builtin):
            return True

        return isinstance(o, self._cls)

    def _convert(self, o: int | float | str | T) -> T:
        if issubclass(self._cls, Basic) and isinstance(o, self._cls.builtin):
            return self._cls(o)
        if not isinstance(o, (Basic, Value)):
            raise TypeError(f"Unexpected type \"{type(o).__name__}\".")
        return o

    def _convert_list(self,
        o: typing.Iterable[int | float | str | T]) -> list[T]:
        return [self._convert(e) for e in o]

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls and list(self) == list(o)
        return super().__eq__(o)

    def __contains__(self, o: int | float | str | T) -> bool:
        if not self._is_instance(o):
            raise TypeError(f"Value is of wrong class for this container")
        o = self._convert(o)
        return super().__contains__(o)

    def __setitem__(self, i: int, o: int | float | str | T):
        if not self._is_instance(o):
            raise TypeError(f"Value is of wrong class for this container")
        if isinstance(o, (int, float, str)):
            o = self._cls(o)
        super().__setitem__(i, o)

    def __add__(
        self, other: typing.Iterable[int | float | str | T]
    ) -> typing.Self:
        lst = self._convert_list(other)
        assert all(self._is_instance(e) for e in lst)
        o = self.copy()
        o.extend(lst)
        return o

    def __iadd__(
        self, other: typing.Iterable[int | float | str | T]
    ) -> typing.Self:
        lst = self._convert_list(other)
        assert all(self._is_instance(e) for e in lst)
        self.extend(self._convert_list(lst))
        return self

    def append(self, o: int | float | str | T):
        if not self._is_instance(o):
            raise TypeError(f"Value is of wrong class for this container")
        super().append(self._convert(o))

    def insert(self, i: int, o: int | float | str | T):
        if not self._is_instance(o):
            raise TypeError(f"Value is of wrong class for this container")
        super().insert(i, self._convert(o))

    def remove(self, o: int | float | str | T):
        if not self._is_instance(o):
            raise TypeError(f"Value is of wrong class for this container")
        o = self._convert(o)
        super().remove(o)

    def copy(self) -> typing.Self:
        return copy.copy(self)

    def count(self, o: int | float | str | T) -> int:
        if not self._is_instance(o):
            raise TypeError(f"Value is of wrong class for this container")
        o = self._convert(o)
        return super().count(o)

    def index(self, o: int | float | str | T, *args: typing.Any) -> int:
        o = self._convert(o)
        assert self._is_instance(o)
        return super().index(o, *args)

    def extend(self, other: typing.Iterable[int | float | str | T]):
        lst = self._convert_list(other)
        assert all(self._is_instance(e) for e in lst)
        super().extend(lst)


class Array(_CheckedList[T], Value):
    def __init__(self, maker: ValFactory[T]):
        _CheckedList.__init__(self, maker.cls_)
        Value.__init__(self)
        self._maker: typing.Final[ValFactory[T]] = maker

    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            self.append(self._maker.create_from(cursor))

    def write(self, cursor: Cursor):
        cursor.write_int(len(self))
        for e in self:
            _write_value(cursor, e)

    @property
    def cls_(self) -> type[T]:
        return self._maker.cls_


class _CheckedDict(dict[K, V]):
    def __init__(
        self,
        key_cls: type[K],
        val_maker: ValFactory[V] | dict[K, ValFactory[V]]
    ):
        super().__init__()
        self._key_cls: type[K] = key_cls
        self._val_maker: ValFactory[V] | dict[K,
            ValFactory[V]] = copy.deepcopy(val_maker)

    @property
    def key_cls(self) -> type[K]:
        return self._key_cls

    def val_cls(self, key: K) -> type[V]:
        if isinstance(self._val_maker, dict):
            return self._val_maker[key].cls_
        return self._val_maker.cls_

    def __contains__(self, key: K) -> bool:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().__contains__(key)

    def __getitem__(self, key: K) -> V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().__getitem__(key)

    def __setitem__(self, key: K, item: V):
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        if not isinstance(item, self._key_to_val_cls(key)):
            raise TypeError(
                f'Value of class "{item.__class__.__name__}"'
                + ' is of invalid class for this container'
            )
        super().__setitem__(key, item)

    def __delitem__(self, key: K) -> None:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        super().__delitem__(key)

    def _is_key_valid(self, key: K) -> bool:
        if isinstance(self._val_maker, dict):
            return key in self._val_maker
        return True

    def _key_to_val_cls(self, key: K) -> type[V]:
        if isinstance(self._val_maker, dict):
            return self._val_maker[key].cls_
        return self._val_maker.cls_

    def _create(self, key: K) -> V:
        if isinstance(self._val_maker, dict):
            return self._val_maker[key].create()
        return self._val_maker.create()

    def copy(self) -> typing.Self:
        return copy.deepcopy(self)

    @classmethod
    def fromkeys(cls,
        iterable: typing.Iterable[K],
        value: None | V = None) -> _CheckedDict[K, V]:
        raise NotImplementedError("Unsupported for this container")

    def pop(self, key: K) -> V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().pop(key)

    def popitem(self) -> typing.Tuple[K, V]:
        return super().popitem()

    def setdefault(self, key: K, default: None | V) -> V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        if not isinstance(default, self._key_to_val_cls(key)):
            raise TypeError(f"Value is of wrong class for this container")

        return super().setdefault(key, default)

    def update(self, m: typing.Mapping[K, V], **kwargs: V):
        d = dict(m) | kwargs
        for k, v in d.items():
            if not isinstance(k, self._key_cls):
                raise KeyError(
                    f'Key "{k}" is not of class {self._key_cls.__name__}'
                )
            if not isinstance(v, self._key_to_val_cls(k)):
                raise TypeError(f"A value is of wrong class for this container")

        super().update(m, **kwargs)

    def get(self, key: K) -> None | V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().get(key)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return (
                o._key_cls == self._key_cls and o._val_maker == self._val_maker
                and dict(o) == dict(self)
            )
        return super().__eq__(o)

    def compute_if_absent(self, key: K) -> V:
        if self._is_key_valid(key):
            raise KeyError(f'Key "{key}" is invalid for this container')
        if key not in self:
            self[key] = self._create(key)
        return self[key]


class DynamicMap(_CheckedDict[str,
    Byte | Char | Bool | Short | Int | Long | Float | Double | Utf8Str | Value],
    Value):
    def __init__(
        self,
        key_cls: type[str],
        val_maker: ValFactory[V] | dict[K, ValFactory[V]],
    ):
        _CheckedDict.__init__(self, key_cls, val_maker)
        Value.__init__(self)

    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            name = cursor.read_utf8str()
            value = cursor.read_auto()
            self[name] = value

    def write(self, cursor: Cursor):
        cursor.write_int(len(self))
        for key, value in self.items():
            cursor.write_utf8str(key)
            _write_value(cursor, value)

    def __eq__(self, other: Value) -> bool:
        if isinstance(other, self.__class__):
            return dict(self) == dict(other)
        return super().__eq__(other)


# class FixedMap(_CheckedDict[str, V], Value):
#     def __init__(
#         self,
#         required: typing.Dict[str, ValFactory[V]],
#         optional: None | typing.Dict[str, ValFactory[V]] = None,
#     ):
#         _CheckedDict.__init__(self, str, required | (optional or {}))
#         Value.__init__(self)

#         self._required: typing.Final[typing.Dict[str, ValFactory[V]]] \
#             = collections.OrderedDict(required)
#         self._optional: typing.Final[typing.Dict[str, ValFactory[V]]] \
#             = collections.OrderedDict(optional or {})

#         for k, v in self._required.items():
#             self[k] = v.create()

#     @property
#     def required(self) -> typing.Tuple[str, ...]:
#         return tuple((self._required).keys())

#     @property
#     def optional(self) -> typing.Tuple[str, ...]:
#         return tuple((self._optional).keys())

#     def read(self, cursor: Cursor):
#         self.clear()

#         for name, val_maker in self._required.items():
#             if not self._read_next(cursor, name, val_maker):
#                 raise FieldNotFoundError(
#                     'Expected field with name "%s" but was not found' % name
#                 )

#         for name, val_maker in self._optional.items():
#             if not self._read_next(cursor, name, val_maker):
#                 break

#     def _read_next(
#         self, cursor: Cursor, name: str, val_maker: ValFactory[V]
#     ) -> bool:
#         cursor.save()
#         try:
#             self[name] = val_maker.create_from(cursor)
#             cursor.unsave()
#             return True
#         except UnexpectedDataTypeError:
#             cursor.restore()
#             return False

#     def write(self, cursor: Cursor):
#         for name, val_maker in self._required.items():
#             value = self[name]
#             assert isinstance(value, val_maker.cls_)
#             _write_value(cursor, value)

#         for name, val_maker in self._optional.items():
#             value = self.get(name)
#             if value is None:
#                 break
#             assert isinstance(value, val_maker.cls_)
#             _write_value(cursor, value)

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             return (
#                 self._required == other._required
#                 and self._optional == other._optional
#                 and dict(self) == dict(other)
#             )
#         return super().__eq__(other)

#     def __str__(self) -> str:
#         d = { k: v for k, v in self.items() if v is not None }
#         return f"{self.__class__.__name__}{str(d)}"

# class NamedValue(Value, typing.Generic[T]):
#     DEMARCATION_BEGIN: typing.Final[int] = 254
#     DEMARCATION_END: typing.Final[int] = 255

#     def __init__(self, name: str):
#         super().__init__()
#         self._name: str = name
#         self._maker: ValFactory[T] = NAME_TO_FACTORY[name]
#         self._value: T = self._maker.create()

#     @property
#     def name(self) -> str:
#         return self._name

#     @property
#     def cls_(self) -> type[T]:
#         return self._maker.cls_

#     @property
#     def value(self) -> T:
#         return self._value

#     @value.setter
#     def value(self, o: T):
#         if not isinstance(o, self._maker.cls_):
#             raise TypeError(f"Value is not a {self._maker.cls_.__name__}")
#         self._value = o

#     @staticmethod
#     def peek_name(cursor: Cursor) -> None | str:
#         name = None
#         cursor.save()
#         ch = cursor.read()
#         if ch == NamedValue.DEMARCATION_BEGIN:
#             name = cursor.read_utf8str(False)
#         cursor.restore()
#         return name

#     @staticmethod
#     def peek_value_cls(cursor: Cursor) -> None | type:
#         cls_ = None
#         cursor.save()
#         ch = cursor.read()
#         if ch == NamedValue.DEMARCATION_BEGIN:
#             name = cursor.read_utf8str(False)
#             template = NAME_TO_FACTORY[name]
#             cls_ = template.cls_
#         cursor.restore()
#         return cls_

#     def read(self, cursor: Cursor):
#         if not cursor.eat(NamedValue.DEMARCATION_BEGIN):
#             raise DemarcationError(
#                 f"Starting demarcation not found @{cursor.tell()}"
#             )

#         name = cursor.read_utf8str(False)
#         if name != self._name:
#             raise UnexpectedNameError(
#                 f'Expected named value "{self._name}" but got "{name}"'
#             )

#         value = self._maker.create_from(cursor)

#         if not cursor.eat(NamedValue.DEMARCATION_END):
#             raise DemarcationError(
#                 "Ending demarcation not found @%d" % cursor.tell()
#             )

#         self._value = value

#     def write(self, cursor: Cursor):
#         cursor.write(NamedValue.DEMARCATION_BEGIN)
#         cursor.write_utf8str(self._name, False)
#         _write_value(cursor, self._value)
#         cursor.write(NamedValue.DEMARCATION_END)

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             return (
#                 self._name == other._name and self._maker == other._maker
#                 and self._value == other._value
#             )
#         return super().__eq__(other)

#     def __str__(self) -> str:
#         return f"{self.__class__.__name__}{{{self._name}: " \
#             + f"{self._maker.cls_.__name__}}}"

# class SwitchMap(_CheckedDict[int, NamedValue], Value):
#     def __init__(self, id_to_name: typing.Dict[int, str]):
#         self._id_to_maker: \
#         typing.Final[typing.Dict[int, ValFactory[NamedValue]]] \
#             = { k: NAME_TO_FACTORY[v] for k, v in id_to_name.items() }

#         _CheckedDict.__init__(self, int, self._id_to_maker)
#         Value.__init__(self)

#         self._id_to_name: typing.Final[typing.Dict[int, str]] \
#             = dict(id_to_name)
#         self._name_to_id: typing.Final[typing.Dict[str, int]] \
#             = { v: k for k, v in id_to_name.items() }

#     def _make_value(self, key: int) -> NamedValue:
#         return self._id_to_maker[key].create()

#     def read(self, cursor: Cursor):
#         self.clear()

#         size = cursor.read_int()
#         for _ in range(size):
#             field_id = cursor.read_int()
#             if field_id not in self._id_to_name:
#                 raise UnexpectedFieldError(
#                     'Unrecognized field ID "%d"' % field_id
#                 )

#             name = NamedValue.peek_name(cursor)
#             if self._id_to_name[field_id] != name:
#                 raise UnexpectedFieldError(
#                     'Expected name "%s" but got "%s"' %
#                     (name, self._id_to_name[field_id])
#                 )

#             self[field_id] = self._id_to_maker[field_id].create_from(cursor)

#     def write(self, cursor: Cursor):
#         id_to_non_null_value = {
#             k: v
#             for k, v in self.items()
#             if v is not None
#         }
#         cursor.write_int(len(id_to_non_null_value))
#         for field_id, field_value in id_to_non_null_value.items():
#             cursor.write_int(field_id)
#             _write_value(cursor, field_value)

#     def __eq__(self, other: typing.Any) -> bool:
#         if isinstance(other, self.__class__):
#             id_to_non_null_value1 = {
#                 k: v
#                 for k, v in self.items()
#                 if v is not None
#             }
#             id_to_non_null_value2 = {
#                 k: v
#                 for k, v in other.items()
#                 if v is not None
#             }
#             return (
#                 self._id_to_name == other._id_to_name
#                 and id_to_non_null_value1 == id_to_non_null_value2
#                 and self._id_to_maker == other._id_to_maker
#             )
#         return super().__eq__(other)

#     def names(self) -> typing.List[str]:
#         return list(self._name_to_id.keys())

#     def ids(self) -> typing.List[int]:
#         return list(self._id_to_name.keys())

#     def name_to_id(self, name: str) -> None | int:
#         return self._name_to_id.get(name)

#     def id_to_name(self, id: int) -> None | str:
#         return self._id_to_name.get(id)

# class NameMap(_CheckedDict[str, NamedValue], Value):
#     def __init__(self):
#         _CheckedDict.__init__(
#             self,
#             str,
#             {
#             name: ValFactory(NamedValue, name)
#             for name in NAME_TO_FACTORY.keys()
#             }
#         )
#         Value.__init__(self)

#     def read(self, cursor: Cursor):
#         self.clear()
#         size = cursor.read_int()
#         for _ in range(size):
#             name = NamedValue.peek_name(cursor)
#             assert name
#             value = NamedValue(name)
#             value.read(cursor)
#             self[name] = value

#     def write(self, cursor: Cursor):
#         cursor.write_int(len(self))
#         for name, value in self.items():
#             assert name == value.name, "name mismatch"
#             value.write(cursor)

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             return dict(self) == dict(other)
#         return super().__eq__(other)

#     @staticmethod
#     def _make_value(name: str) -> NamedValue:
#         return NamedValue(name)

# class DateTime(Value):
#     def __init__(self):
#         self._value: None | int = -1  # -1 is null

#     @property
#     def value(self) -> None | int:
#         return self._value

#     @value.setter
#     def value(self, value: None | int):
#         if value is not None and not isinstance(value, int):
#             raise TypeError(f"Value is not of class {int.__name__}")
#         self._value = value

#     def read(self, cursor: Cursor):
#         self._value = cursor.read_long()

#     def write(self, cursor: Cursor):
#         cursor.write_long(
#             self._value if self._value is not None and self._value >= 0 else -1
#         )

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             o1 = (
#                 self._value
#                 if self._value is not None and self._value >= 0 else -1
#             )
#             o2 = (
#                 other._value
#                 if other._value is not None and other._value >= 0 else -1
#             )
#             return o1 == o2
#         return super().__eq__(other)

# class Json(Value):
#     def __init__(self):
#         self._value: None | bool | int | float | str | list | dict = None

#     @property
#     def value(self) -> None | bool | int | float | str | list | dict:
#         return self._value

#     @value.setter
#     def value(self, value: None | bool | int | float | str | list | dict):
#         if value is not None and not isinstance(value,
#             (bool | int | float | str | list | dict)):
#             class_names = [
#                 c.__name__ for c in [bool | int | float | str | list | dict]
#             ]
#             raise TypeError(
#                 f"value is not any of types {', '.join(class_names)}"
#             )
#         self._value = value

#     def read(self, cursor: Cursor):
#         s = cursor.read_utf8str()
#         self._value = json.loads(s) if s is not None and s else None

#     def write(self, cursor: Cursor):
#         s = json.dumps(self._value) if self._value is not None else ""
#         cursor.write_utf8str(s)

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             return self._value == other._value
#         return super().__eq__(other)

# class LastPageRead(Value):  # also known as LPR. LPR is kindle position info
#     EXTENDED_LPR_VERSION: int = 2

#     def __init__(self):
#         super().__init__()
#         self._pos: Position = Position()
#         self._timestamp: int = -1
#         self._lpr_version: int = -1

#     @property
#     def pos(self) -> Position:
#         return self._pos

#     @property
#     def lpr_version(self) -> None | int:
#         return self._lpr_version

#     @lpr_version.setter
#     def lpr_version(self, value: None | int):
#         if value is not None and not isinstance(value, int):
#             raise TypeError(f"value is not of type {int.__name__}")
#         self._lpr_version = value

#     @property
#     def timestamp(self) -> int:
#         return self._timestamp

#     @timestamp.setter
#     def timestamp(self, value: int):
#         if value is not None and not isinstance(value, int):
#             raise TypeError(f"value is not of type {int.__name__}")
#         self._timestamp = value

#     def read(self, cursor: Cursor):
#         self._pos.value = None
#         self._pos.prefix = None
#         self._timestamp = -1
#         self._lpr_version = -1

#         type_byte = cursor.peek()
#         if type_byte == UTF8STR_TYPE_INDICATOR:
#             # old LPR version'
#             self._pos.read(cursor)
#         elif type_byte == BYTE_TYPE_INDICATOR:
#             # new LPR version
#             self._lpr_version = cursor.read_byte()
#             self._pos.read(cursor)
#             self._timestamp = int(cursor.read_long())
#         else:
#             raise UnexpectedFieldError(
#                 "Expected Utf8Str or byte but got %d" % type_byte
#             )

#     def write(self, cursor: Cursor):
#         # XXX may cause problems if kindle expects the original LPR format
#         #   version when datastore file is re-written
#         if self._timestamp is None or self._timestamp < 0:
#             # old LPR version
#             self._pos.write(cursor)
#         else:
#             # new LPR version
#             lpr_version = max(self.EXTENDED_LPR_VERSION, self._lpr_version)
#             cursor.write_byte(lpr_version)
#             self._pos.write(cursor)
#             cursor.write_long(self._timestamp)

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             return (
#                 self._pos == other._pos and self._timestamp == other.timestamp
#                 and self._lpr_version == other._lpr_version
#             )
#         return super().__eq__(other)

#     def __str__(self) -> str:
#         return (
#             self.__class__.__name__ + ":" + str({
#             "lpr_version": self._lpr_version,
#             "timestamp": self._timestamp,
#             "pos": self._pos,
#             })
#         )

# class Position(Value):
#     PREFIX_VERSION1: int = 0x01

#     def __init__(self):
#         self._chunk_eid: None | int = -1
#         self._chunk_pos: None | int = -1
#         self._value: None | int = -1

#     @property
#     def chunk_eid(self) -> None | int:
#         return self._chunk_eid

#     @chunk_eid.setter
#     def chunk_eid(self, value: None | int):
#         if value is not None and not isinstance(value, int):
#             raise TypeError(f"value is not of type {int.__name__}")
#         self._chunk_eid = value

#     @property
#     def chunk_pos(self) -> None | int:
#         return self._chunk_pos

#     @chunk_pos.setter
#     def chunk_pos(self, value: None | int):
#         if value is not None and not isinstance(value, int):
#             raise TypeError(f"value is not of type {int.__name__}")
#         self._chunk_pos = value

#     @property
#     def value(self) -> None | int:
#         return self._value

#     @value.setter
#     def value(self, value: None | int):
#         if value is not None and not isinstance(value, int):
#             raise TypeError(f"value is not of type {int.__name__}")
#         self._value = value

#     def read(self, cursor: Cursor):
#         s = cursor.read_utf8str()
#         split = s.split(":", 2)
#         if len(split) > 1:
#             b = base64.b64decode(split[0])
#             version = b[0]
#             if version == self.PREFIX_VERSION1:
#                 self._chunk_eid = int.from_bytes(b[1:5], "little")
#                 self._chunk_pos = int.from_bytes(b[5:9], "little")
#             else:
#                 # TODO throw a proper exception
#                 raise Exception(
#                     "Unrecognized position version 0x%02x" % version
#                 )
#             self._value = int(split[1])
#         else:
#             self._value = int(s)

#     def write(self, cursor: Cursor):
#         s = ""
#         if (self._chunk_eid is not None and self._chunk_eid >= 0
#                 and self._chunk_pos is not None and self._chunk_pos >= 0):
#             b_version = self.PREFIX_VERSION1.to_bytes(1, "little", signed=False)
#             b_eid = self._chunk_eid.to_bytes(4, "little", signed=False)
#             b_pos = self._chunk_pos.to_bytes(4, "little", signed=False)
#             s += base64.b64encode(b_version + b_eid + b_pos).decode("ascii")
#             s += ":"
#         s += str(
#             self._value if self._value is not None and self._value >= 0 else -1
#         )
#         cursor.write_utf8str(s)

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             val1 = (
#                 self._value
#                 if self._value is not None and self._value >= 0 else -1
#             )
#             val2 = (
#                 other._value
#                 if other._value is not None and other._value >= 0 else -1
#             )
#             eid1 = (
#                 self._chunk_eid if self._chunk_eid is not None
#                 and self._chunk_eid >= 0 else None
#             )
#             eid2 = (
#                 other._chunk_eid if other._chunk_eid is not None
#                 and other._chunk_eid >= 0 else None
#             )
#             pos1 = (
#                 self._chunk_pos if self._chunk_pos is not None
#                 and self._chunk_pos >= 0 else None
#             )
#             pos2 = (
#                 other._chunk_pos if other._chunk_pos is not None
#                 and other._chunk_pos >= 0 else None
#             )
#             return val1 == val2 and eid1 == eid2 and pos1 == pos2
#         return super().__eq__(other)

#     def __str__(self) -> str:
#         d = {
#             "chunk_eid": self._chunk_eid,
#             "chunk_pos": self._chunk_pos,
#             "char_pos": self._value,
#         }
#         d = {
#             k: v
#             for k,
#             v in d.items()
#             if v is not None and not (isinstance(v, int) or v >= 0)
#         }
#         return f"{self.__class__.__name__}{str(d)}"

# class TimeZoneOffset(Value):
#     def __init__(self):
#         self._value: None | int = None  # -1 is null

#     @property
#     def value(self) -> None | int:
#         return self._value

#     @value.setter
#     def value(self, value: None | int):
#         if value is not None and not isinstance(value, int):
#             raise TypeError(f"value is not of type {int.__name__}")
#         self._value = value

#     def read(self, cursor: Cursor):
#         self._value = cursor.read_long()

#     def write(self, cursor: Cursor):
#         cursor.write_long(
#             self._value if self._value is not None and self._value >= 0 else -1
#         )

#     def __eq__(self, other: Value) -> bool:
#         if isinstance(other, self.__class__):
#             v1 = (
#                 self._value
#                 if self._value is not None and self._value >= 0 else -1
#             )
#             v2 = (
#                 other._value
#                 if other._value is not None and other._value >= 0 else -1
#             )
#             return v1 == v2

#         return super().__eq__(other)

# # basics
# BYTE_FACTORY: typing.Final[ValFactory[Byte]] = ValFactory(Byte)
# CHAR_FACTORY: typing.Final[ValFactory[Char]] = ValFactory(Char)
# BOOL_FACTORY: typing.Final[ValFactory[Bool]] = ValFactory(Bool)
# SHORT_FACTORY: typing.Final[ValFactory[Short]] = ValFactory(Short)
# INT_FACTORY: typing.Final[ValFactory[Int]] = ValFactory(Int)
# LONG_FACTORY: typing.Final[ValFactory[Long]] = ValFactory(Long)
# FLOAT_FACTORY: typing.Final[ValFactory[Float]] = ValFactory(Float)
# DOUBLE_FACTORY: typing.Final[ValFactory[Double]] = ValFactory(Double)
# UTF8STR_FACTORY: typing.Final[ValFactory[Utf8Str]] = ValFactory(Utf8Str)

# # composites
# JSON_FACTORY: typing.Final[ValFactory[Json]] = ValFactory(Json)
# POSITION_FACTORY: typing.Final[ValFactory[Position]] = ValFactory(Position)
# DATETIME_FACTORY: typing.Final[ValFactory[DateTime]] = ValFactory(DateTime)
# LAST_PAGE_READ_FACTORY: typing.Final[ValFactory[LastPageRead]
#                                      ] = ValFactory(LastPageRead)
# DYNAMIC_MAP_FACTORY: typing.Final[ValFactory[DynamicMap]
#                                   ] = ValFactory(DynamicMap)
# TIMEZONE_OFFSET_FACTORY: typing.Final[ValFactory[TimeZoneOffset]
#                                       ] = ValFactory(TimeZoneOffset)

# ARRAY_BYTE_FACTORY: typing.Final[ValFactory[Array[Byte]]
#                                  ] = ValFactory(Array, BYTE_FACTORY)
# ARRAY_CHAR_FACTORY: typing.Final[ValFactory[Array[Char]]
#                                  ] = ValFactory(Array, CHAR_FACTORY)
# ARRAY_BOOL_FACTORY: typing.Final[ValFactory[Array[Bool]]
#                                  ] = ValFactory(Array, BOOL_FACTORY)
# ARRAY_SHORT_FACTORY: typing.Final[ValFactory[Array[Short]]
#                                   ] = ValFactory(Array, SHORT_FACTORY)
# ARRAY_INT_FACTORY: typing.Final[ValFactory[Array[Int]]
#                                 ] = ValFactory(Array, INT_FACTORY)
# ARRAY_LONG_FACTORY: typing.Final[ValFactory[Array[Long]]
#                                  ] = ValFactory(Array, LONG_FACTORY)
# ARRAY_FLOAT_FACTORY: typing.Final[ValFactory[Array[Float]]
#                                   ] = ValFactory(Array, FLOAT_FACTORY)
# ARRAY_DOUBLE_FACTORY: typing.Final[ValFactory[Array[Double]]
#                                    ] = ValFactory(Array, DOUBLE_FACTORY)
# ARRAY_UTF8STR_FACTORY: typing.Final[ValFactory[Array[Utf8Str]]
#                                     ] = ValFactory(Array, UTF8STR_FACTORY)

# # timer.average.calculator.distribution.normal
# TIMER_AVERAGE_CALCULATOR_DISTRIBUTION_NORMAL_FACTORY: typing.Final[
#     ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.TIMER_AVG_DISTRIBUTION_COUNT: LONG_FACTORY,
#     keys.TIMER_AVG_DISTRIBUTION_SUM: DOUBLE_FACTORY,
#     keys.TIMER_AVG_DISTRIBUTION_SUM_OF_SQUARES: DOUBLE_FACTORY,
#     },
#     )

# # timer.average.calculator.outliers
# TIMER_AVERAGE_CALCULATOR_OUTLIERS_FACTORY: typing.Final[
#     ValFactory[Array]] = ValFactory(Array, DOUBLE_FACTORY)

# # timer.average.calculator
# TIMER_AVERAGE_CALCULATOR_FACTORY: typing.Final[ValFactory[FixedMap]
#                                                ] = ValFactory(
#     FixedMap,
#     {
#     keys.TIMER_AVG_SAMPLES_1:
#     ARRAY_DOUBLE_FACTORY,
#     keys.TIMER_AVG_SAMPLES_2:
#     ARRAY_DOUBLE_FACTORY,
#     keys.TIMER_AVG_NORMAL_DISTRIBUTIONS:
#     ValFactory(Array, TIMER_AVERAGE_CALCULATOR_DISTRIBUTION_NORMAL_FACTORY),
#     keys.TIMER_AVG_OUTLIERS:
#     ValFactory(Array, TIMER_AVERAGE_CALCULATOR_OUTLIERS_FACTORY),
#     },
#                                                )

# # timer.model
# TIMER_MODEL_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.TIMER_VERSION: LONG_FACTORY,
#     keys.TIMER_TOTAL_TIME: LONG_FACTORY,
#     keys.TIMER_TOTAL_WORDS: LONG_FACTORY,
#     keys.TIMER_TOTAL_PERCENT: DOUBLE_FACTORY,
#     keys.TIMER_AVERAGE_CALCULATOR: TIMER_AVERAGE_CALCULATOR_FACTORY,
#     },
# )

# # timer.data.store
# TIMER_DATA_STORE_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.TIMERV1_STORE_ON: BOOL_FACTORY,
#     keys.TIMERV1_STORE_READING_TIMER_MODEL: TIMER_MODEL_FACTORY,
#     keys.TIMERV1_STORE_VERSION: INT_FACTORY,
#     },
# )

# # page.history.record
# PAGE_HISTORY_RECORD_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.PAGE_HISTORY_POS: POSITION_FACTORY,
#     keys.PAGE_HISTORY_TIME: DATETIME_FACTORY,
#     },
# )

# # font.prefs
# FONT_PREFS_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.FONT_PREFS_TYPEFACE: UTF8STR_FACTORY,
#     keys.FONT_PREFS_LINE_SP: INT_FACTORY,
#     keys.FONT_PREFS_SIZE: INT_FACTORY,
#     keys.FONT_PREFS_ALIGN: INT_FACTORY,
#     keys.FONT_PREFS_INSET_TOP: INT_FACTORY,
#     keys.FONT_PREFS_INSET_LEFT: INT_FACTORY,
#     keys.FONT_PREFS_INSET_BOTTOM: INT_FACTORY,
#     keys.FONT_PREFS_INSET_RIGHT: INT_FACTORY,
#     keys.FONT_PREFS_UNKNOWN_1: INT_FACTORY,
#     },
#     {
#     keys.FONT_PREFS_BOLD: INT_FACTORY,
#     keys.FONT_PREFS_USER_SIDELOADABLE_FONT: UTF8STR_FACTORY,
#     keys.FONT_PREFS_CUSTOM_FONT_INDEX: INT_FACTORY,
#     keys.FONT_PREFS_MOBI_7_SYSTEM_FONT: UTF8STR_FACTORY,
#     keys.FONT_PREFS_MOBI_7_RESTORE_FONT: BOOL_FACTORY,
#     keys.FONT_PREFS_READING_PRESET_SELECTED: UTF8STR_FACTORY,
#     },
# )

# # fpr
# FPR_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.FPR_POS: POSITION_FACTORY,
#     },
#     {
#     keys.FPR_TIMESTAMP: DATETIME_FACTORY,
#     keys.FPR_TIMEZONE_OFFSET: TIMEZONE_OFFSET_FACTORY,
#     keys.FPR_COUNTRY: UTF8STR_FACTORY,
#     keys.FPR_DEVICE: UTF8STR_FACTORY,
#     },
# )

# # updated_lpr
# UPDATED_LPR_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.UPDATED_LPR_POS: POSITION_FACTORY,
#     },
#     {
#     keys.UPDATED_LPR_TIMESTAMP: DATETIME_FACTORY,
#     keys.UPDATED_LPR_TIMEZONE_OFFSET: TIMEZONE_OFFSET_FACTORY,
#     keys.UPDATED_LPR_COUNTRY: UTF8STR_FACTORY,
#     keys.UPDATED_LPR_DEVICE: UTF8STR_FACTORY,
#     },
# )

# # apnx.key
# APNX_KEY_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.APNX_ASIN: UTF8STR_FACTORY,
#     keys.APNX_CDE_TYPE: UTF8STR_FACTORY,
#     keys.APNX_SIDECAR_AVAILABLE: BOOL_FACTORY,
#     keys.APNX_OPN_TO_POS: ARRAY_INT_FACTORY,
#     keys.APNX_FIRST: INT_FACTORY,
#     keys.APNX_UNKNOWN_1: INT_FACTORY,
#     keys.APNX_UNKNOWN_2: INT_FACTORY,
#     keys.APNX_PAGE_MAP: UTF8STR_FACTORY,
#     },
# )

# # fixed.layout.data
# FIXED_LAYOUT_DATA_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.FIXED_LAYOUT_DATA_UNKNOWN_1: BOOL_FACTORY,
#     keys.FIXED_LAYOUT_DATA_UNKNOWN_2: BOOL_FACTORY,
#     keys.FIXED_LAYOUT_DATA_UNKNOWN_3: BOOL_FACTORY,
#     },
# )

# # sharing.limits
# SHARING_LIMITS_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     # TODO discover structure for sharing.limits
#     keys.SHARING_LIMITS_ACCUMULATED:
#     None
#     },
# )

# # language.store
# LANGUAGE_STORE_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.LANGUAGE_STORE_LANGUAGE: UTF8STR_FACTORY,
#     keys.LANGUAGE_STORE_UNKNOWN_1: INT_FACTORY,
#     },
# )

# # periodicals.view.state
# PERIODICALS_VIEW_STATE_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.PERIODICALS_UNKNOWN_1: UTF8STR_FACTORY,
#     keys.PERIODICALS_UNKNOWN_2: INT_FACTORY,
#     },
# )

# # purchase.state.data
# PURCHASE_STATE_DATA_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.PURCHASE_STATE: INT_FACTORY,
#     keys.PURCHASE_TIME: DATETIME_FACTORY,
#     },
# )

# # timer.data.store.v2
# TIMER_DATA_STOREV2_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.TIMERV2_ON: BOOL_FACTORY,
#     keys.TIMERV2_READING_TIMER_MODEL: TIMER_MODEL_FACTORY,
#     keys.TIMERV2_VERSION: INT_FACTORY,
#     keys.TIMERV2_LAST_OPTION: INT_FACTORY,
#     },
# )

# # book.info.store
# BOOK_INFO_STORE_FACTORY: typing.Final[ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.BOOK_INFO_NUM_WORDS: LONG_FACTORY,
#     keys.BOOK_INFO_PERCENT_OF_BOOK: DOUBLE_FACTORY,
#     },
# )

# # page.history.store
# PAGE_HISTORY_STORE_FACTORY: typing.Final[
#     ValFactory[Array]] = ValFactory(Array, PAGE_HISTORY_RECORD_FACTORY)

# # reader.state.preferences
# READER_STATE_PREFERENCES_FACTORY: typing.Final[
#     ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.READER_PREFS_FONT_PREFERENCES: FONT_PREFS_FACTORY,
#     keys.READER_PREFS_LEFT_MARGIN: INT_FACTORY,
#     keys.READER_PREFS_RIGHT_MARGIN: INT_FACTORY,
#     keys.READER_PREFS_TOP_MARGIN: INT_FACTORY,
#     keys.READER_PREFS_BOTTOM_MARGIN: INT_FACTORY,
#     keys.READER_PREFS_UNKNOWN_1: BOOL_FACTORY,
#     },
#     )

# # annotation.personal.bookmark
# # annotation.personal.clip_article
# # annotation.personal.highlight
# # annotation.personal.note
# ANNOTATION_PERSONAL_ELEMENT_FACTORY: typing.Final[
#     ValFactory[FixedMap]] = ValFactory(
#     FixedMap,
#     {
#     keys.ANNOTATION_START_POS: POSITION_FACTORY,
#     keys.ANNOTATION_END_POS: POSITION_FACTORY,
#     keys.ANNOTATION_CREATION_TIME: DATETIME_FACTORY,
#     keys.ANNOTATION_LAST_MODIFICATION_TIME: DATETIME_FACTORY,
#     keys.ANNOTATION_TEMPLATE: UTF8STR_FACTORY,
#     },
#     {
#     keys.ANNOTATION_NOTE: UTF8STR_FACTORY,
#     },
#     )

# # saved.avl.interval.tree (child)
# SAVED_AVL_INTERVAL_TREE_BOOKMARK_FACTORY: typing.Final[
#     ValFactory[NamedValue]
# ] = ValFactory(NamedValue, names.ANNOTATION_PERSONAL_BOOKMARK)
# SAVED_AVL_INTERVAL_TREE_HIGHLIGHT_FACTORY: typing.Final[
#     ValFactory[NamedValue]
# ] = ValFactory(NamedValue, names.ANNOTATION_PERSONAL_HIGHLIGHT)
# SAVED_AVL_INTERVAL_TREE_NOTE_FACTORY: typing.Final[
#     ValFactory[NamedValue]
# ] = ValFactory(NamedValue, names.ANNOTATION_PERSONAL_NOTE)
# SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLE_FACTORY: typing.Final[
#     ValFactory[NamedValue]
# ] = ValFactory(NamedValue, names.ANNOTATION_PERSONAL_CLIP_ARTICLE)

# # saved.avl.interval.tree
# SAVED_AVL_INTERVAL_TREE_BOOKMARKS_FACTORY: typing.Final[
#     ValFactory[Array]
# ] = ValFactory(Array, SAVED_AVL_INTERVAL_TREE_BOOKMARK_FACTORY)
# SAVED_AVL_INTERVAL_TREE_HIGHLIGHTS_FACTORY: typing.Final[
#     ValFactory[Array]
# ] = ValFactory(Array, SAVED_AVL_INTERVAL_TREE_HIGHLIGHT_FACTORY)
# SAVED_AVL_INTERVAL_TREE_NOTES_FACTORY: typing.Final[
#     ValFactory[Array]
# ] = ValFactory(Array, SAVED_AVL_INTERVAL_TREE_NOTE_FACTORY)
# SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLES_FACTORY: typing.Final[
#     ValFactory[Array]
# ] = ValFactory(Array, SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLE_FACTORY)

# # annotation.cache.object
# ANNOTATION_CACHE_OBJECT_FACTORY: typing.Final[ValFactory[SwitchMap]
#                                               ] = ValFactory(
#     SwitchMap,
#     {
#     keys.ANNOTATION_BOOKMARKS:
#     names.SAVED_AVL_INTERVAL_TREE,
#     keys.ANNOTATION_HIGHLIGHTS:
#     names.SAVED_AVL_INTERVAL_TREE,
#     keys.ANNOTATION_NOTES:
#     names.SAVED_AVL_INTERVAL_TREE,
#     keys.ANNOTATION_CLIP_ARTICLES:
#     names.SAVED_AVL_INTERVAL_TREE,
#     },
#     {
#     keys.ANNOTATION_BOOKMARKS:
#     SAVED_AVL_INTERVAL_TREE_BOOKMARKS_FACTORY,
#     keys.ANNOTATION_HIGHLIGHTS:
#     SAVED_AVL_INTERVAL_TREE_HIGHLIGHTS_FACTORY,
#     keys.ANNOTATION_NOTES:
#     SAVED_AVL_INTERVAL_TREE_NOTES_FACTORY,
#     keys.ANNOTATION_CLIP_ARTICLES:
#     SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLES_FACTORY,
#     # keys.ANNOTATION_BOOKMARKS: Template(
#     #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_BOOKMARKS_FACTORY),
#     # keys.ANNOTATION_HIGHLIGHTS: Template(
#     #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_HIGHLIGHTS_FACTORY),
#     # keys.ANNOTATION_NOTES: Template(
#     #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_NOTES_FACTORY),
#     # keys.ANNOTATION_CLIP_ARTICLES: Template(
#     #     NamedValue, names.SAVED_AVL_INTERVAL_TREE, SAVED_AVL_INTERVAL_TREE_CLIP_ARTICLES_FACTORY)
#     },
#                                               )

# NAME_TO_FACTORY: typing.Final[dict[str, None | ValFactory[typing.Any]]] = {
#     names.CLOCK_DATA_STORE: None,
#     names.DICTIONARY: UTF8STR_FACTORY,
#     names.LPU: None,
#     names.PDF_CONTRAST: None,
#     names.SYNC_LPR: BOOL_FACTORY,
#     names.TPZ_LINE_SPACING: None,
#     names.XRAY_OTA_UPDATE_STATE: None,
#     names.XRAY_SHOWING_SPOILERS: None,
#     names.XRAY_SORTING_STATE: None,
#     names.XRAY_TAB_STATE: None,
#     names.DICT_PREFS_V_2: DYNAMIC_MAP_FACTORY,
#     names.END_ACTIONS: DYNAMIC_MAP_FACTORY,
#     names.READER_METRICS: DYNAMIC_MAP_FACTORY,
#     names.START_ACTIONS: DYNAMIC_MAP_FACTORY,
#     names.TRANSLATOR: DYNAMIC_MAP_FACTORY,
#     names.WIKIPEDIA: DYNAMIC_MAP_FACTORY,
#     names.BUY_ASIN_RESPONSE_DATA: JSON_FACTORY,
#     names.NEXT_IN_SERIES_INFO_DATA: JSON_FACTORY,
#     names.PRICE_INFO_DATA: JSON_FACTORY,
#     names.ERL: POSITION_FACTORY,
#     names.LPR: LAST_PAGE_READ_FACTORY,
#     names.FPR: FPR_FACTORY,
#     names.UPDATED_LPR: UPDATED_LPR_FACTORY,
#     names.APNX_KEY:
#     APNX_KEY_FACTORY,  # APNX is "Amazon page num xref" (i.e. page num map)
#     names.FIXED_LAYOUT_DATA: FIXED_LAYOUT_DATA_FACTORY,
#     names.SHARING_LIMITS: SHARING_LIMITS_FACTORY,
#     names.LANGUAGE_STORE: LANGUAGE_STORE_FACTORY,
#     names.PERIODICALS_VIEW_STATE: PERIODICALS_VIEW_STATE_FACTORY,
#     names.PURCHASE_STATE_DATA: PURCHASE_STATE_DATA_FACTORY,
#     names.TIMER_DATA_STORE: TIMER_DATA_STORE_FACTORY,
#     names.TIMER_DATA_STORE_V2: TIMER_DATA_STOREV2_FACTORY,
#     names.BOOK_INFO_STORE: BOOK_INFO_STORE_FACTORY,
#     names.PAGE_HISTORY_STORE: PAGE_HISTORY_STORE_FACTORY,
#     names.READER_STATE_PREFERENCES: READER_STATE_PREFERENCES_FACTORY,
#     names.FONT_PREFS: FONT_PREFS_FACTORY,
#     names.ANNOTATION_CACHE_OBJECT: ANNOTATION_CACHE_OBJECT_FACTORY,
#     names.ANNOTATION_PERSONAL_BOOKMARK: ANNOTATION_PERSONAL_ELEMENT_FACTORY,
#     names.ANNOTATION_PERSONAL_HIGHLIGHT: ANNOTATION_PERSONAL_ELEMENT_FACTORY,
#     names.ANNOTATION_PERSONAL_NOTE: ANNOTATION_PERSONAL_ELEMENT_FACTORY,
#     names.ANNOTATION_PERSONAL_CLIP_ARTICLE: ANNOTATION_PERSONAL_ELEMENT_FACTORY,
# }
