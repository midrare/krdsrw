from __future__ import annotations

import abc
import base64
import copy
import dataclasses
import inspect
import json
import typing
import warnings

from .basics import Basic
from .basics import Bool
from .basics import Byte
from .basics import Char
from .basics import Double
from .basics import Float
from .basics import Int
from .basics import Long
from .basics import Short
from .basics import Utf8Str
from .basics import read_byte
from .basics import read_int
from .basics import read_long
from .basics import read_utf8str
from .basics import write_byte
from .basics import write_int
from .basics import write_long
from .basics import write_utf8str
from .builtins import DictBase
from .builtins import IntBase
from .builtins import ListBase
from .constants import OBJECT_BEGIN
from .constants import OBJECT_END
from .cursor import Cursor
from .cursor import Serializable
from .error import UnexpectedBytesError
from .error import UnexpectedStructureError

K = typing.TypeVar("K", bound=int | float | str)
T = typing.TypeVar(
    "T",
    bound=Byte
    | Char
    | Bool
    | Short
    | Int
    | Long
    | Float
    | Double
    | Utf8Str
    | Serializable,
)


def _flatten(o: typing.Any, skip_null: bool = True) -> list[typing.Any]:
    def recurse(oo: typing.Any, master: list[typing.Any]):
        if isinstance(oo, (tuple, list)):
            for e in oo:
                recurse(e, master)
            return
        if skip_null and oo is None:
            return
        master.append(oo)

    result = []
    recurse(o, result)
    return result


def _explode(
    o: typing.Any | list[typing.Any], size: int = 0
) -> list[typing.Any]:
    result = []
    if isinstance(o, (tuple, list)):
        result.extend(o)
    else:
        result.append(o)
    result += [None for _ in range(size - len(result))]
    return result


def _read_object(
    cursor: Cursor,
    cls_: type,
    schema: typing.Any | None = None,
    schema_id: None | str = None,
) -> T:
    if schema_id:
        if not cursor.eat(OBJECT_BEGIN):
            raise UnexpectedBytesError(
                cursor.tell(), OBJECT_BEGIN, cursor.peek()
            )

        schema_id_actual = read_utf8str(cursor, False)
        if not schema_id_actual:
            raise UnexpectedStructureError("Object has blank schema.")
        if schema_id_actual != schema_id:
            raise UnexpectedStructureError(
                f'Expected object schema "{schema_id}"'
                + f' but got "{schema_id_actual}".'
            )

    # noinspection PyProtectedMember
    result = cls_._create(cursor, _schema=schema)  # type: ignore

    if schema_id and not cursor.eat(OBJECT_END):
        raise UnexpectedBytesError(cursor.tell(), OBJECT_END, cursor.peek())

    assert result is not None, "Failed to create object"
    return result  # type: ignore


def _make_object(
    cls_: type,
    *args,
    schema: typing.Any | None = None,
    **kwargs,
) -> typing.Any:
    if schema is not None:
        return cls_(*args, _schema=schema, **kwargs)
    return cls_(*args, **kwargs)


def _write_object(
    cursor: Cursor,
    o: typing.Any,
    schema_id: None | str = None,
):
    if schema_id:
        cursor.write(OBJECT_BEGIN)
        write_utf8str(cursor, schema_id, False)
    # noinspection PyProtectedMember
    o._write(cursor)
    if schema_id:
        cursor.write(OBJECT_END)


def _is_compatible(
    o: type | typing.Any,
    cls_: type | typing.Iterable[type],
) -> bool:
    if inspect.isclass(cls_):
        cls_ = [cls_]

    for e in cls_:
        if (inspect.isclass(o) and issubclass(o, e)) or (
            not inspect.isclass(o) and isinstance(o, e)
        ):
            return True

        for t in [bool, int, float, str, bytes, list, tuple, dict]:
            if issubclass(e, t) and (
                (inspect.isclass(o) and issubclass(o, t))
                or (not inspect.isclass(o) and isinstance(o, t))
            ):
                return True

    return False


@dataclasses.dataclass
class Protoform:
    cls_: type
    schema: typing.Any | None = dataclasses.field(default=None)
    name: None | str = dataclasses.field(default=None)


@dataclasses.dataclass
class Field:
    proto: Protoform = dataclasses.field()
    schema_id: None | str = dataclasses.field(default=None)
    required: None | bool = dataclasses.field(default=None)


Index: typing.TypeAlias = Field
Mapping: typing.TypeAlias = dict[str, Field]


