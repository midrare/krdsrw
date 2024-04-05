from __future__ import annotations
import abc
import base64
import copy
import json
import typing
import warnings

from . import schemas

from .builtins import IntBase
from .builtins import ListBase
from .builtins import DictBase
from .cursor import Cursor
from .cursor import Serializable
from .error import UnexpectedBytesError
from .error import UnexpectedStructureError
from .specs import Spec
from .specs import Field
from .specs import Index
from .basics import Basic
from .basics import Byte
from .basics import Char
from .basics import Bool
from .basics import Short
from .basics import Int
from .basics import Long
from .basics import Float
from .basics import Double
from .basics import Utf8Str
from .basics import read_byte
from .basics import write_byte
from .basics import read_int
from .basics import write_int
from .basics import read_long
from .basics import write_long
from .basics import read_utf8str
from .basics import write_utf8str

K = typing.TypeVar("K", bound=int | float | str)
T = typing.TypeVar("T", bound=Byte | Char | Bool | Short | Int | Long \
    | Float | Double | Utf8Str | Serializable)


def _read_basic(cursor: Cursor) \
-> None|Bool|Char|Byte|Short|Int|Long|Float|Double|Utf8Str:
    for t in [ Bool, Byte, Char, Short, Int, Long, Float, Double, Utf8Str ]:
        if cursor._peek_raw_byte() == t.magic_byte:
            return t._create(cursor)

    return None


class Array(ListBase[T], Serializable, metaclass=abc.ABCMeta):
    # Array can contain Basic and other containers
    @classmethod
    def spec(cls,
             elmt: Spec[T],
             schema: None | str = None) -> Spec[typing.Self]:
        class Array(cls):
            @property
            @typing.override
            def elmt_spec(self) -> Spec[T]:
                return elmt

            @property
            @typing.override
            def elmt_schema(self) -> None | str:
                return schema

        return Spec(Array)  # type: ignore

    @property
    @abc.abstractmethod
    def elmt_spec(self) -> Spec[T]:
        raise NotImplementedError("Must be implemented by the subclass.")

    @property
    def elmt_cls(self) -> type[T]:
        return self.elmt_spec.cls_

    @property
    def elmt_schema(self) -> None | str:
        return None

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        size = read_int(cursor)
        for _ in range(size):
            e = result.elmt_spec.read(cursor, result.elmt_schema)
            result.append(e)
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        write_int(cursor, len(self))
        for e in self:
            self.elmt_spec.write(cursor, e, self.elmt_schema)

    def make_element(self, *args, **kwargs) -> T:
        if issubclass(self.elmt_spec.cls_, Basic) and (args or kwargs):
            return self.elmt_spec.make(*args, **kwargs)

        result = self.elmt_spec.make()
        if isinstance(result, dict) and (args or kwargs):
            result.update(*args, **kwargs)
        elif isinstance(result, list) and (args or kwargs):
            result.extend(*args, **kwargs)

        return result

    def make_and_append(self, *args, **kwargs) -> T:
        result = self.make_element(*args, **kwargs)
        self.append(result)
        return result

    @typing.override
    def _is_allowed(self, value: typing.Any) -> bool:
        return self.elmt_spec.is_compatible(value)

    @typing.override
    def _transform(self, value: typing.Any) -> T:
        return self.elmt_spec.make(value)


class _TypedField(typing.NamedTuple):
    spec: Spec[typing.Any]
    schema: None | str = None
    required: bool = True


