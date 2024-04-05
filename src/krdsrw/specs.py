import copy
import dataclasses
import inspect
import typing

from .basics import read_utf8str
from .basics import write_utf8str
from .cursor import Cursor
from .cursor import Serializable
from .error import UnexpectedBytesError
from .error import UnexpectedStructureError

T = typing.TypeVar("T", bound=typing.Any)


def _flatten(o: typing.Any) -> list[typing.Any]:
    def recurse(o: typing.Any, master: list[typing.Any]):
        if isinstance(o, (tuple, list)):
            for e in o:
                recurse(e, master)
            return
        master.append(o)

    result = []
    recurse(o, result)
    return result


@dataclasses.dataclass
class Field:
    key: None | type | str | typing.Literal['*'] | typing.Any \
        | tuple[None | type | str | typing.Literal['*'] | typing.Any, ...] \
        | list[None | type | str | typing.Literal['*'] | typing.Any]
    value: None | type | typing.Literal['*'] | typing.Any \
        | tuple[None | type | typing.Literal['*'] | typing.Any, ...] \
        | list[None | type | typing.Literal['*'] | typing.Any]
    is_readable: bool = True
    is_writable: bool = True
    is_deletable: bool = True


@dataclasses.dataclass
class Index:
    value: None | type | typing.Literal['*'] | typing.Any \
        | tuple[None | type | typing.Literal['*'] | typing.Any, ...] \
        | list[None | type | typing.Literal['*'] | typing.Any]


class Spec(typing.Generic[T]):
    # named object data structure (schema utf8str + data)
    _OBJECT_BEGIN: typing.Final[int] = 0xfe
    # end of data for object
    _OBJECT_END: typing.Final[int] = 0xff

    def __init__(
        self,
        cls_: type[T],
        default: None | typing.Any \
        | tuple[typing.Any, ...] | list[typing.Any] = None,
        schema: None | dict[typing.Any, typing.Any] = None,
        indexes: None | list[Index] | list[Field] | list[Index | Field] = None,
    ):
        super().__init__()

        self._cls: typing.Final[type[T]] = cls_
        self._init_default: list[typing.Any] = _flatten(default or [])
        self._init_schema: dict[typing.Any, typing.Any] = schema or {}
        self._indexes: list[Index | Field] \
            = copy.deepcopy(indexes or [])  # type: ignore

    @property
    def cls_(self) -> type[T]:
        return self._cls

    @property
    def indexes(self) -> list[Index | Field]:
        return list(self._indexes)

    def read(self, cursor: Cursor, schema: None | str = None) -> T:
        result = None

        if schema:
            if not cursor.eat(self._OBJECT_BEGIN):
                raise UnexpectedBytesError(
                    cursor.tell(), self._OBJECT_BEGIN, cursor.peek())

            schema_ = read_utf8str(cursor, False)
            if not schema_:
                raise UnexpectedStructureError('Object has blank schema.')
            if schema_ != schema:
                raise UnexpectedStructureError(
                    f"Expected object schema \"{schema}\""
                    + f" but got \"{schema_}\".")

        result = self._cls._create(cursor, **self._init_schema)

        if schema and not cursor.eat(self._OBJECT_END):
            raise UnexpectedBytesError(
                cursor.tell(), self._OBJECT_END, cursor.peek())

        assert result is not None, 'Failed to create object'
        return result  # type: ignore

    def make(self, *args, **kwargs) -> T:
        if not args and not kwargs:
            return self._cls(*self._init_default, **self._init_schema)
        return self._cls(*args, **kwargs, **self._init_schema)

    def write(self, cursor: Cursor, o: T, schema: None | str = None):
        if schema:
            cursor.write(self._OBJECT_BEGIN)
            write_utf8str(cursor, schema, False)
        o._write(cursor)
        if schema:
            cursor.write(self._OBJECT_END)

    @typing.override
    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls \
            and self._init_default == o._init_default \
            and self._init_schema == o._init_schema
        return super().__eq__(o)

    def is_compatible(self, o: type | typing.Any) -> bool:
        if (inspect.isclass(o) and issubclass(o, self._cls)) \
        or (not inspect.isclass(o) and isinstance(o, self._cls)):
            return True

        for t in [ bool, int, float, str, bytes, list, tuple, dict ]:
            if issubclass(self._cls, t) \
            and ((inspect.isclass(o) and issubclass(o, t)) \
                or (not inspect.isclass(o) and isinstance(o, t))):
                return True

        return False
