import copy
import dataclasses
import inspect
import typing

from .basics import read_utf8str
from .basics import write_utf8str
from .cursor import Cursor
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
        args: None | typing.Any | tuple[typing.Any, ...]
        | list[typing.Any] = None,
        kwargs: None | dict[typing.Any, typing.Any] = None,
        indexes: None | list[Index] | list[Field] | list[Index | Field] = None,
    ):
        super().__init__()

        self._cls: typing.Final[type[T]] = cls_
        self._init_args: list[typing.Any] = _flatten(args or [])
        self._init_kwargs: dict[typing.Any, typing.Any] = kwargs or {}
        self._indexes: list[Index | Field] \
            = copy.deepcopy(indexes or [])  # type: ignore

    @property
    def cls_(self) -> type[T]:
        return self._cls

    @property
    def indexes(self) -> list[Index | Field]:
        return list(self._indexes)

    def read(self, cursor: Cursor, name: None | str = None) -> T:
        from .objects import Object
        o = None

        if name:
            if not cursor.eat(self._OBJECT_BEGIN):
                raise UnexpectedBytesError(
                    cursor.tell(), self._OBJECT_BEGIN, cursor.peek())

            name_ = read_utf8str(cursor, False)
            if not name_:
                raise UnexpectedStructureError('Object has blank name.')
            if name_ != name:
                raise UnexpectedStructureError(
                    f"Expected object name \"{name}\""
                    + f" but got \"{name_}\".")

        if hasattr(self._cls, 'create'):
            o = self._cls.create(cursor, *self._init_args, **self._init_kwargs)
        elif issubclass(self._cls, Object):
            o = self._cls(*self._init_args, **self._init_kwargs)
            o.read(cursor)

        if name and not cursor.eat(self._OBJECT_END):
            raise UnexpectedBytesError(
                cursor.tell(), self._OBJECT_END, cursor.peek())

        assert o is not None, 'Failed to create object'
        return o  # type: ignore

    def make(self, *args, **kwargs) -> T:
        return self._cls(
            *self._init_args,
            *args,
            **self._init_kwargs,
            **kwargs,
        )

    def write(self, cursor: Cursor, o: T, name: None | str = None):
        if name:
            cursor.write(self._OBJECT_BEGIN)
            write_utf8str(cursor, name, False)
        o.write(cursor)
        if name:
            cursor.write(self._OBJECT_END)

    @typing.override
    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls \
            and self._init_args == o._init_args \
            and self._init_kwargs == o._init_kwargs
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