class _TypedDict(DictBase[str, T], metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        init = dict(*args, **kwargs)
        for key, field in self._key_to_field.items():
            if field.required and key not in init:
                init[key] = field.spec.make()

        # call parent constructor last so that hooks will work
        super().__init__(init)

    @property
    @abc.abstractmethod
    def _key_to_field(self) -> dict[str, _TypedField]:
        raise NotImplementedError("Must be implemented in subclass.")

    @typing.override
    def _is_key_readable(self, key: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        return key in self._key_to_field

    @typing.override
    def _is_key_writable(self, key: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        return bool(self._key_to_field.get(key))

    @typing.override
    def _is_value_writable(
        self,
        value: typing.Any,
        key: typing.Any,
    ) -> bool:
        if not isinstance(key, str):
            return False
        field = self._key_to_field.get(key)
        if not field:
            return False
        if value is not None and not field.spec.is_compatible(value):
            return False
        return True

    @typing.override
    def _is_key_deletable(self, key: typing.Any) -> bool:
        return key not in self._key_to_field or not self._key_to_field[
            key].required

    @typing.override
    def _transform_value(
        self,
        value: typing.Any,
        key: typing.Any,
    ) -> T:
        field = self._key_to_field.get(key)
        if not field:
            raise KeyError(f"No template for key \"{key}\".")
        if value is None:
            value = field.spec.make()
        elif isinstance(value, (bool, int, float, str, bytes)) \
        and not isinstance(value, Basic):
            value = field.spec.make(value)

        return value  # type: ignore

    @typing.override
    def _make_postulate(self, key: typing.Any) -> None | T:
        field = self._key_to_field.get(key)
        if field is None:
            return None
        return field.spec.make()

    @typing.override
    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._required_spec == other._required_spec  # type: ignore
                and self._optional_spec == other._optional_spec  # type: ignore
                and dict(self) == dict(other))
        return super().__eq__(other)

    @typing.override
    def __str__(self) -> str:
        d = { k: v for k, v in self.items() if v is not None }
        return f"{self.__class__.__name__}{d}"

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{dict(self)}"


class Record(_TypedDict, Serializable, metaclass=abc.ABCMeta):
    # Record can contain basics and other containers
    # keys are just arbitrary aliases for convenience. values are
    # hardcoded and knowing what value is where is determined by
    # the order of their appearance

    @classmethod
    def spec(
        cls,
        required: dict[str, Spec | tuple[Spec, str]],
        optional: None | dict[str, Spec | tuple[Spec, str]] = None,
    ) -> Spec[_TypedDict]:
        def explode(o, len_: int) -> list:
            result = []
            if isinstance(o, (tuple, list)):
                result.extend(o)
            else:
                result.append(o)
            result += [ None for _ in range(len_ - len(result)) ]
            return result

        fields = {}

        for alias, _packed in required.items():
            spec, schema = explode(_packed, 2)
            fields[alias] = _TypedField(spec, schema, True)

        for alias, _packed in (optional or {}).items():
            spec, schema = explode(_packed, 2)
            fields[alias] = _TypedField(spec, schema, False)

        class Record(cls):
            @property
            @typing.override
            def _key_to_field(self) -> dict[str, _TypedField]:
                return fields

        return Spec(Record)

    @property
    @abc.abstractmethod
    def _key_to_field(self) -> dict[str, _TypedField]:
        raise NotImplementedError("Must be implemented in subclass.")

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)

        for alias, field in result._key_to_field.items():
            val = result._read_next(cursor, field.spec, field.schema)
            if val is None:
                if field.required:
                    raise UnexpectedStructureError(
                        f'Value for field "{alias}" but was not found',
                        pos=cursor.tell())
                else:
                    break
            result[alias] = val

        return result

    def _read_next(
            self,
            cursor: Cursor,
            spec: Spec[T],
            schema: None | str = None) -> None | T:
        # objects in a Record have no OBJECT_BEGIN OBJECT_END demarcating
        # bytes. the demarcation is implied by the ordering of the elements

        cursor.save()
        try:
            val = spec.read(cursor, schema)
            cursor.unsave()
            return val
        except UnexpectedBytesError:
            cursor.restore()
            return None

    @typing.override
    def _write(self, cursor: Cursor):
        for alias, field in self._key_to_field.items():
            assert (not field.required and alias not in self) \
            or isinstance(self[alias], field.spec.cls_), 'Invalid state'
            if not alias in self:
                assert not field.required, 'required field not present'
                break
            field.spec.write(cursor, self[alias], field.schema)


# can contain Bool, Char, Byte, Short, Int, Long, Float, Double, Utf8Str, Object
class IntMap(_TypedDict, Serializable):
    def __init__(self, *args, **kwargs):
        self._idx_to_field: dict[int, _TypedField] = {}
        self._alias_to_idx: dict[str, int] = {}
        self._idx_to_alias: dict[int, str] = {}

        for i, (alias, field) in enumerate(self._key_to_field.items()):
            self._idx_to_field[i] = field
            self._alias_to_idx[alias] = i
            self._idx_to_alias[i] = alias

        # parent constructor after schema setup so hooks run correctly
        super().__init__(*args, **kwargs)

    @classmethod
    def spec(
        cls,
        alias_schema_spec: list[tuple[str, str, Spec]],
    ) -> Spec[typing.Self]:
        fields = {}
        for alias, schema, spec in alias_schema_spec:
            fields[alias] = _TypedField(spec, schema, False)

        class IntMap(cls):
            @property
            @typing.override
            def _key_to_field(self) -> dict[str, _TypedField]:
                return fields

        return Spec(IntMap)  # type: ignore

    def _to_idx(self, alias: int | str) -> int:
        if isinstance(alias, int):
            return alias

        return self._alias_to_idx[alias]

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        size = read_int(cursor)
        for _ in range(size):
            idxnum = read_int(cursor)

            if idxnum not in result._idx_to_field:
                raise UnexpectedStructureError(
                    f"Object index number {idxnum} not recognized")

            alias = result._idx_to_alias[idxnum]
            schema = result._idx_to_field[idxnum].schema
            spc = result._idx_to_field[idxnum].spec
            result[alias] = spc.read(cursor, schema)
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        write_int(cursor, len(self))

        for alias, value in self.items():
            idx = self._to_idx(alias)
            schema = self._idx_to_field[idx].schema
            spc = self._idx_to_field[idx].spec

            write_int(cursor, idx)
            spc.write(cursor, value, schema)


# can contain Bool, Char, Byte, Short, Int, Long, Float, Double, Utf8Str
class DynamicMap(DictBase[str, typing.Any], Serializable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @typing.override
    def _is_key_readable(self, key: typing.Any) -> bool:
        return isinstance(key, str)

    @typing.override
    def _is_key_writable(self, key: typing.Any) -> bool:
        return isinstance(key, str)

    @typing.override
    def _is_value_writable(
        self,
        value: typing.Any,
        key: typing.Any,
    ) -> bool:
        return isinstance(key, str) and isinstance(value, Basic)

    @typing.override
    def _transform_value(
        self,
        value: typing.Any,
        key: typing.Any,
    ) -> typing.Any:
        if not isinstance(value, Basic):
            if isinstance(value, bool):
                warnings.warn(
                    f"Implicit type conversion "
                    + f"from {value} to Bool({value})")
                value = Bool(value)
            elif isinstance(value, int):
                warnings.warn(
                    f"Implicit type conversion "
                    + f"from {value} to Int({value})")
                value = Int(value)
            elif isinstance(value, float):
                warnings.warn(
                    f"Implicit type conversion "
                    + f"from {value} to Double({value})")
                value = Double(value)
            elif isinstance(value, str):
                warnings.warn(
                    f"Implicit type conversion "
                    + f"from \"{value}\" to Utf8Str({value})")
                value = Utf8Str(value)

        return value

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        size = read_int(cursor)
        for _ in range(size):
            key = read_utf8str(cursor)
            value = _read_basic(cursor)
            assert value is not None, 'Value not found'
            result[key] = value
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        write_int(cursor, len(self))
        for key, value in self.items():
            assert isinstance(key, str)
            write_utf8str(cursor, key)
            value._write(cursor)


class DateTime(IntBase, Serializable):
    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        init = []
        if len(args) + len(kwargs) <= 0:
            init = [-1]
        return super().__new__(cls, *init, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}ms}}"

    @typing.override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}ms}}"

    @typing.override
    def __bool__(self) -> bool:
        return int(self) >= 0

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        return cls(read_long(cursor), *args, **kwargs)

    @typing.override
    def _write(self, cursor: Cursor):
        write_long(cursor, max(-1, int(self)))

    def __bytes__(self) -> bytes:
        csr = Cursor()
        self._write(csr)
        return csr.dump()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, int):
            return int(self) == int(other)
        return False

    def __json__(self) -> None | bool | int | float | str | tuple | list | dict:
        return int(self)


