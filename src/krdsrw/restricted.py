import collections.abc
import copy
import operator
import re
import typing
import weakref

K = typing.TypeVar("K", bound=int | float | str)
T = typing.TypeVar("T", bound=typing.Any)


class RestrictedList(list[T]):
    def __init__(self, *args, **kwargs):
        super().__init__(
            self._pre_write_transform(e) \
            for e in list(*args, **kwargs))

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
            assert isinstance(o, collections.abc.Iterable), \
                'when index is slice the value must be iterable'

            o = list(o)
            for e in o:
                if not self._pre_write_filter(e):
                    raise ValueError(
                        f"The value \"{e}\" is invalid for this container.")

            super().__setitem__(
                i, list(self._pre_write_transform(e) for e in o))
        else:
            if not self._pre_write_filter(o):
                raise ValueError(
                    f"The value \"{o}\" is invalid for this container.")

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
                raise ValueError(
                    f"The value \"{e}\" is invalid for this container.")

        result = self.copy()
        super(result.__class__, result).extend( \
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
                raise ValueError(
                    f"The value \"{e}\" is invalid for this container.")

        result = super().__iadd__(self._pre_write_transform(e) for e in other)
        self._post_write_hook()

        return result

    @typing.override
    def append(self, o: int | float | str | T):
        if not self._pre_write_filter(o):
            raise ValueError(
                f"The value \"{o}\" is invalid for this container.")

        super().append(self._pre_write_transform(o))
        self._post_write_hook()

    @typing.override
    def insert(self, i: typing.SupportsIndex, o: int | float | str | T):
        if not self._pre_write_filter(o):
            raise ValueError(
                f"The value \"{o}\" is invalid for this container.")

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
                raise ValueError(
                    f"The value \"{e}\" is invalid for this container.")

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


class RestrictedDict(dict[K, T]):
    def __init__(self, *args, **kwargs):
        super().__init__(self._transform_for_write(dict(*args, **kwargs)))

    def _pre_read_filter(self, key: typing.Any) -> bool:
        return True

    def _pre_read_transform(self, key: typing.Any) -> K:
        return key

    def _pre_write_filter(self, key: typing.Any, value: typing.Any) -> bool:
        return True

    def _pre_write_transform(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[K, T]:
        return key, value

    def _post_write_hook(self):
        pass

    def _pre_del_filter(self, key: typing.Any) -> bool:
        return True

    def _pre_del_transform(self, key: typing.Any) -> T:
        return key

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
        if self._pre_read_filter(key):
            key_ = self._pre_read_transform(key)
            if super().__contains__(key_):
                return super().setdefault(key_, default)  # type: ignore

        if not self._pre_write_filter(key, default):
            raise ValueError(f"The key-value pair "\
                + f"({key}, {default}) "\
                + f"is invalid for this container.")

        key_, default_ = self._pre_write_transform(key, default)
        result = super().setdefault(key_, default_)
        self._post_write_hook()

        return result

    def _transform_for_write(self, other: dict) -> dict[K, T]:
        result = {}  # deliberate plain dict
        for key, value in other.items():
            if not self._pre_write_filter(key, value):
                raise ValueError(f"The key-value pair "\
                + f"({key}, {value}) "\
                + f"is invalid for this container.")

            key_, value_ = self._pre_write_transform(key, value)
            result[key_] = value_
        return result

    @typing.override
    def update( # type: ignore
        self,
        *args: typing.Mapping[K, T],
        **kwargs: T,
    ):
        other = self._transform_for_write(dict(*args, **kwargs))
        super().update(other)
        if other:
            self._post_write_hook()

    @typing.override
    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return dict(o) == dict(self)
        return super().__eq__(o)

    @typing.override
    def __contains__(self, key: typing.Any) -> bool:
        if not self._pre_read_filter(key):
            return False
        return super().__contains__(self._pre_read_transform(key))

    @typing.override
    def __delitem__(self, key: K):
        if not self._pre_del_filter(key):
            raise KeyError(f"The key \"{key}\" is required "\
            + "for this container and cannot be deleted.")

        key_ = self._pre_del_transform(key)
        is_contained = super().__contains__(key_)
        super().__delitem__(key_)  # type: ignore
        if is_contained:
            self._post_write_hook()

    @typing.override
    def __getitem__(self, key: K) -> T:
        if not self._pre_read_filter(key):
            raise KeyError(f"Key \"{key}\" is invalid for this container.")

        key_ = self._pre_read_transform(key)
        return super().__getitem__(key_)  # type: ignore

    @typing.override
    def __setitem__(self, key: K, item: int | float | str | T):
        if not self._pre_write_filter(key, item):
            raise ValueError(f"The key-value pair "\
                + f"({key}, {item}) "\
                + f"is invalid for this container.")

        key_, item_ = self._pre_write_transform(key, item)
        super().__setitem__(key_, item_)  # type: ignore
        self._post_write_hook()

    @typing.override
    def get(self, key: K, default: None | T = None) -> T:  # type: ignore
        if not self._pre_read_filter(key):
            raise KeyError(f"Key \"{key}\" is invalid for this container.")

        key_ = self._pre_read_transform(key)
        return super().get(key_, default)  # type: ignore

    @typing.override
    def pop(self, key: K, default: None | T = None) -> None | T:  # type: ignore
        if not self._pre_del_filter(key):
            raise KeyError(f"The key \"{key}\" is required "\
            + "for this container and cannot be deleted.")

        before = len(self)

        key_ = self._pre_del_transform(key)
        result = super().pop(key_, default)  # type: ignore

        if len(self) != before:
            self._post_write_hook()

        return result

    @typing.override
    def popitem(self, last: bool = True) -> tuple[K, T]:
        items = tuple(self.items())
        if last:
            items = reversed(items)

        for k, v in items:
            if self._pre_del_filter(k):
                # no need for transform b/c already in dict
                super().__delitem__(k)
                self._post_write_hook()
                return (k, v)

        # same exception as plain dict
        raise KeyError("No removable (non-required) items remaining.")

    @typing.override
    def clear(self, children: bool = True):
        is_modified = False

        for k, _ in reversed(list(self.items())):
            if self._pre_del_filter(k):
                super().__delitem__(k)
                is_modified = True

        if children:
            for value in list(self.values()):
                if (clr := getattr(value, 'clear', None)) and callable(clr):
                    clr()

        if is_modified:
            self._post_write_hook()

    @typing.override
    def copy(self) -> typing.Self:
        return copy.copy(self)

    @typing.override
    def __or__(
        self,
        other: typing.Mapping[typing.Any, typing.Any],
    ) -> typing.Self:
        return self.__class__({ **self, **dict(other) })

    @typing.override
    def __ior__(  # type: ignore
        self,
        other: typing.Mapping[typing.Any, typing.Any],
    ) -> typing.Self:
        self.update(dict(other))
        return self


class ChainDict(dict):
    def __init__(self, *args, **kwargs):
        self._parents: list[weakref.ReferenceType[typing.Self]] = []
        self._candidates: dict[typing.Any, typing.Any] = {}
        # parent constructor last so hooks work correctly
        super().__init__(*args, **kwargs)

    def _make_candidate(self, key: typing.Any) -> typing.Any:
        return self.__class__()

    def _get_candidate(self, key: typing.Any) -> typing.Any:
        result = self._candidates.get(key)
        if result is None:
            result = self._make_candidate(key)
            self._candidates[key] = result
        return result

    @typing.override
    def __getitem__(self, key: typing.Any) -> typing.Any:
        o = None

        if o is None and super().__contains__(key):
            o = super().__getitem__(key)

        if o is None:
            o = self._get_candidate(key)
            if not any(e() is self for e in o._parents):
                o._parents.append(weakref.ref(self))

        return o

    @typing.override
    def __setitem__(self, key: typing.Any, value: typing.Any):
        super().__setitem__(key, value)
        for p_ref in list(self._parents):
            parent = p_ref()
            if parent is None:
                self._parents.remove(p_ref)
                continue

            for k, v in list(parent._candidates.items()):
                if v is self:
                    parent._candidates.pop(k)
                    parent[k] = self
