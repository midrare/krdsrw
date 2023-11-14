import abc
import collections
import typing

from .cursor import Cursor
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


T = typing.TypeVar("T", bound=Byte | Char | Bool | Short | Int | Long \
    | Float | Double | Utf8Str | Value)


class Value(metaclass=abc.ABCMeta):
    def __init__(self, _name: None | str = None):
        super().__init__()
        self._name: str = _name or ''

    @abc.abstractmethod
    def read(self, cursor: Cursor):
        raise NotImplementedError(
            "This method must be implemented by the subclass."
        )

    @abc.abstractmethod
    def write(self, cursor: Cursor):
        raise NotImplementedError(
            "This method must be implemented by the subclass."
        )

    @abc.abstractmethod
    def __eq__(self, other: Value) -> bool:
        raise NotImplementedError(
            "This method must be implemented by the subclass."
        )

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{{self._name}}}"


class ValFactory(typing.Generic[T]):
    def __init__(self, cls_: type[T], *args, **kwargs):
        super().__init__()

        if not any(issubclass(cls_, c) for c in ALL_BASIC_TYPES) \
        and issubclass(cls_, Value):
            raise TypeError(f"Unsupported type \"{type(cls_).__name__}\".")

        self._cls: typing.Final[type[T]] = cls_
        self._args: typing.Final[list] = list(args)
        self._kwargs: typing.Final[dict] = collections.OrderedDict(kwargs)

    @property
    def cls_(self) -> type[T]:
        return self._cls

    def create(self) -> T:
        return self._cls(*self._args, **self._kwargs)

    def read_from(self, cursor: Cursor) -> T:
        if issubclass(self._cls, Basic):
            return cursor.read_auto(self._cls)  # type: ignore
        assert issubclass(self._cls, Value), 'class is not subclass of Value'
        val = self._cls(*self._args, **self._kwargs)
        val.read(cursor)
        return val

    def is_basic(self) -> bool:
        return issubclass(self._cls, Basic)

    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return self._cls == o._cls and self._args == o._args \
            and self._kwargs == o._kwargs
        return super().__eq__(o)