class Json(Serializable):
    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        if list(args) == [None]:
            args = []

        if args:
            for cls_ in [ bool, int, float, str, bytes, list, tuple, dict ]:
                if isinstance(args[0], cls_):
                    subcls = cls._subclass(cls_)
                    return subcls.__new__(subcls, *args, **kwargs)

        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __init__(self, *args, **kwargs):
        if list(args) == [None]:
            args = []
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{}}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{}}"

    @classmethod
    def _subclass(cls, t: type) -> type[typing.Self]:
        return {
            bool: _JsonBool,
            int: _JsonInt,
            float: _JsonFloat,
            str: _JsonStr,
            bytes: _JsonBytes,
            tuple: _JsonTuple,
            list: _JsonList,
            dict: _JsonDict,
        }[t]

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        jsnstr = read_utf8str(cursor)
        value = json.loads(jsnstr) if jsnstr else None
        return cls(value, *args, **kwargs)

    @typing.override
    def _write(self, cursor: Cursor):
        jsnstr = json.dumps(self, cls=_JsonEncoder)
        if jsnstr == 'null':
            jsnstr = ''
        write_utf8str(cursor, jsnstr)

    def __bytes__(self) -> bytes:
        csr = Cursor()
        self._write(csr)
        return csr.dump()

    def __bool__(self) -> bool:
        return False

    def __json__(
            self
    ) -> None | bool | int | float | str | bytes | tuple | list | dict:
        return None


