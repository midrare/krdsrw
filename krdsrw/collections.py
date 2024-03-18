import collections.abc
import copy
import typing

from .error import KRDSRWError


class RestrictionError(KRDSRWError):
    pass


class InvalidKeyError(RestrictionError):
    def __init__(self, key: typing.Any):
        super().__init__(f"Key \"{key}\" is invalid for this container.")
        self._key: typing.Any = key

    @property
    def key(self) -> typing.Any:
        return self._key


class InvalidValueError(RestrictionError):
    def __init__(self, value: typing.Any, key: None | typing.Any = None):
        errmsg = f"The value \"{value}\" is invalid for this container."
        if key is not None:
            errmsg = f"The key-value pair "\
                + f"({key}, {value}) "\
                + f"is invalid for this container."

        super().__init__(errmsg)

        self._key: None | typing.Any = key
        self._value: typing.Any = value

    @property
    def key(self) -> None | typing.Any:
        return self._key

    @property
    def value(self) -> typing.Any:
        return self._value


class RequiredKeyError(RestrictionError):
    def __init__(self, key: typing.Any):
        errmsg = f"The key \"{key}\" is required "\
            + "for this container and cannot be deleted."
        super().__init__(errmsg)
        self._key: typing.Any = key

    @property
    def key(self) -> typing.Any:
        return self._key


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
                    raise InvalidValueError(e)

            super().__setitem__(
                i, list(self._pre_write_transform(e) for e in o))
        else:
            if not self._pre_write_filter(o):
                raise InvalidValueError(o)

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
                raise InvalidValueError(e)

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
                raise InvalidValueError(e)

        result = super().__iadd__(self._pre_write_transform(e) for e in other)
        self._post_write_hook()

        return result

    @typing.override
    def append(self, o: int | float | str | T):
        if not self._pre_write_filter(o):
            raise InvalidValueError(o)

        super().append(self._pre_write_transform(o))
        self._post_write_hook()

    @typing.override
    def insert(self, i: typing.SupportsIndex, o: int | float | str | T):
        if not self._pre_write_filter(o):
            raise InvalidValueError(o)

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
                raise InvalidValueError(e)

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

    def _pre_default_filter(
        self,
        key: typing.Any,
        default: typing.Any,
    ) -> bool:
        return True

    def _pre_default_transform(
        self: typing.Any,
        key: typing.Any,
        default: typing.Any,
    ) -> T:
        return default

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
        if not self._pre_default_filter(key, default):
            raise InvalidValueError(default, key)

        key_ = self._pre_read_transform(key)
        if super().__contains__(key_):
            default_ = self._pre_default_transform(key, default)
            return super().setdefault(key_, default_)  # type: ignore

        if not self._pre_write_filter(key, default):
            raise InvalidValueError(default, key)

        default_ = self._pre_default_transform(key, default)
        key_, default_ = self._pre_write_transform(key, default_)
        result = super().setdefault(key_, default_)
        self._post_write_hook()

        return result

    def _transform_for_write(self, other: dict) -> dict[K, T]:
        result = {}  # deliberate plain dict
        for key, value in other.items():
            if not self._pre_write_filter(key, value):
                raise InvalidValueError(value, key)

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
            raise RequiredKeyError(key)

        key_ = self._pre_del_transform(key)
        is_contained = super().__contains__(key_)
        super().__delitem__(key_)  # type: ignore
        if is_contained:
            self._post_write_hook()

    @typing.override
    def __getitem__(self, key: K) -> T:
        if not self._pre_read_filter(key):
            raise InvalidKeyError(key)

        key_ = self._pre_read_transform(key)
        return super().__getitem__(key_)  # type: ignore

    @typing.override
    def __setitem__(self, key: K, item: int | float | str | T):
        if not self._pre_write_filter(key, item):
            raise InvalidValueError(item, key)

        key_, item_ = self._pre_write_transform(key, item)
        super().__setitem__(key_, item_)  # type: ignore
        self._post_write_hook()

    @typing.override
    def get(self, key: K, default: None | T = None) -> T:  # type: ignore
        if not self._pre_read_filter(key):
            raise InvalidKeyError(key)
        if not self._pre_default_filter(key, default):
            raise InvalidValueError(default, key)

        key_ = self._pre_read_transform(key)
        key_, default_ = self._pre_default_transform(key_, default)
        return super().get(key_, default_)  # type: ignore

    @typing.override
    def pop(self, key: K, default: None | T = None) -> None | T:  # type: ignore
        if not self._pre_del_filter(key):
            raise RequiredKeyError(key)

        key_ = self._pre_del_transform(key)
        default_ = self._pre_default_transform(key, default)
        before = len(self)
        result = super().pop(key_, default_)  # type: ignore
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
