import collections.abc
import copy
import typing

K = typing.TypeVar("K", bound=int | float | str)
T = typing.TypeVar("T", bound=typing.Any)


class StrictList(list[T]):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self[:] = list(*args, **kwargs)

    def _pre_write_filter(self, value: typing.Any) -> bool:
        return True

    def _pre_write_transform(self, value: typing.Any) -> T:
        return value

    def _post_write_hook(self):
        pass

    @typing.overload
    def __setitem__(
        self,
        i: typing.SupportsIndex,
        o: int | float | str | T,
    ):
        ...

    @typing.overload
    def __setitem__(
        self,
        i: slice,
        o: typing.Iterable[int | float | str | T],
    ):
        ...

    @typing.override
    def __setitem__(
        self,
        i: typing.SupportsIndex | slice,
        o: bool | int | float | str | bytes | T | \
        typing.Iterable[bool | int | float | str | bytes | T],
    ):
        if isinstance(i, slice):
            assert isinstance(o, collections.abc.Iterable),\
                'when index is slice the value must be iterable'

            o = list(o)
            for e in o:
                if not self._pre_write_filter(e):
                    raise TypeError(f"Value \"{e}\" is not allowed.")

            super().__setitem__(
                i, list(self._pre_write_transform(e) for e in o))
        else:
            if not self._pre_write_filter(o):
                raise TypeError(f"Value \"{o}\" is not allowed.")

            super().__setitem__(i, self._pre_write_transform(o))

        self._post_write_hook()

    @typing.override
    def __add__(  # type: ignore
        self,
        other: typing.Sequence[int | float | str | T],
    ) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._pre_write_filter(e):
                raise TypeError(f"Value \"{e}\" is not allowed.")

        result = self.copy()
        super(result.__class__, result).extend(\
            self._pre_write_transform(e) for e in other)
        return result

    @typing.override
    def __iadd__(
        self,
        other: typing.Iterable[int | float | str | T],
    ) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._pre_write_filter(e):
                raise TypeError(f"Value \"{e}\" is not allowed.")

        result = super().__iadd__(self._pre_write_transform(e) for e in other)
        self._post_write_hook()

        return result

    @typing.override
    def append(self, o: int | float | str | T):
        if not self._pre_write_filter(o):
            raise TypeError(f"Value \"{o}\" is not allowed.")

        super().append(self._pre_write_transform(o))
        self._post_write_hook()

    @typing.override
    def insert(self, i: typing.SupportsIndex, o: int | float | str | T):
        if not self._pre_write_filter(o):
            raise TypeError(f"Value \"{o}\" is not allowed.")

        super().insert(i, self._pre_write_transform(o))
        self._post_write_hook()

    @typing.override
    def copy(self) -> typing.Self:
        return copy.copy(self)

    @typing.override
    def extend(self, other: typing.Iterable[int | float | str | T]):
        other = list(other)
        for e in other:
            if not self._pre_write_filter(e):
                raise TypeError(f"Value \"{e}\" is not allowed.")

        super().extend(self._pre_write_transform(e) for e in other)
        self._post_write_hook()

    @typing.override
    def count(self, o: bool | int | float | str | bytes | T) -> int:
        return super().count(o)  # type: ignore

    @typing.override
    def pop(self, idx: typing.SupportsIndex = -1) -> T:
        result = super().pop(idx)
        self._post_write_hook()
        return result

    @typing.override
    def remove(self, value: T):
        super().remove(value)
        self._post_write_hook()

    @typing.override
    def clear(self):
        super().clear()
        self._post_write_hook()