class _JsonBool(int, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__()

    def __bool__(self) -> bool:
        return int(self) != 0

    def __json__(self) -> bool:
        return int(self) != 0


class _JsonInt(int, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonFloat(float, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonStr(str, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonBytes(bytes, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonTuple(tuple, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonList(list, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class _JsonDict(dict, Json):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class _JsonEncoder(json.JSONEncoder):
    @typing.override
    def default(self, o: typing.Any) -> typing.Any:
        f = getattr(o, '__json__', None)
        if f and callable(f):
            return f()
        return super().default(o)

    @typing.override
    def encode(self, o: typing.Any) -> str:
        if isinstance(o, _JsonBool):
            o = bool(o)
        return super().encode(o)

    @typing.override
    def iterencode(
        self,
        o: typing.Any,
        _one_shot: bool = False,
    ) -> typing.Iterator[str]:
        if isinstance(o, _JsonBool):
            o = bool(o)
        return super().iterencode(o, _one_shot)


class Position(_TypedDict, Serializable):
    _MAGIC_CHUNK_V1: typing.Final[int] = 0x01
    _FIELDS: typing.Final[dict[str, _TypedField]] = {
        'char_pos': _TypedField(Spec(Int), None, True),
        'chunk_eid': _TypedField(Spec(Int, -1), None, False),
        'chunk_pos': _TypedField(Spec(Int, -1), None, False),
    }

    @property
    @typing.override
    def _key_to_field(self) -> dict[str, _TypedField]:
        return self._FIELDS

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        s = read_utf8str(cursor)
        split = s.split(":", 2)
        if len(split) > 1:
            b = base64.b64decode(split[0])
            version = b[0]
            if version == result._MAGIC_CHUNK_V1:
                result['chunk_eid'] = int.from_bytes(b[1:5], "little")
                result['chunk_pos'] = int.from_bytes(b[5:9], "little")
            else:
                # TODO throw a proper exception
                raise Exception(
                    "Unrecognized position version 0x%02x" % version)
            result['char_pos'] = int(split[1])
        else:
            result['char_pos'] = int(s)
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        s = ""
        if self['chunk_eid'] >= 0 and self['chunk_pos'] >= 0:
            b_version = self._MAGIC_CHUNK_V1.to_bytes(1, "little", signed=False)
            b_eid = self['chunk_eid'].to_bytes(4, "little", signed=False)
            b_pos = self['chunk_pos'].to_bytes(4, "little", signed=False)
            s += base64.b64encode(b_version + b_eid + b_pos).decode("ascii")
            s += ":"
        s += str(
            int(self['char_pos'])
            if self['char_pos'] is not None and self['char_pos'] >= 0 else -1)
        write_utf8str(cursor, s)


class LPR(_TypedDict, Serializable):  # aka LPR
    _MAGIC_V2: typing.Final[int] = 2
    _FIELDS: typing.Final[dict[str, _TypedField]] = {
        'pos': _TypedField(Spec(Position), None, True),
        'timestamp': _TypedField(Spec(Int), None, False),
        'lpr_version': _TypedField(Spec(Int), None, False),
    }

    @property
    @typing.override
    def _key_to_field(self) -> dict[str, _TypedField]:
        return self._FIELDS

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        init = {}

        type_byte = cursor.peek()
        if type_byte == Utf8Str.magic_byte:
            # old LPR version'
            init['pos'] = Position._create(cursor)
        elif type_byte == Byte.magic_byte:
            # new LPR version
            init['lpr_version'] = read_byte(cursor)
            init['pos'] = Position._create(cursor)
            init['timestamp'] = int(read_long(cursor))
        else:
            raise UnexpectedBytesError(
                cursor.tell(), [Utf8Str.magic_byte, Byte.magic_byte], type_byte)

        return cls(*args, **init, **kwargs)

    @typing.override
    def _write(self, cursor: Cursor):
        # XXX may cause problems if kindle expects the original LPR format
        #   version when datastore file is re-written
        if self['timestamp'] < 0:
            # old LPR version
            self['pos']._write(cursor)
        else:
            # new LPR version
            lpr_version = max(self._MAGIC_V2, self['lpr_version'])
            write_byte(cursor, lpr_version)
            self['pos']._write(cursor)
            write_long(cursor, self['timestamp'])


class TimeZoneOffset(IntBase, Serializable):
    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        init = []
        if len(args) + len(kwargs) <= 0:
            init = [-1]
        return super().__new__(cls, *init, *args, **kwargs)

    @typing.override
    def __init__(self, *args, **kwargs):
        super().__init__()

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        return cls(read_long(cursor), *args, **kwargs)

    @typing.override
    def _write(self, cursor: Cursor):
        write_long(cursor, max(-1, self))

    @typing.override
    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            return int(self) == int(other)
        return super().__eq__(other)

    @typing.override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    def __bool__(self) -> bool:
        return self >= 0

    def __bytes__(self) -> bytes:
        csr = Cursor()
        self._write(csr)
        return csr.dump()

    def __json__(self) -> None | bool | int | float | str | tuple | list | dict:
        return int(self)


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
class DataStore(DictBase, Serializable):
    _MAGIC_STR: typing.Final[bytes] = b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
    _FIXED_MYSTERY_NUM: typing.Final[int] = (
        1  # present after the signature; unknown what this number means
    )

    # named object data structure (schema utf8str + data)
    _OBJECT_BEGIN: typing.Final[int] = 0xfe
    # end of data for object
    _OBJECT_END: typing.Final[int] = 0xff

    @typing.override
    def _is_key_readable(self, key: typing.Any) -> bool:
        return key in self.keys() or schemas.get_factory_by_schema(
            key) is not None

    @typing.override
    def _is_key_writable(self, key: typing.Any) -> bool:
        return key in self.keys() or schemas.get_factory_by_schema(
            key) is not None

    @typing.override
    def _is_value_writable(
        self,
        value: typing.Any,
        key: typing.Any,
    ) -> bool:
        return key in self.keys() or schemas.get_factory_by_schema(
            key) is not None

    @typing.override
    def _is_key_deletable(self, key: typing.Any) -> bool:
        return key in self.keys() or schemas.get_factory_by_schema(
            key) is not None

    @classmethod
    def _eat_signature_or_error(cls, cursor: Cursor):
        if not cursor.eat(cls._MAGIC_STR):
            raise UnexpectedBytesError(
                cursor.tell(),
                cls._MAGIC_STR,
                cursor.peek(len(cls._MAGIC_STR)),
            )

    @classmethod
    def _eat_fixed_mystery_num_or_error(cls, cursor: Cursor):
        cursor.save()
        value = read_long(cursor)
        if value != cls._FIXED_MYSTERY_NUM:
            cursor.restore()
            raise UnexpectedBytesError(
                cursor.tell(),
                Long(cls._FIXED_MYSTERY_NUM).to_bytes(),
                Long(value).to_bytes(),
            )
        cursor.unsave()

    @classmethod
    def _peek_object_type(
        cls,
        csr: Cursor,
        magic_byte: bool = True,
    ) -> None | type:
        from . import schemas
        cls_ = None
        csr.save()

        if not magic_byte or csr.eat(cls._OBJECT_BEGIN):
            schema = read_utf8str(csr, False)
            fct = schemas.get_factory_by_schema(schema)
            assert fct, f'Unsupported schema \"{schema}\".'
            cls_ = fct.cls_

        csr.restore()
        return cls_

    @classmethod
    def _peek_object_schema(
        cls,
        csr: Cursor,
        magic_byte: bool = True,
    ) -> None | str:
        schema = None
        csr.save()
        if not magic_byte or csr.eat(cls._OBJECT_BEGIN):
            schema = read_utf8str(csr, False)
        csr.restore()
        return schema

    @classmethod
    def _read_object(
        cls,
        csr: Cursor,
        schema: None | str = None,
    ) -> tuple[typing.Any, str]:
        assert schema is None or schema, 'expected either null or non-empty schema'
        from . import schemas

        schema_ = cls._peek_object_schema(csr)
        if not schema_:
            raise UnexpectedStructureError('Failed to read schema for object.')
        if schema is not None and schema_ != schema:
            raise UnexpectedStructureError(
                f'Object schema "{schema_}" does not match expected schema "{schema}"'
            )
        maker = schemas.get_factory_by_schema(schema_)
        if not maker:
            raise UnexpectedStructureError(f'Unsupported schema \"{schema_}\".')
        o = maker.read(csr, schema_)
        return o, schema_

    @classmethod
    def _write_object(
        cls,
        csr: Cursor,
        o: typing.Any,
        schema: str,
    ):
        assert schema, 'expected non-empty schema'
        csr.write(cls._OBJECT_BEGIN)
        write_utf8str(csr, schema, False)
        o._write(csr)
        csr.write(cls._OBJECT_END)

    @typing.override
    @classmethod
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        result._eat_signature_or_error(cursor)
        result._eat_fixed_mystery_num_or_error(cursor)

        size = read_int(cursor)
        for _ in range(size):
            value, schema = cls._read_object(cursor)
            assert schema, 'Object has blank schema.'
            result[schema] = value
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        cursor.write(self._MAGIC_STR)
        write_long(cursor, self._FIXED_MYSTERY_NUM)
        write_int(cursor, len(self))
        for schema, value in self.items():
            self._write_object(cursor, value, schema)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{dict(self)}"


ALL_OBJECT_TYPES: typing.Final[tuple[type, ...]] = (
    Array,
    Record,
    IntMap,
    DynamicMap,
    DateTime,
    Json,
    LPR,
    Position,
    TimeZoneOffset,
    DataStore,
)
