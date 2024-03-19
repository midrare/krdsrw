from __future__ import annotations
import abc
import base64
import collections
import collections.abc
import copy
import json
import typing

from . import schemas

from .restricted import RestrictedList
from .restricted import RestrictedDict
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


def _read_basic(cursor: Cursor) \
-> None|Bool|Char|Byte|Short|Int|Long|Float|Double|Utf8Str:
    for t in [ Bool, Byte, Char, Short, Int, Long, Float, Double, Utf8Str ]:
        if cursor._peek_raw_byte() == t.magic_byte:
            return t.create(cursor)

    return None


class Array(RestrictedList[T], Object):
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

    def make(self, *args, **kwargs) -> T:
        if self._elmt_spec.is_basic() and (args or kwargs):
            return self._elmt_spec.cast(*args, **kwargs)

        result = self._elmt_spec.make()
        if isinstance(result, dict) and (args or kwargs):
            result.update(*args, **kwargs)
        elif isinstance(result, list) and (args or kwargs):
            result.extend(*args, **kwargs)

        return result

    def make_and_append(self, *args, **kwargs) -> T:
        result = self.make(*args, **kwargs)
        self.append(result)
        return result

    @typing.override
    def _pre_write_filter(self, value: typing.Any) -> bool:
        return self._elmt_spec.is_castable(value)

    @typing.override
    def _pre_write_transform(self, value: typing.Any) -> T:
        return self._elmt_spec.cast(value)


