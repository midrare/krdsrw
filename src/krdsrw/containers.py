from __future__ import annotations
import abc
import collections.abc
import copy
import typing
import weakref

K = typing.TypeVar("K", bound=int | float | str)
T = typing.TypeVar("T", bound=typing.Any)


class Chainable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _add_parent(self, parent: typing.Any):
        raise NotImplementedError("Must be implemented by subclass.")

    @abc.abstractmethod
    def _commit_child(self, child: typing.Any):
        raise NotImplementedError("Must be implemented by subclass.")


class ListBase(list[T], Chainable, metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        self._modified: bool = False
        self._parents: list[weakref.ReferenceType[Chainable]] = []
        self._standins: list[typing.Any] = []
        super().__init__(map(self._transform, list(*args, **kwargs)))

    @property
    def is_modified(self) -> bool:
        return self._modified

    def _is_allowed(self, value: typing.Any) -> bool:
        return True

    def _transform(self, value: typing.Any) -> T:
        return value

    def _add_child(self, child: typing.Any):
        if any(e is child for e in self._standins):
            return
        if any(e is child for e in self):
            return
        self._standins.append(child)

    @typing.override
    def _add_parent(self, parent: typing.Any):
        if not isinstance(parent, Chainable):
            return
        for e in self._parents:
            if e() is parent:
                break
        else:
            self._parents.append(weakref.ref(parent))

    def _commit_parent(self):
        while self._parents:
            ref = self._parents.pop()
            if ref is None:
                continue
            parent = ref()
            if parent is None or not isinstance(parent, Chainable):
                continue
            parent._commit_child(self)

    @typing.override
    def _commit_child(self, child: typing.Any):
        if not self._is_allowed(child):
            raise ValueError(
                f"The value \"{child}\" is invalid for this container.")
        super().append(child)

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
                if not self._is_allowed(e):
                    raise ValueError(
                        f"The value \"{e}\" is invalid for this container.")

            super().__setitem__(i, list(self._transform(e) for e in o))
        else:
            if not self._is_allowed(o):
                raise ValueError(
                    f"The value \"{o}\" is invalid for this container.")

            super().__setitem__(i, self._transform(o))

        self._modified = True
        self._commit_parent()

    @typing.override
    def __add__(  # type: ignore
        self,
        other: typing.Sequence[int | float | str | T],
    ) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._is_allowed(e):
                raise ValueError(
                    f"The value \"{e}\" is invalid for this container.")

        result = self.copy()
        super(result.__class__, result).extend( \
            self._transform(e) for e in other)
        return result

    @typing.override
    def __iadd__(
        self,
        other: typing.Iterable[int | float | str | T],
    ) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._is_allowed(e):
                raise ValueError(
                    f"The value \"{e}\" is invalid for this container.")

        result = super().__iadd__(self._transform(e) for e in other)
        self._modified = True
        self._commit_parent()

        return result

    @typing.override
    def append(self, o: int | float | str | T):
        if not self._is_allowed(o):
            raise ValueError(
                f"The value \"{o}\" is invalid for this container.")

        super().append(self._transform(o))
        self._modified = True
        self._commit_parent()

    @typing.override
    def insert(self, i: typing.SupportsIndex, o: int | float | str | T):
        if not self._is_allowed(o):
            raise ValueError(
                f"The value \"{o}\" is invalid for this container.")

        super().insert(i, self._transform(o))
        self._modified = True
        self._commit_parent()

    @typing.override
    def copy(self) -> typing.Self:
        return copy.copy(self)

    @typing.override
    def extend(self, other: typing.Iterable[int | float | str | T]):
        other = list(other)
        for e in other:
            if not self._is_allowed(e):
                raise ValueError(
                    f"The value \"{e}\" is invalid for this container.")

        super().extend(self._transform(e) for e in other)
        self._modified = True
        self._commit_parent()

    @typing.override
    def count(self, o: bool | int | float | str | bytes | T) -> int:
        return super().count(o)  # type: ignore

    @typing.override
    def pop(self, idx: typing.SupportsIndex = -1) -> T:
        result = super().pop(idx)
        self._modified = True
        self._commit_parent()
        return result

    @typing.override
    def remove(self, value: T):
        super().remove(value)
        self._modified = True
        self._commit_parent()

    @typing.override
    def clear(self):
        super().clear()
        self._standins.clear()
        self._modified = True
        self._commit_parent()


class DictBase(dict[K, T], Chainable):
    def __init__(self, *args, **kwargs):
        self._is_modified: bool = False
        self._key_to_standin: dict[K, T] = {}
        self._parents: list[weakref.ReferenceType[Chainable]] = []
        init = self._transform_for_write(dict(*args, **kwargs))
        super().__init__(init)

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    def _is_key_readable(self, key: typing.Any) -> bool:
        return True

    def _transform_key(self, key: typing.Any) -> K:
        return key

    def _is_key_value_writable(
            self, key: typing.Any, value: typing.Any) -> bool:
        return True

    def _transform_key_value(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[K, T]:
        return key, value

    def _make_standin(self, key: typing.Any) -> None | T:
        return None

    def _add_child(self, child: typing.Any):
        raise NotImplementedError

    @typing.override
    def _add_parent(self, parent: typing.Any):
        if not isinstance(parent, Chainable):
            return
        for e in self._parents:
            if e() is parent:
                break
        else:
            self._parents.append(weakref.ref(parent))

    @typing.override
    def _commit_child(self, child: typing.Any):
        for k, v in list(self._key_to_standin.items()):
            if v is not child:
                continue
            self._key_to_standin.pop(k)
            if k in self.keys():
                continue
            assert self._is_key_value_writable(k, child)
            super().__setitem__(k, child)

    def _commit_parent(self):
        while self._parents:
            ref = self._parents.pop()
            if ref is None:
                continue
            parent = ref()
            if parent is None or not isinstance(parent, Chainable):
                continue
            parent._commit_child(self)

    def _is_key_deletable(self, key: typing.Any) -> bool:
        return True

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
        if self._is_key_readable(key):
            key_ = self._transform_key(key)
            if super().__contains__(key_):
                return super().setdefault(key_, default)  # type: ignore

        if not self._is_key_value_writable(key, default):
            raise ValueError(f"The key-value pair "\
                + f"({key}, {default}) "\
                + f"is invalid for this container.")

        key_, default_ = self._transform_key_value(key, default)
        result = super().setdefault(key_, default_)
        self._is_modified = True
        self._commit_parent()

        return result

    def _transform_for_write(self, other: dict) -> dict[K, T]:
        result = {}  # deliberate plain dict
        for key, value in other.items():
            if not self._is_key_value_writable(key, value):
                raise ValueError(f"The key-value pair "\
                + f"({key}, {value}) "\
                + f"is invalid for this container.")

            key_, value_ = self._transform_key_value(key, value)
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
            self._is_modified = True
            self._commit_parent()

    @typing.override
    def __eq__(self, o: typing.Any) -> bool:
        if isinstance(o, self.__class__):
            return dict(o) == dict(self)
        return super().__eq__(o)

    @typing.override
    def __contains__(self, key: typing.Any) -> bool:
        if not self._is_key_readable(key):
            return False
        return super().__contains__(self._transform_key(key))

    @typing.override
    def __delitem__(self, key: K):
        if not self._is_key_deletable(key):
            raise KeyError(f"The key \"{key}\" is required "\
            + "for this container and cannot be deleted.")

        key_ = self._transform_key(key)
        is_contained = super().__contains__(key_)
        super().__delitem__(key_)  # type: ignore
        if is_contained:
            self._is_modified = True
            self._commit_parent()

    @typing.override
    def __getitem__(self, key: K) -> T:
        if not self._is_key_readable(key):
            raise KeyError(f"Key \"{key}\" is invalid for this container.")

        key_ = self._transform_key(key)
        if super().__contains__(key):
            return super().__getitem__(key_)  # type: ignore

        if key_ in self._key_to_standin:
            return self._key_to_standin[key]

        value = self._make_standin(key_)
        if value is not None:
            self._key_to_standin[key_] = value
            value._parents.append(weakref.ref(self))
            return value

        raise KeyError(f"Key \"{key}\" not found.")

    @typing.override
    def __setitem__(self, key: K, item: int | float | str | T):
        if not self._is_key_value_writable(key, item):
            raise ValueError(f"The key-value pair "\
                + f"({key}, {item}) "\
                + f"is invalid for this container.")

        key_, item_ = self._transform_key_value(key, item)
        super().__setitem__(key_, item_)  # type: ignore
        self._is_modified = True
        self._commit_parent()

    @typing.override
    def get(self, key: K, default: None | T = None) -> T:  # type: ignore
        if not self._is_key_readable(key):
            raise KeyError(f"Key \"{key}\" is invalid for this container.")

        key_ = self._transform_key(key)
        return super().get(key_, default)  # type: ignore

    @typing.override
    def pop(self, key: K, default: None | T = None) -> None | T:  # type: ignore
        if not self._is_key_deletable(key):
            raise KeyError(f"The key \"{key}\" is required "\
            + "for this container and cannot be deleted.")

        before = len(self)

        key_ = self._transform_key(key)
        result = super().pop(key_, default)  # type: ignore

        if len(self) != before:
            self._is_modified = True
            self._commit_parent()

        return result

    @typing.override
    def popitem(self, last: bool = True) -> tuple[K, T]:
        items = tuple(self.items())
        if last:
            items = reversed(items)

        for k, v in items:
            if self._is_key_deletable(k):
                # no need for transform b/c already in dict
                super().__delitem__(k)
                self._is_modified = True
                self._commit_parent()
                return (k, v)

        # same exception as plain dict
        raise KeyError("No removable (non-required) items remaining.")

    @typing.override
    def clear(self, children: bool = True):
        is_modified = False

        for k, _ in reversed(list(self.items())):
            if self._is_key_deletable(k):
                super().__delitem__(k)
                is_modified = True

        if children:
            for value in list(self.values()):
                if (clr := getattr(value, 'clear', None)) and callable(clr):
                    clr()

        if self._key_to_standin:
            is_modified = True
            self._key_to_standin.clear()

        if is_modified:
            self._is_modified = True
            self._commit_parent()

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