def _fix_mapping(schema: Mapping, default_required: None | bool = None):
    for k in list(schema.keys()):
        if schema[k] is NotImplemented:
            del schema[k]
            continue

        if inspect.isclass(schema[k]):
            t = schema[k]
            assert isinstance(t, type)
            schema[k] = Field(Protoform(t))

        if schema[k].required is None:
            schema[k].required = default_required


class Array(ListBase[T], Serializable, metaclass=abc.ABCMeta):
    # Array can contain Basic and other containers

    @typing.override
    def __init__(self, *args, _schema: Index, **kwargs):
        assert _schema, "schema must be provided (non-null)"
        self.__elmt_cls: type[T] = _schema.proto.cls_  # type: ignore
        self.__elmt_schema: typing.Any = _schema.proto.schema
        self.__elmt_schema_id: None | str = _schema.schema_id or None

        # super constructor last so hooks work properly
        super().__init__(*args, **kwargs)

    @property
    def elmt_schema_cls(self) -> type[T]:
        return self.__elmt_cls

    @property
    def elmt_schema_id(self) -> None | str:
        return self.__elmt_schema_id

    @classmethod
    def _schema(
        cls,
        cls_: type,
        schema: typing.Any | None = None,
        schema_id: None | str = None,
    ) -> Index:
        return Index(Protoform(cls_, schema), schema_id)

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        size = read_int(cursor)
        for _ in range(size):
            result.append(
                _read_object(
                    cursor,
                    result.__elmt_cls,
                    result.__elmt_schema,
                    result.__elmt_schema_id,
                )
            )
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        write_int(cursor, len(self))
        for e in self:
            _write_object(cursor, e, self.__elmt_schema_id)

    def make_element(self, *args, **kwargs) -> T:
        if issubclass(self.__elmt_cls, dict):
            init = dict(*args, **kwargs)
            return _make_object(
                self.__elmt_cls, init, schema=self.__elmt_schema
            )

        if issubclass(self.__elmt_cls, tuple):
            init = tuple(*args, **kwargs)
            return _make_object(
                self.__elmt_cls, init, schema=self.__elmt_schema
            )

        if issubclass(self.__elmt_cls, list):
            init = list(*args, **kwargs)
            return _make_object(
                self.__elmt_cls, init, schema=self.__elmt_schema
            )

        return _make_object(
            self.__elmt_cls, *args, schema=self.__elmt_schema, **kwargs
        )

    def make_and_append(self, *args, **kwargs) -> T:
        result = self.make_element(*args, **kwargs)
        self.append(result)
        return result

    @typing.override
    def _is_allowed(self, value: typing.Any) -> bool:
        return _is_compatible(value, self.__elmt_cls)

    @typing.override
    def _transform(self, value: typing.Any) -> T:
        return _make_object(self.__elmt_cls, value, schema=self.__elmt_schema)


class _TypedDict(DictBase[str, T], metaclass=abc.ABCMeta):
    @typing.override
    def __init__(self, *args, _schema: Mapping, **kwargs):
        schema = copy.deepcopy(_schema)
        _fix_mapping(schema, True)

        init = dict(*args, **kwargs)
        for key, field in schema.items():
            if field.required and key not in init:
                init[key] = _make_object(
                    field.proto.cls_, schema=field.proto.schema
                )

        self.__key_to_field: Mapping = schema

        # call parent constructor last so that hooks will work
        super().__init__(init)

    @typing.override
    @typing.final
    def _is_key_readable(self, key: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        return key in self.__key_to_field

    @typing.override
    @typing.final
    def _is_key_writable(self, key: typing.Any) -> bool:
        if not isinstance(key, str):
            return False
        return bool(self.__key_to_field.get(key))

    @typing.override
    @typing.final
    def _is_value_writable(
        self,
        value: typing.Any,
        key: typing.Any,
    ) -> bool:
        if not isinstance(key, str):
            return False
        field = self.__key_to_field.get(key)
        if not field:
            return False
        if value is not None and not _is_compatible(value, field.proto.cls_):
            return False
        return True

    @typing.override
    @typing.final
    def _is_key_deletable(self, key: typing.Any) -> bool:
        return (
            key not in self.__key_to_field
            or not self.__key_to_field[key].required
        )

    @typing.override
    @typing.final
    def _transform_value(
        self,
        value: typing.Any,
        key: typing.Any,
    ) -> T:
        field = self.__key_to_field.get(key)
        if not field:
            raise KeyError(f'No template for key "{key}".')

        if value is None:
            value = _make_object(field.proto.cls_, schema=field.proto.schema)
        else:
            value = _make_object(
                field.proto.cls_, value, schema=field.proto.schema
            )

        assert isinstance(value, field.proto.cls_)
        return value  # type: ignore

    @typing.override
    @typing.final
    def _make_postulate(self, key: typing.Any) -> T | None:
        field = self.__key_to_field.get(key)
        if field is None:
            return None
        return _make_object(field.proto.cls_, schema=field.proto.schema)

    @typing.override
    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, self.__class__):
            # noinspection PyProtectedMember
            return (
                (
                    self._required_spec  # type: ignore
                    == other._required_spec  # type: ignore
                )
                and (
                    self._optional_spec  # type: ignore
                    == other._optional_spec  # type: ignore
                )
                and (dict(self) == dict(other))
            )
        return super().__eq__(other)

    @typing.override
    def __str__(self) -> str:
        return str({k: v for k, v in self.items() if v is not None})

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{dict(self)}"