class StrictDict(dict[K, T]):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.update(dict(*args, **kwargs))

    def _key(self, key: typing.Any) -> K:
        return key

    def _key_value(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[K, T]:
        return key, value

    def _allow_read(self, key: typing.Any) -> bool:
        return True

    def _allow_write(self, key: typing.Any, value: typing.Any) -> bool:
        return True

    def _allow_del(self, key: typing.Any) -> bool:
        return True

    def _on_modified(self):
        pass

    @typing.override
    @classmethod
    def fromkeys(  # type: ignore
        cls,
        iterable: typing.Iterable[K],
        value: None | T = None,
    ) -> typing.Self:
        o = cls()
        o.update(dict((k, value) for k in iterable))  # type: ignore
        return o

    @typing.override
    def setdefault(self, key: K, default: None | T = None) -> T:
        key_ = self._key(key)
        if super().__contains__(key_):
            if not self._allow_read(key_):
                raise TypeError(\
                    f"Reading key \"{key}\" is not allowed.")

            key_, value = self._key_value(key, default)
            return super().setdefault(key_, value)  # type: ignore

        key_, value = self._key_value(key, default)
        if not self._allow_write(key_, value):
            raise TypeError(
                f"Writing key \"{key}\" "
                + f"with value \"{default}\" is not allowed.")

        result = super().setdefault(key_, value)  # type: ignore
        self._on_modified()

        return result

    @typing.override
    def update( # type: ignore
        self,
        *args: typing.Mapping[K, T],
        **kwargs: T,
    ):
        transformed = {}  # deliberate plain dict
        for key, value in dict(*args, **kwargs).items():
            key_, value_ = self._key_value(key, value)\

            if not self._allow_write(key_, value_):
                raise TypeError(
                    f"Writing to key \"{key}\" "
                    + f"with value \"{value}\" is not allowed.")

            transformed[key_] = value_

        super().update(transformed)
        if transformed:
            self._on_modified()

    @typing.override
    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return dict(o) == dict(self)
        return super().__eq__(o)

    @typing.override
    def __contains__(self, key: typing.Any) -> bool:
        key = self._key(key)
        return super().__contains__(key)

    @typing.override
    def __delitem__(self, key: K):
        key_ = self._key(key)
        if not self._allow_del(key_):
            raise KeyError(f"Key \"{key}\" cannot be deleted.")

        is_contained = super().__contains__(key_)
        super().__delitem__(key_)  # type: ignore
        if is_contained:
            self._on_modified()

    @typing.override
    def __getitem__(self, key: K) -> T:
        key_ = self._key(key)

        if not self._allow_read(key_):
            raise KeyError(f"Reading \"{key}\" is not allowed.")

        return super().__getitem__(key_)  # type: ignore

    @typing.override
    def __setitem__(self, key: K, item: int | float | str | T):
        key_, item_ = self._key_value(key, item)
        if not self._allow_write(key_, item_):
            raise TypeError(
                f"Write to key \"{key}\" of"
                + f" value \"{item}\" is not allowed.")

        super().__setitem__(key_, item_)  # type: ignore
        self._on_modified()

    @typing.override
    def get(self, key: K, default: None | T = None) -> T:  # type: ignore
        key_ = self._key(key)

        if not self._allow_read(key_):
            raise KeyError(f"Reading key \"{key}\" is not allowed.")

        return super().get(key_, default)  # type: ignore

    @typing.override
    def pop(self, key: K, default: None | T = None) -> None | T:  # type: ignore
        key_ = self._key(key)
        if not self._allow_read(key_):
            raise KeyError(f"Deleting key \"{key}\" is not allowed.")

        result = super().pop(key_, default)  # type: ignore
        self._on_modified()

        return result

    @typing.override
    def popitem(self) -> tuple[K, T]:
        for k, v in reversed(tuple(self.items())):
            if self._allow_del(k):
                super().__delitem__(k)
                self._on_modified()
                return (k, v)

        raise IndexError("No removable items remaining.")

    @typing.override
    def clear(self, children: bool = True):
        is_modified = False

        for k, _ in reversed(list(self.items())):
            if self._allow_del(k):
                super().__delitem__(k)
                is_modified = True

        if children:
            for value in list(self.values()):
                if (clr := getattr(value, 'clear', None)) and callable(clr):
                    clr()

        if is_modified:
            self._on_modified()

    @typing.override
    def copy(self) -> typing.Self:
        return copy.copy(self)
