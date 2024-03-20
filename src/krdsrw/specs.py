import inspect
import typing

from .cursor import Cursor
from .error import UnexpectedBytesError
from .error import UnexpectedStructureError

T = typing.TypeVar("T", bound=typing.Any)


class Spec(typing.Generic[T]):
    # named object data structure (schema utf8str + data)
    _OBJECT_BEGIN: typing.Final[int] = 0xfe
    # end of data for object
    _OBJECT_END: typing.Final[int] = 0xff

    def __init__(self, cls_: type[T], *args, **kwargs):
        super().__init__()

        self._cls: typing.Final[type[T]] = cls_
        self._args: typing.Final[list] = list(args)
        self._kwargs: typing.Final[dict] = dict(kwargs)

    @property
    def cls_(self) -> type[T]:
        return self._cls

    def read(self, cursor: Cursor, name: None | str = None) -> T:
        from .objects import Object
        o = None

        if name:
            if not cursor.eat(self._OBJECT_BEGIN):
                raise UnexpectedBytesError(
                    cursor.tell(), self._OBJECT_BEGIN, cursor.peek())

            name_ = cursor.read_utf8str(False)
            if not name_:
                raise UnexpectedStructureError('Object has blank name.')
            if name_ != name:
                raise UnexpectedStructureError(
                    f"Expected object name \"{name}\""
                    + f" but got \"{name_}\".")

        if hasattr(self._cls, 'create'):
            o = self._cls.create(cursor, *self._args, **self._kwargs)
        elif issubclass(self._cls, Object):
            o = self._cls(*self._args, **self._kwargs)
            o.read(cursor)

        if name and not cursor.eat(self._OBJECT_END):
            raise UnexpectedBytesError(
                cursor.tell(), self._OBJECT_END, cursor.peek())

        assert o is not None, 'Failed to create object'
        return o

    def make(self) -> T:
        return self._cls(*self._args, **self._kwargs)

    def write(self, cursor: Cursor, o: T, name: None | str = None):
        if name:
            cursor.write(self._OBJECT_BEGIN)
            cursor.write_utf8str(name, False)
        o.write(cursor)
        if name:
            cursor.write(self._OBJECT_END)

    @typing.override
    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls \
            and self._args == o._args \
            and self._kwargs == o._kwargs
        return super().__eq__(o)

    def is_compatible(self, o: type | typing.Any) -> bool:
        if inspect.isclass(o):
            return issubclass(o, self._cls) \
            or ((builtin := getattr(self._cls, 'builtin')) \
            and inspect.isclass(builtin) and issubclass(o, builtin))
        return isinstance(o, self._cls) \
        or ((builtin := getattr(self._cls, 'builtin')) \
        and inspect.isclass(builtin) and isinstance(o, builtin))

    def cast(self, o: typing.Any) -> T:
        if issubclass(self._cls, list):
            o2 = self._cls(*self._args, **self._kwargs)
            o2.extend(o)
            return o2

        if issubclass(self._cls, dict):
            o2 = self._cls(*self._args, **self._kwargs)
            o2.update(o)
            return o2

        return self._cls(o, *self._args, **self._kwargs)