class Record(_TypedDict, Serializable, metaclass=abc.ABCMeta):
    # Record can contain basics and other containers
    # keys are just arbitrary aliases for convenience. values are
    # hardcoded and knowing what value is where is determined by
    # the order of their appearance

    @typing.override
    def __init__(
        self,
        *args,
        _schema: Mapping,
        **kwargs,
    ):
        schema = copy.deepcopy(_schema)
        _fix_mapping(schema, True)

        self.__key_to_field: Mapping = schema
        # super constructor last so hooks work correctly
        super().__init__(*args, _schema=schema, **kwargs)

    @classmethod
    def _schema(cls, mapping: dict[str, type | Field]) -> Mapping:
        return copy.deepcopy(mapping)

    @classmethod
    @typing.override
    def _create(
        cls,
        cursor: Cursor,
        *args,
        _schema: Mapping,
        **kwargs,
    ) -> typing.Self:
        schema = copy.deepcopy(_schema)
        _fix_mapping(schema)

        result = cls(*args, _schema=schema, **kwargs)

        for alias, field in schema.items():
            val = cls._read_next(
                cursor,
                field.proto.cls_,
                field.proto.schema,
                field.schema_id,
            )

            if val is None:
                if field.required:
                    raise UnexpectedStructureError(
                        f'Value for field "{alias}" but was not found',
                        pos=cursor.tell(),
                    )
                else:
                    break

            result[alias] = val

        return result

    @classmethod
    def _read_next(
        cls,
        cursor: Cursor,
        cls_: type,
        schema: typing.Any,
        schema_id: None | str = None,
    ) -> T | None:
        # objects in a Record have no OBJECT_BEGIN OBJECT_END demarcating
        # bytes. the demarcation is implied by the ordering of the elements

        cursor.save()
        try:
            val = _read_object(cursor, cls_, schema, schema_id)
            cursor.unsave()
            return val
        except UnexpectedBytesError:
            cursor.restore()
            return None

    @typing.override
    def _write(self, cursor: Cursor):
        for alias, field in self.__key_to_field.items():
            if alias not in self:
                assert not field.required, "required field not present"
                break
            assert isinstance(self[alias], field.proto.cls_), "invalid state"
            _write_object(cursor, self[alias], field.schema_id)


class IntMap(_TypedDict, Serializable):
    # can contain Bool, Char, Byte, Short, Int, Long, Float, Double,
    #   Utf8Str, Object

    def __init__(self, *args, _schema: Mapping, **kwargs):
        schema = copy.deepcopy(_schema)
        _fix_mapping(schema, False)

        self.__idx_to_field: dict[int, Field] = {}
        self.__alias_to_idx: dict[str, int] = {}
        self.__idx_to_alias: dict[int, str] = {}

        for i, (alias, field) in enumerate(schema.items()):
            self.__idx_to_field[i] = field
            self.__alias_to_idx[alias] = i
            self.__idx_to_alias[i] = alias

        # parent constructor after schema setup so hooks run correctly
        super().__init__(*args, _schema=schema, **kwargs)

    def __to_idx(self, alias: int | str) -> int:
        if isinstance(alias, int):
            return alias

        return self.__alias_to_idx[alias]

    @classmethod
    def _schema(cls, mapping: dict[str, type | Field]) -> Mapping:
        return copy.deepcopy(mapping)

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        size = read_int(cursor)
        for _ in range(size):
            idxnum = read_int(cursor)

            if idxnum not in result.__idx_to_field:
                raise UnexpectedStructureError(
                    f"Object index number {idxnum} not recognized"
                )

            alias = result.__idx_to_alias[idxnum]
            cls_ = result.__idx_to_field[idxnum].proto.cls_
            schema_id = result.__idx_to_field[idxnum].schema_id
            schema = result.__idx_to_field[idxnum].proto.schema

            result[alias] = _read_object(cursor, cls_, schema, schema_id)
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        write_int(cursor, len(self))

        for alias, value in self.items():
            idx = self.__to_idx(alias)
            schema_id = self.__idx_to_field[idx].schema_id

            write_int(cursor, idx)
            _write_object(cursor, value, schema_id)