class Record(RestrictedDict[str, T], Object):
    # Record can contain basics and other containers
    # keys are just arbitrary aliases for convenience. values are
    # hardcoded and knowing what value is where is determined by
    # the order of their appearance

    def __init__(
        self,
        required: dict[str, Spec[T] | tuple[Spec[T], str]],
        optional: None | dict[str, Spec[T] | tuple[Spec[T], str]] = None,
    ):
        super().__init__()

        def get_spec(v):
            if isinstance(v, (tuple, list)):
                return next(e for e in v if isinstance(e, Spec))
            if isinstance(v, Spec):
                return v
            return v

        def get_name(v):
            if isinstance(v, (tuple, list)):
                return next(e for e in v if isinstance(e, str))
            if isinstance(v, str):
                return v
            return ''

        self._required_spec: typing.Final[dict[str, Spec[T]]] \
            = {k: get_spec(v) for k, v in required.items()}
        self._optional_spec: typing.Final[dict[str, Spec[T]]] \
            = {k: get_spec(v) for k, v in (optional or {}).items()}
        self._required_name: typing.Final[dict[str, str]] \
            = {k: get_name(v) for k, v in required.items()}
        self._optional_name: typing.Final[dict[str, str]] \
            = {k: get_name(v) for k, v in (optional or {}).items()}

        for k, v in self._required_spec.items():
            self[k] = v.make()

    @typing.override
    def _pre_read_filter(self, key: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        return key in self._required_spec or key in self._optional_spec

    @typing.override
    def _pre_write_filter(self, key: typing.Any, value: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        maker = self._required_spec.get(key) or self._optional_spec.get(key)
        if not maker:
            return False
        if value is not None and not maker.is_compatible(value):
            return False
        return True

    @typing.override
    def _pre_del_filter(self, key: typing.Any) -> bool:
        return key not in self._required_spec

    @typing.override
    def _pre_write_transform(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[str, T]:
        maker = self._required_spec.get(key) or self._optional_spec.get(key)
        if not maker:
            raise Exception(f"No template for key \"{key}\".")
        if value is None:
            value = maker.make()
        elif isinstance(value, (bool, int, float, str, bytes)) \
        and not isinstance(value, Basic):
            value = maker.cast(value)

        return key, value  # type: ignore

    @typing.override
    def _pre_default_filter(
        self,
        key: typing.Any,
        default: typing.Any,
    ) -> bool:
        if not isinstance(key, str):
            return False
        maker = self._required_spec.get(key) or self._optional_spec.get(key)
        if not maker:
            return False
        if default is not None and not maker.is_compatible(default):
            return False
        return True

    @typing.override
    def _pre_default_transform(
        self: typing.Any,
        key: typing.Any,
        default: typing.Any,
    ) -> T:
        maker = self._required_spec.get(key) or self._optional_spec.get(key)
        if not maker:
            raise Exception(f"No template for key \"{key}\".")
        if default is None:
            default = maker.make()
        elif isinstance(default, (bool, int, float, str, bytes)) \
        and not isinstance(default, Basic):
            default = maker.cast(default)
        return default  # type: ignore

    @property
    def required(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._required_spec.items() }

    @property
    def optional(self) -> dict[str, type[T]]:
        return { k: v.cls_ for k, v in self._optional_spec.items() }

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()

        for alias, spec in self._required_spec.items():
            name = self._required_name.get(alias)
            val = self._read_next(cursor, spec, name)
            if val is None:
                raise UnexpectedStructureError(
                    f'Value for field "{alias}" but was not found',
                    pos=cursor.tell())
            self[alias] = val

        for alias, spec in self._optional_spec.items():
            name = self._optional_name.get(alias)
            val = self._read_next(cursor, spec, name)
            if val is None:
                break
            self[alias] = val

    def _read_next(
            self,
            cursor: Cursor,
            spec: Spec[T],
            name: None | str = None) -> None | T:
        # objects in a Record have no OBJECT_BEGIN OBJECT_END demarcating
        # bytes. the demarcation is implied by the ordering of the elements

        cursor.save()
        try:
            val = spec.read(cursor, name)
            cursor.unsave()
            return val
        except UnexpectedBytesError:
            cursor.restore()
            return None

    @typing.override
    def write(self, cursor: Cursor):
        for alias, spec in self._required_spec.items():
            assert isinstance(self[alias], spec.cls_), 'Invalid state'
            name = self._required_name.get(alias)
            spec.write(cursor, self[alias], name)

        for alias, spec in self._optional_spec.items():
            value = self.get(alias)
            if value is None:
                break
            assert isinstance(value, spec.cls_), 'Invalid state'
            name = self._optional_name.get(alias)
            spec.write(cursor, value, name)

    @typing.override
    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._required_spec == other._required  # type: ignore
                and self._optional_spec == other._optional  # type: ignore
                and dict(self) \
                == dict(other)
            )
        return super().__eq__(other)

    @typing.override
    def __str__(self) -> str:
        d = { k: v for k, v in self.items() if v is not None }
        return f"{self.__class__.__name__}{d}"

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{dict(self)}"


# can contain Bool, Char, Byte, Short, Int, Long, Float, Double, Utf8Str, Object
class IntMap(RestrictedDict[str, typing.Any], Object):
    def __init__(self, idx_alias_name_spec: list[tuple[int, str, str, Spec]]):
        super().__init__()

        self._idx_to_spec: dict[int, Spec] = {}
        self._idx_to_name: dict[int, str] = {}
        self._idx_to_alias: dict[int, str] = {}

        for idx, alias, name, spec in idx_alias_name_spec:
            self._idx_to_alias[idx] = alias
            self._idx_to_name[idx] = name
            self._idx_to_spec[idx] = spec

        for idx, alias, name, spec in idx_alias_name_spec:
            self[alias] = spec.make()

    @typing.override
    def _pre_read_filter(self, key: typing.Any) -> bool:
        return key in list(self._idx_to_spec.keys()) \
            + list(self._idx_to_name.keys()) \
            + list(self._idx_to_alias.keys()) \
            + list(self._idx_to_alias.values())

    @typing.override
    def _pre_del_filter(self, key: typing.Any) -> bool:
        return False

    @typing.override
    def _pre_write_filter(self, key: typing.Any, value: typing.Any) -> bool:
        if key not in list(self._idx_to_spec.keys()) \
                + list(self._idx_to_name.keys()) \
                + list(self._idx_to_alias.keys()) \
                + list(self._idx_to_alias.values()):
            return False

        idx = self._to_idx(key) if isinstance(key, str) else key
        assert idx >= 0, 'failed to determine key'
        if not self._idx_to_spec[idx].is_instance(value):
            return False

        return True

    @typing.override
    def _pre_read_transform(self, key: typing.Any) -> str:
        return self._to_alias(key)

    @typing.override
    def _pre_write_transform(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[str, typing.Any]:
        maker = self._idx_to_spec[self._to_idx(key)]
        if maker.is_basic() \
        and isinstance(value, (bool, int, float, str, bytes)) \
        and not isinstance(value, Basic):
            value = maker.cast(value)

        return self._to_alias(key), value

    @typing.override
    def _pre_default_filter(self, key: typing.Any, default: typing.Any) -> bool:
        if default is None:
            return True

        idx = self._to_idx(key)
        return self._idx_to_spec[idx].is_compatible(default)

    @typing.override
    def _pre_default_transform(
        self: typing.Any,
        key: typing.Any,
        default: typing.Any,
    ) -> typing.Any:
        if default is None:
            idx = self._to_idx(key)
            default = self._idx_to_spec[idx].make()

        maker = self._idx_to_spec[self._to_idx(key)]
        if maker.is_basic() \
        and isinstance(default, (bool, int, float, str, bytes)) \
        and not isinstance(default, Basic):
            default = maker.cast(default)

        return default

    def _to_idx(self, alias: int | str) -> int:
        if isinstance(alias, int):
            return alias

        for k, v in self._idx_to_alias.items():
            if v == alias:
                return k

        raise ValueError(
            f"Human-readable alias \"{alias}\" has no associated index.")

    def _to_alias(self, idx: int | str) -> str:
        if isinstance(idx, str):
            return idx

        # we want to use string alias instead of raw int so that casting
        # to plain dict retains human-readable key names
        for k, v in self._idx_to_alias.items():
            if idx == k:
                return v

        raise ValueError(
            f"Index \"{idx}\" has no associated human-readable alias.")

    @typing.override
    def read(self, cursor: Cursor):
        self.clear()
        size = cursor.read_int()
        for _ in range(size):
            idxnum = cursor.read_int()

            if idxnum not in list(self._idx_to_spec.keys()) \
                    + list(self._idx_to_alias.keys()):
                raise UnexpectedStructureError(
                    f"Object index number {idxnum} not recognized")
            name = self._idx_to_name[idxnum]
            self[name] = self._idx_to_spec[idxnum].read(cursor, name)

    @typing.override
    def write(self, cursor: Cursor):
        cursor.write_int(len(self))

        for name, value in self.items():
            idx = self._to_idx(name)
            cursor.write_int(idx)
            self._idx_to_spec[idx].write(cursor, value, name)


# can contain Bool, Char, Byte, Short, Int, Long, Float, Double, Utf8Str
class DynamicMap(RestrictedDict[str, typing.Any], Object):
    def __init__(self):
        super().__init__()

    @typing.override
    def _pre_read_filter(self, key: typing.Any) -> bool:
        return isinstance(key, str)

    @typing.override
    def _pre_write_filter(self, key: typing.Any, value: typing.Any) -> bool:
        return isinstance(key, str) and isinstance(value, Basic)

    @typing.override
    def _pre_default_filter(self, key: typing.Any, default: typing.Any) -> bool:
        return isinstance(key, str) and (default is None \
            or isinstance(default, (bool, int, float, str, bytes)))

    @typing.override
    def _pre_write_transform(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[str, typing.Any]:
        if not isinstance(value, Basic):
            if isinstance(value, bool):
                value = Bool(value)
            elif isinstance(value, int):
                value = Int(value)
            elif isinstance(value, float):
                value = Double(value)
            elif isinstance(value, str):
                value = Utf8Str(value)
        return super()._pre_write_transform(key, value)

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
            raise UnexpectedBytesError(
                cursor.tell(), [Utf8Str.magic_byte, Byte.magic_byte], type_byte)

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


# fpr, updated_lpr
PageReadPos = typing.TypedDict(
    'PageReadPos', {
        'pos': Position,
        'timestamp': typing.NotRequired[DateTime],
        'timezone_offset': typing.NotRequired[TimeZoneOffset],
        'country': typing.NotRequired[Utf8Str],
        'device': typing.NotRequired[Utf8Str],
    })

# apnx.key
APNXKey = typing.TypedDict(
    'APNXKey', {
        'asin': Utf8Str,
        'cde_type': Utf8Str,
        'sidecar_available': Bool,
        'opn_to_pos': Array[Int],
        'first': Int,
        'unknown1': Int,
        'unknown2': Int,
        'page_map': Utf8Str,
    })

# fixed.layout.data
FixedLayoutData = typing.TypedDict(
    'FixedLayoutData', {
        'unknown1': Bool,
        'unknonw2': Bool,
        'unknown3': Bool,
    })

# sharing.limits
SharingLimits = typing.TypedDict(
    'SharingLimits',
    {
        'accumulated': NotImplemented,  # TODO structure for sharing.limits
    })

# language.store
LanguageStore = typing.TypedDict(
    'LanguageStore', {
        'language': Utf8Str,
        'unknown1': Int,
    })

# periodicals.view.state
PeriodicalsViewState = typing.TypedDict(
    'PeriodicalsViewState', {
        'unknown1': Utf8Str,
        'unknown2': Int,
    })

# purchase.state.data
PurchaseStateData = typing.TypedDict(
    'PurchaseStateData', {
        'state': Int,
        'time': DateTime,
    })

# timer.average.calculator.distribution.normal
TimerAverageCalculatorDistributionNormal = typing.TypedDict(
    'TimerAverageCalculatorDistributionNormal', {
        'count': Long,
        'sum': Double,
        'sum_of_squares': Double,
    })

# timer.average.calculator.outliers
TimerAverageCalculatorOutliers = Array[Double]

# timer.model[average_calculator]
TimerAverageCalculator = typing.TypedDict(
    'TimerAverageCalculator',
    {
        'samples1': Array[Double],
        'samples2': Array[Double],
        'normal_distributions':
        Array[TimerAverageCalculatorDistributionNormal],  # type: ignore
        'outliers': Array[TimerAverageCalculatorOutliers],
    })

# timer.model
TimerModel = typing.TypedDict(
    'TimerModel', {
        'version': Long,
        'total_time': Long,
        'total_words': Long,
        'total_percent': Double,
        'average_calculator': TimerAverageCalculator,
    })

# timer.data.store
TimerDataStore = typing.TypedDict(
    'TimerDataStore', {
        'on': Bool,
        'reading_timer_model': TimerModel,
        'version': Int,
    })

# timer.data.store.v2
TimerDataStoreV2 = typing.TypedDict(
    'TimerDataStoreV2', {
        'on': Bool,
        'reading_timer_model': TimerModel,
        'version': Int,
        'last_option': Int,
    })

# book.info.store
BookInfoStore = typing.TypedDict(
    'BookInfoStore', {
        'num_words': Long,
        'percent_of_book': Double,
    })

# page.history.store (array element)
PageHistoryStoreElement = typing.TypedDict(
    'PageHistoryStoreElement', {
        'pos': Position,
        'time': DateTime,
    })

# font.prefs
FontPrefs = typing.TypedDict(
    'FontPrefs', {
        'typeface': Utf8Str,
        'line_sp': Int,
        'size': Int,
        'align': Int,
        'inset_top': Int,
        'inset_left': Int,
        'inset_bottom': Int,
        'inset_right': Int,
        'unknown1': Int,
        'bold': typing.NotRequired[Int],
        'user_sideloadable_font': typing.NotRequired[Utf8Str],
        'custom_font_index': typing.NotRequired[Int],
        'mobi7_system_font': typing.NotRequired[Utf8Str],
        'mobi7_restore_font': typing.NotRequired[Utf8Str],
        'reading_preset_selected': typing.NotRequired[Utf8Str],
    })

# reader.state.preferences
ReaderStatePreferences = typing.TypedDict(
    'ReaderStatePreferences', {
        'font_preferences': FontPrefs,
        'left_margin': Int,
        'right_margin': Int,
        'top_margin': Int,
        'bottom_margin': Int,
        'unknown1': Bool,
    })

# annotation.personal.bookmark
# annotation.personal.highlight
# annotation.personal.note
# annotation.personal.clip_article
AnnotationPersonalElement = typing.TypedDict(
    'AnnotationPersonalElement', {
        'start_pos': Position,
        'end_pos': Position,
        'creation_time': DateTime,
        'last_modification_time': DateTime,
        'template': Utf8Str,
        'note': typing.NotRequired[Utf8Str],
    })

# annotation.cache.object
AnnotationCacheObject = typing.TypedDict(
    'AnnotationCacheObject',
    {
        'bookmarks': Array[AnnotationPersonalElement],  # type: ignore
        'highlights': Array[AnnotationPersonalElement],  # type: ignore
        'notes': Array[AnnotationPersonalElement],  # type: ignore
        'clip_articles': Array[AnnotationPersonalElement],  # type: ignore
    })

# whisperstore.migration.status
WhisperstoreMigrationStatus = typing.TypedDict(
    'WhisperstoreMigrationStatus', {
        'unknown1': Bool,
        'unknown2': Bool,
    })

# can contain Bool, Char, Byte, Short, Int, Long, Float, Double, Utf8Str, Object
from .typehints import _SchemaDict


class DataStore(_SchemaDict, Object):
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

    @typing.override
    def _pre_read_filter(self, key: typing.Any) -> bool:
        return key in self.keys() or schemas.get_spec_by_name(key) is not None

    @typing.override
    def _pre_write_filter(self, key: typing.Any, value: typing.Any) -> bool:
        return key in self.keys() or schemas.get_spec_by_name(key) is not None

    @typing.override
    def _pre_del_filter(self, key: typing.Any) -> bool:
        return key in self.keys() or schemas.get_spec_by_name(key) is not None

    def _key(self, key: typing.Any) -> bool | int | float | str:
        spec = schemas.get_spec_by_name(key)
        assert spec, 'spec should not be null'
        if key not in self.keys():
            self[key] = spec.make()
        return key

    def _key_value(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[bool | int | float | str, Bool | Char | Byte | Short | Int
               | Long | Float | Double
               | Utf8Str | Object]:
        return key, value

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
            value, name = cursor.read_object()
            assert name, 'Object has blank name.'
            self[name] = value

    def write(self, cursor: Cursor):
        cursor.write(self.MAGIC_STR)
        cursor.write_long(self.FIXED_MYSTERY_NUM)
        cursor.write_int(len(self))
        for name, value in self.items():
            cursor.write_object(value, name)

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