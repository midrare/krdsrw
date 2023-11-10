from __future__ import annotations
import collections
import typing

from . import datastore

T = typing.TypeVar("T")


class WrappedList(collections.UserList[T]):
    def __init__(
        self,
        cls: typing.Type[T],
        array: datastore.Array,
        unwrap: typing.Callable[T,
                                datastore.Value],
        wrap: typing.Callable[datastore.Value,
                              T],
    ):
        super().__init__()

        self._cls: typing.Type[T] = cls
        self._array: datastore.Array = array
        self._wrap: typing.Callable[datastore.Value, T] = wrap
        self._unwrap: typing.Callable[T, datastore.Value] = unwrap

        self.data[:] = [wrap(v) for v in array.value]

    def clear(self):
        self.data.clear()
        self._array.value.clear()

    def copy(self) -> typing.List[T]:
        return self._copy()

    def append(self, obj: T):
        if not isinstance(obj, self._cls):
            raise TypeError(f"value is not of type {self._cls.__name__}")

        self.data.append(obj)
        self._array.value.append(self._unwrap(obj))

    def extend(self, it: typing.Iterable[T]):
        objs = list(it)
        if any(not isinstance(o, self._cls) for o in objs):
            raise TypeError(
                f"one or more value(s) is not of type {self._cls.__name__}"
            )

        self.data.extend(objs)
        self._array.value.extend(self._unwrap(o) for o in objs)

    def pop(self, index: typing.SupportsIndex = ...) -> T:
        self._array.value.pop(index)
        return self.data.pop(index)

    def insert(self, index: typing.SupportsIndex, obj: T):
        if not isinstance(obj, self._cls):
            raise TypeError(f"value is not of type {self._cls.__name__}")
        self.data.insert(index, obj)
        self._array.value.insert(index, self._unwrap(obj))

    def remove(self, value: T):
        if not isinstance(value, self._cls):
            raise TypeError(f"value is not of type {self._cls.__name__}")
        idx = self.data.index(value)
        self.data.pop(idx)
        self._array.value.pop(idx)

    def sort(self, *, key: None = ..., reverse: bool = ...):
        zipped = list(zip(self.data, self._array.value))
        zipped.sort(key=lambda t: t[0], reverse=reverse)
        self.data[:] = [t[0] for t in zipped]
        self._array.value[:] = [t[1] for t in zipped]

    def _copy(self):
        copy = WrappedList(
            datastore.Array(self._array.template),
            self._wrap,
            self._unwrap
        )
        copy.data[:] = self.data
        copy._array.value[:] = self._array.value
        return copy

    def __setitem__(self, i: int | slice, o: T | typing.Iterable[T]):
        if isinstance(i, slice):
            if any(not isinstance(x, self._cls) for x in o):
                raise TypeError(
                    f"one or more value(s) is not of type {self._cls.__name__}"
                )
        else:
            if not isinstance(o, self._cls):
                raise TypeError(f"value is not of type {self._cls.__name__}")

        if isinstance(i, slice):
            self.data[i] = o
            self._array.value[i] = [self._unwrap(e) for e in o]
        else:
            self.data[i] = o
            self._array.value[i] = self._unwrap(o)

    def __delitem__(self, i: int | slice):
        del self.data[i]
        del self._array.value[i]

    def __add__(self, x: list[T]) -> WrappedList[T]:
        values = list(x)
        if any(not isinstance(o, self._cls) for o in values):
            raise TypeError(
                f"one or more value(s) is not of type {self._cls.__name__}"
            )

        copy = self._copy()
        copy.data.extend(values)
        copy._array.value.extend(self._unwrap(o) for o in values)
        return copy

    def __iadd__(self, x: typing.Iterable[T]):
        objs = list(x)
        if any(not isinstance(o, self._cls) for o in objs):
            raise TypeError(
                f"one or more value(s) is not of type {self._cls.__name__}"
            )
        self.data.extend(objs)
        self._array.value.extend(self._unwrap(o) for o in objs)

    def __mul__(self, n: int | slice) -> WrappedList[T]:
        copy = self._copy()
        copy.data *= n
        copy._array.value *= n
        return copy

    def __rmul__(self, n: int | slice) -> WrappedList[T]:
        return self.__mul__(n)

    def __imul__(self, n: typing.SupportsIndex):
        self.data *= n
        self._array.value *= n

    def index(
        self,
        value: T,
        start: int | slice = ...,
        stop: int | slice = ...
    ) -> int:
        if not isinstance(value, self._cls):
            raise TypeError(f"value is not of type {self._cls.__name__}")

        return self.data.index(value, start, stop)

    def count(self, value: T) -> int:
        if not isinstance(value, self._cls):
            raise TypeError(f"value is not of type {self._cls.__name__}")
        return self.data.count(value)

    def reverse(self):
        self.data.reverse()
        self._array.value.reverse()

    def __len__(self) -> int:
        return len(self._array.value)

    def __iter__(self) -> typing.Iterator[T]:
        return self.data.__iter__()

    def __str__(self) -> str:
        return super().__str__()

    def __getitem__(self, idx: int | slice) -> T:
        return self.data[idx]

    def __contains__(self, o: object) -> bool:
        if not isinstance(o, self._cls):
            raise TypeError(f"value is not of type {self._cls.__name__}")
        return o in self.data

    def __reversed__(self) -> typing.Iterator[T]:
        copy = self._copy()
        copy.data.reverse()
        copy._array.value.reverse()
        return copy

    def __gt__(self, x: list[T]) -> bool:
        return self.data > x

    def __ge__(self, x: list[T]) -> bool:
        return self.data >= x

    def __lt__(self, x: list[T]) -> bool:
        return self.data < x

    def __le__(self, x: list[T]) -> bool:
        return self.data <= x

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return (
                self._array == o._array and self.data == o.data
                and self._wrap == o._wrap and self._unwrap == o._unwrap
            )
        return super().__eq__(o)