# can contain Bool, Char, Byte, Short, Int, Long, Float, Double, Utf8Str
class DynamicMap(DictBase[str, typing.Any], Serializable):
    @typing.override
    def __init__(self, *args, **kwargs):
        args = list(args)
        kwargs = dict(kwargs)

        if args == [None]:
            args = []

        if kwargs.get("_schema") is None:
            kwargs.pop("_schema", None)

        assert "_schema" not in kwargs, "invalid argument"
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
                    + f"from {value} to Bool({value})"
                )
                value = Bool(value)
            elif isinstance(value, int):
                warnings.warn(
                    f"Implicit type conversion "
                    + f"from {value} to Int({value})"
                )
                value = Int(value)
            elif isinstance(value, float):
                warnings.warn(
                    f"Implicit type conversion "
                    + f"from {value} to Double({value})"
                )
                value = Double(value)
            elif isinstance(value, str):
                warnings.warn(
                    f"Implicit type conversion "
                    + f'from "{value}" to Utf8Str({value})'
                )
                value = Utf8Str(value)

        return value

    @classmethod
    def _read_basic(
        cls, cursor: Cursor
    ) -> (
        None
        | Bool
        | Char
        | Byte
        | Short
        | Int
        | Long
        | Float
        | Double
        | Utf8Str
    ):
        for t in [Bool, Byte, Char, Short, Int, Long, Float, Double, Utf8Str]:
            if cursor.peek() == t.magic_byte:
                # noinspection PyProtectedMember
                return t._create(cursor)

        return None

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        size = read_int(cursor)
        for _ in range(size):
            key = read_utf8str(cursor)
            value = cls._read_basic(cursor)
            assert value is not None, "Value not found"
            result[key] = value
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        write_int(cursor, len(self))
        for key, value in self.items():
            assert isinstance(key, str)
            write_utf8str(cursor, key)
            _write_object(cursor, value)


class DateTime(IntBase, Serializable):
    @typing.override
    def __new__(
        cls,
        *args,
        _schema: None | int = None,
        **kwargs,
    ) -> typing.Self:
        args = list(args)
        kwargs = dict(kwargs)

        if args == [None]:
            args = []

        if kwargs.get("_schema") is None:
            kwargs.pop("_schema", None)

        assert "_schema" not in kwargs, "invalid argument"
        if not args and _schema is not None:
            args = [_schema]
        return super().__new__(cls, *args, **kwargs)

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

    def __json__(
        self,
    ) -> None | bool | int | float | str | tuple | list | dict:
        return int(self)


class Json(Serializable):
    @typing.override
    def __new__(
        cls,
        *args,
        _schema: (
            None | bool | int | float | str | bytes | tuple | list | dict
        ) = None,
        **kwargs,
    ) -> Json:
        args = list(args)
        kwargs = dict(kwargs)

        if args == [None]:
            args = []

        if kwargs.get("_schema") is None:
            kwargs.pop("_schema", None)

        if not args and _schema is not None:
            args = [_schema]

        if args:
            for cls_ in [bool, int, float, str, bytes, list, tuple, dict]:
                if isinstance(args[0], cls_):
                    subcls = cls._subclass(cls_)
                    return subcls.__new__(subcls, *args, **kwargs)

        return super().__new__(cls)

    # noinspection PyUnusedLocal
    @typing.override
    def __init__(self, *args, **kwargs):
        super().__init__()

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
        }[
            t
        ]  # type: ignore

    @classmethod
    @typing.override
    def _create(
        cls,
        cursor: Cursor,
        *args,
        _schema: typing.Any | None = None,
        **kwargs,
    ) -> typing.Self:
        jsnstr = read_utf8str(cursor)
        value = json.loads(jsnstr) if jsnstr else None
        return cls(value, *args, _schema=_schema, **kwargs)

    @typing.override
    def _write(self, cursor: Cursor):
        jsnstr = json.dumps(self, cls=_JsonEncoder)
        if jsnstr == "null":
            jsnstr = ""
        write_utf8str(cursor, jsnstr)

    def __bytes__(self) -> bytes:
        csr = Cursor()
        self._write(csr)
        return csr.dump()

    def __bool__(self) -> bool:
        return False

    def __json__(
        self,
    ) -> None | bool | int | float | str | bytes | tuple | list | dict:
        return None


class _JsonBool(int, Json):  # type: ignore
    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()

    def __bool__(self) -> bool:
        return int(self) != 0

    def __json__(self) -> bool:
        return int(self) != 0


class _JsonInt(int, Json):  # type: ignore
    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonFloat(float, Json):  # type: ignore
    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonStr(str, Json):  # type: ignore
    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonBytes(bytes, Json):  # type: ignore
    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonTuple(tuple, Json):  # type: ignore
    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()


class _JsonList(list, Json):  # type: ignore
    def __init__(
        self,
        *args,
        _schema: typing.Any | None = None,
        **kwargs,
    ):
        args = list(args)
        kwargs = dict(kwargs)

        if args == [None]:
            args = []

        if kwargs.get("_schema") is None:
            kwargs.pop("_schema", None)

        if not args and _schema is not None:
            args = [_schema]

        super().__init__(*args, **kwargs)


class _JsonDict(dict, Json):  # type: ignore
    def __init__(
        self,
        *args,
        _schema: typing.Any | None = None,
        **kwargs,
    ):
        args = list(args)
        kwargs = dict(kwargs)

        if args == [None]:
            args = []

        if kwargs.get("_schema") is None:
            kwargs.pop("_schema", None)

        if not args and _schema is not None:
            args = [_schema]

        super().__init__(*args, **kwargs)


class _JsonEncoder(json.JSONEncoder):
    @typing.override
    def default(self, o: typing.Any) -> typing.Any:
        f = getattr(o, "__json__", None)
        if f and callable(f):
            return f()
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
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
    _FIELDS: typing.Final[dict[str, Field]] = {
        "char_pos": Field(Protoform(Int)),
        "chunk_eid": Field(Protoform(Int, -1), required=False),
        "chunk_pos": Field(Protoform(Int, -1), required=False),
    }

    @typing.override
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        args = list(args)
        kwargs = dict(kwargs)

        if args == [None]:
            args = []

        if kwargs.get("_schema") is None:
            kwargs.pop("_schema", None)

        assert "_schema" not in kwargs, "invalid argument"
        super().__init__(*args, _schema=self._FIELDS, **kwargs)

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        s = read_utf8str(cursor)
        split = s.split(":", 2)
        if len(split) > 1:
            b = base64.b64decode(split[0])
            version = b[0]
            if version == result._MAGIC_CHUNK_V1:
                result["chunk_eid"] = int.from_bytes(b[1:5], "little")
                result["chunk_pos"] = int.from_bytes(b[5:9], "little")
            else:
                # TODO throw a proper exception
                raise Exception(
                    "Unrecognized position version 0x%02x" % version
                )
            result["char_pos"] = int(split[1])
        else:
            result["char_pos"] = int(s)
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        s = ""
        if self["chunk_eid"] >= 0 and self["chunk_pos"] >= 0:
            b_version = self._MAGIC_CHUNK_V1.to_bytes(
                1, "little", signed=False
            )
            b_eid = self["chunk_eid"].to_bytes(4, "little", signed=False)
            b_pos = self["chunk_pos"].to_bytes(4, "little", signed=False)
            s += base64.b64encode(b_version + b_eid + b_pos).decode("ascii")
            s += ":"
        s += str(
            int(self["char_pos"])
            if self["char_pos"] is not None and self["char_pos"] >= 0
            else -1
        )
        write_utf8str(cursor, s)


class LPR(_TypedDict, Serializable):  # aka LPR
    _MAGIC_V2: typing.Final[int] = 2
    _FIELDS: typing.Final[dict[str, Field]] = {
        "pos": Field(Protoform(Position)),
        "timestamp": Field(Protoform(Int, -1), required=False),
        "lpr_version": Field(Protoform(Int, -1), required=False),
    }

    @typing.override
    def __init__(self, *args, **kwargs):
        args = list(args)
        kwargs = dict(kwargs)

        if args == [None]:
            args = []

        if kwargs.get("_schema") is None:
            kwargs.pop("_schema", None)

        assert "_schema" not in kwargs, "invalid argument"
        super().__init__(*args, _schema=self._FIELDS, **kwargs)

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        init = {}

        type_byte = cursor.peek()
        if type_byte == Utf8Str.magic_byte:
            # old LPR version'
            init["pos"] = _read_object(cursor, Position)
        elif type_byte == Byte.magic_byte:
            # new LPR version
            init["lpr_version"] = read_byte(cursor)
            init["pos"] = _read_object(cursor, Position)
            init["timestamp"] = int(read_long(cursor))
        else:
            raise UnexpectedBytesError(
                cursor.tell(),
                [Utf8Str.magic_byte, Byte.magic_byte],
                type_byte,
            )

        return cls(*args, **init, **kwargs)

    @typing.override
    def _write(self, cursor: Cursor):
        # XXX may cause problems if kindle expects the original LPR format
        #   version when datastore file is re-written
        if self["timestamp"] < 0:
            # old LPR version
            _write_object(cursor, self["pos"])
        else:
            # new LPR version
            lpr_version = max(self._MAGIC_V2, self["lpr_version"])
            write_byte(cursor, lpr_version)
            _write_object(cursor, self["pos"])
            write_long(cursor, self["timestamp"])


class TimeZoneOffset(IntBase, Serializable):
    @typing.override
    def __new__(
        cls,
        *args,
        _schema: None | int = None,
        **kwargs,
    ) -> TimeZoneOffset:
        if not args and _schema is not None:
            args = [_schema]
        assert "_schema" not in kwargs, "invalid argument"
        return super().__new__(cls, *args, **kwargs)

    # noinspection PyUnusedLocal
    @typing.override
    def __init__(self, *args, **kwargs):
        super().__init__()

    @classmethod
    @typing.override
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

    def __json__(
        self,
    ) -> None | bool | int | float | str | tuple | list | dict:
        return int(self)


# can contain Bool, Char, Byte, Short, Int, Long, Float, Double,
#   Utf8Str, Object
class ObjectMap(_TypedDict, Serializable):
    _MAGIC_STR: typing.Final[bytes] = b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
    _FIXED_MYSTERY_NUM: typing.Final[int] = (
        1  # present after the signature; unknown what this number means
    )

    def __init__(self, *args, _schema: Mapping, **kwargs):
        schema = copy.deepcopy(_schema)
        _fix_mapping(schema, False)

        self.__key_to_field: Mapping = schema
        # super constructor last so hooks work correctly
        super().__init__(*args, _schema=schema, **kwargs)

    @classmethod
    def _schema(cls, mapping: dict[str, type | Field]) -> Mapping:
        result = copy.deepcopy(mapping)
        _fix_mapping(result, False)
        return result

    @classmethod
    def __eat_signature_or_error(cls, cursor: Cursor):
        if not cursor.eat(cls._MAGIC_STR):
            raise UnexpectedBytesError(
                cursor.tell(),
                cls._MAGIC_STR,
                cursor.peek(len(cls._MAGIC_STR)),
            )

    @classmethod
    def __eat_fixed_mystery_num_or_error(cls, cursor: Cursor):
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
    def __peek_object_schema_id(
        cls,
        csr: Cursor,
        magic_byte: bool = True,
    ) -> None | str:
        schema_id = None
        csr.save()
        if not magic_byte or csr.eat(OBJECT_BEGIN):
            schema_id = read_utf8str(csr, False)
        csr.restore()
        return schema_id

    @classmethod
    def __read_object(
        cls,
        csr: Cursor,
        cls_: type,
        schema: typing.Any | None = None,
        schema_id: None | str = None,
    ) -> tuple[typing.Any, str]:
        assert (
            schema_id is None or schema_id
        ), "expected either null or non-empty schema"
        schema_id_actual = cls.__peek_object_schema_id(csr)
        if not schema_id_actual:
            raise UnexpectedStructureError(
                "Failed to read schema for object."
            )
        if schema_id is not None and schema_id_actual != schema_id:
            raise UnexpectedStructureError(
                f'Object schema "{schema_id_actual}"'
                + f' does not match expected schema "{schema_id}"'
            )
        o = _read_object(csr, cls_, schema, schema_id_actual)
        return o, schema_id_actual

    @classmethod
    def __write_object(
        cls,
        csr: Cursor,
        o: typing.Any,
        schema_id: str,
    ):
        assert schema_id, "expected non-empty schema"
        csr.write(OBJECT_BEGIN)
        write_utf8str(csr, schema_id, False)
        # noinspection PyProtectedMember
        o._write(csr)
        csr.write(OBJECT_END)

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        result = cls(*args, **kwargs)
        result.__eat_signature_or_error(cursor)
        result.__eat_fixed_mystery_num_or_error(cursor)

        size = read_int(cursor)
        for _ in range(size):
            schema_id = cls.__peek_object_schema_id(cursor)
            schema = result.__key_to_field[schema_id]
            value, schema_id_actual = result.__read_object(
                cursor,
                schema.proto.cls_,
                schema.proto.schema,
                schema_id,
            )
            assert schema_id_actual, "Object has blank schema."
            result[schema_id_actual] = value
        return result

    @typing.override
    def _write(self, cursor: Cursor):
        cursor.write(self._MAGIC_STR)
        write_long(cursor, self._FIXED_MYSTERY_NUM)
        write_int(cursor, len(self))
        for schema_id, value in self.items():
            self.__write_object(cursor, value, schema_id)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{dict(self)}"


# @formatter:off
# fmt: off
# autopep8: off
# yapf: disable

# noinspection PyProtectedMember
_timer_average_calculator_outliers = Array._schema(Double)
# noinspection PyProtectedMember
_timer_average_calculator_distribution_normal = Record._schema({
    "count": Long,
    "sum": Double,
    "sum_of_squares": Double,
})

# noinspection PyProtectedMember
_timer_average_calculator = Record._schema({
    "samples1": Field(Protoform(Array, Array._schema(Double))),
    "samples2": Field(Protoform(Array, Array._schema(Double))),
    "normal_distributions": Field(Protoform(Array, Array._schema(
        Record,
        _timer_average_calculator_distribution_normal,
        "timer.average.calculator.distribution.normal",
    ))),
    "outliers": Field(Protoform(Array, Array._schema(
        Array,
        _timer_average_calculator_outliers,
        "timer.average.calculator.outliers",
    ))),
})

# noinspection PyProtectedMember
_timer_model = Record._schema({
    "version": Long,
    "total_time": Long,
    "total_words": Long,
    "total_percent": Double,
    "average_calculator": Field(
        Protoform(Record, _timer_average_calculator),
        "timer.average.calculator",
    ),
})

# noinspection PyProtectedMember
_font_prefs = Record._schema({
    "typeface": Utf8Str,
    "line_sp": Int,
    "size": Int,
    "align": Int,
    "inset_top": Int,
    "inset_left": Int,
    "inset_bottom": Int,
    "inset_right": Int,
    "unknown1": Int,
    "bold": Field(Protoform(Int), required=False),
    "user_sideloadable_font": Field(Protoform(Utf8Str), required=False),
    "custom_font_index": Field(Protoform(Int), required=False),
    "mobi7_system_font": Field(Protoform(Utf8Str), required=False),
    "mobi7_restore_font": Field(Protoform(Bool), required=False),
    "reading_preset_selected": Field(Protoform(Utf8Str), required=False),
})

# noinspection PyProtectedMember
_reader_state_preferences = Record._schema({
    "font_preferences": Field(Protoform(Record, _font_prefs)),
    "left_margin": Int,
    "right_margin": Int,
    "top_margin": Int,
    "bottom_margin": Int,
    "unknown1": Bool,
})

# noinspection PyProtectedMember
_annotation_personal_element = Record._schema({
    "start_pos": Position,
    "end_pos": Position,
    "creation_time": DateTime,
    "last_modification_time": DateTime,
    "template": Utf8Str,
    "note": Field(Protoform(Utf8Str), required=False),
})

# noinspection PyProtectedMember
_annotation_cache_object = IntMap._schema({
    "bookmarks": Field(
        Protoform(Array, Array._schema(
            Record,
            _annotation_personal_element,
            "annotation.personal.bookmark",
        )),
        "saved.avl.interval.tree",
    ),
    "highlights": Field(
        Protoform(Array, Array._schema(
            Record,
            _annotation_personal_element,
            "annotation.personal.highlight",
        )),
        "saved.avl.interval.tree",
    ),
    "notes": Field(
        Protoform(Array, Array._schema(
            Record,
            _annotation_personal_element,
            "annotation.personal.note",
        )),
        "saved.avl.interval.tree",
    ),
    "clip_articles": Field(
        Protoform(Array, Array._schema(
            Record,
            _annotation_personal_element,
            "annotation.personal.clip_article",
        )),
        "saved.avl.interval.tree",
    ),
})

# noinspection PyProtectedMember
# NOTE if you update this schema map update the type hints too
_store_key_to_field: \
dict[str, type | NotImplemented | Field] \
= ObjectMap._schema({  # noqa
    "clock.data.store": NotImplemented,
    "dictionary": Utf8Str,
    "lpu": NotImplemented,
    "pdf.contrast": NotImplemented,
    "sync_lpr": Bool,
    "tpz.line.spacing": NotImplemented,
    "XRAY_OTA_UPDATE_STATE": NotImplemented,
    "XRAY_SHOWING_SPOILERS": NotImplemented,
    "XRAY_SORTING_STATE": NotImplemented,
    "XRAY_TAB_STATE": NotImplemented,
    "dict.prefs.v2": DynamicMap,
    "EndActions": DynamicMap,
    "ReaderMetrics": DynamicMap,
    "StartActions": DynamicMap,
    "Translator": DynamicMap,
    "Wikipedia": DynamicMap,
    "buy.asin.response.data": Json,
    "next.in.series.info.data": Json,
    "price.info.data": Json,
    "erl": Position,
    "lpr": LPR,
    "fpr": Field(Protoform(Record, Record._schema({
        "pos": Position,
        "timestamp": Field(Protoform(DateTime), required=False),
        "timezone_offset": Field(Protoform(TimeZoneOffset), required=False),
        "country": Field(Protoform(Utf8Str), required=False),
        "device": Field(Protoform(Utf8Str), required=False),
    }))),
    "updated_lpr": Field(Protoform(Record, Record._schema({
        "pos": Position,
        "timestamp": Field(Protoform(DateTime), required=False),
        "timezone_offset": Field(Protoform(TimeZoneOffset), required=False),
        "country": Field(Protoform(Utf8Str), required=False),
        "device": Field(Protoform(Utf8Str), required=False),
    }))),
    # amzn page num xref (i.e. page num map)
    "apnx.key": Field(Protoform(Record, Record._schema({
        "asin": Utf8Str,
        "cde_type": Utf8Str,
        "sidecar_available": Bool,
        "opn_to_pos": Field(Protoform(Array, Array._schema(Int))),
        "first": Int,
        "unknown1": Int,
        "unknown2": Int,
        "page_map": Utf8Str,
    }))),
    "fixed.layout.data": Field(Protoform(Record, Record._schema({
        "unknown1": Bool,
        "unknown2": Bool,
        "unknown3": Bool,
    }))),
    "sharing.limits": Field(Protoform(Record, Record._schema({
        # TODO discover structure for sharing.limits
        "accumulated": NotImplemented
    }))),
    "language.store": Field(Protoform(Record, Record._schema({
        "language": Utf8Str,
        "unknown1": Int,
    }))),
    "periodicals.view.state": Field(Protoform(Record, Record._schema({
        "unknown1": Utf8Str,
        "unknown2": Int,
    }))),
    "purchase.state.data": Field(Protoform(Record, Record._schema({
        "state": Int,
        "time": DateTime,
    }))),
    "timer.model": Field(Protoform(Record, _timer_model)),
    "timer.data.store": Field(Protoform(Record, Record._schema({
        "on": Bool,
        "reading_timer_model": Field(Protoform(Record, _timer_model)),
        "version": Int,
    }))),
    "timer.data.store.v2": Field(Protoform(Record, Record._schema({
        "on": Bool,
        "reading_timer_model": Field(Protoform(Record, _timer_model)),
        "version": Int,
        "last_option": Int,
    }))),
    "book.info.store": Field(Protoform(Record, Record._schema({
        "num_words": Long,
        "percent_of_book": Double,
    }))),
    "page.history.store": Field(Protoform(Array, Array._schema(
        Record,
        Record._schema({"pos": Position, "time": DateTime}),
        "page.history.record",
    ))),
    "reader.state.preferences": Field(
        Protoform(Record, _reader_state_preferences)),
    "font.prefs": Field(
        Protoform(Record, _font_prefs)),
    "annotation.cache.object": Field(
        Protoform(IntMap, _annotation_cache_object)),
    "annotation.personal.bookmark": Field(
        Protoform(Record, _annotation_personal_element)),
    "annotation.personal.highlight": Field(
        Protoform(Record, _annotation_personal_element)),
    "annotation.personal.note": Field(
        Protoform(Record, _annotation_personal_element)),
    "annotation.personal.clip_article": Field(
        Protoform(Record, _annotation_personal_element)),
    "whisperstore.migration.status": Field(
        Protoform(Record, Record._schema({
        "unknown1": Bool,
        "unknown2": Bool,
    }))),
    "timer.average.calculator.distribution.normal": Field(
        Protoform(Record, _timer_average_calculator_distribution_normal)),
    "timer.average.calculator.outliers": Field(
        Protoform(Array, _timer_average_calculator_outliers),
    ),
})

# autopep8: on
# yapf: enable
# fmt: on
# @formatter:on


class Store(ObjectMap):
    @typing.override
    def __init__(self, *args, **kwargs):
        assert kwargs.get("_schema") is None, "invalid argument"
        super().__init__(
            *args,
            _schema=_store_key_to_field,
            **kwargs,
        )

    @classmethod
    @typing.override
    def _create(cls, cursor: Cursor, *args, **kwargs) -> typing.Self:
        assert kwargs.get("_schema") is None, "invalid argument"
        return super()._create(
            cursor,
            *args,
            **kwargs,
        )


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
    ObjectMap,
)
