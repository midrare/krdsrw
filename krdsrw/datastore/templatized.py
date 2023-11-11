from __future__ import annotations
import typing

from .factory import ValueFactory
from .value import Value

T = typing.TypeVar("T", bound=Value)
K = typing.TypeVar("K", int, str)
V = typing.TypeVar("V", bound=Value)


class CheckedDict(dict[K, V]):
    def __init__(self, key_cls: typing.Type[K], value_cls: typing.Type[V]):
        super().__init__()
        self._key_cls: typing.Type[K] = key_cls
        self._value_cls: typing.Type[V] = value_cls

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().__contains__(key)

    def __getitem__(self, key: K) -> V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().__getitem__(key)

    def __setitem__(self, key: K, item: V):
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        if not isinstance(item, self._value_cls):
            raise TypeError(
                f'Value of class "{item.__class__.__name__}"'
                + ' is of invalid class for this container'
            )

        super().__setitem__(key, item)

    def __delitem__(self, key: K) -> None:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        super().__delitem__(key)

    def copy(self) -> CheckedDict[K, V]:
        d = CheckedDict(self._key_cls, self._value_cls)
        d.update(self)
        return d

    @classmethod
    def fromkeys(cls,
                 iterable: typing.Iterable[K],
                 value: None | V = None) -> TemplatizedDict[K, V]:
        raise NotImplementedError("Unsupported operation for this container")

    def pop(self, key: K) -> V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().pop(key)

    def popitem(self) -> typing.Tuple[K, V]:
        return super().popitem()

    def setdefault(self, key: K, default: V) -> V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        if not isinstance(default, self._value_cls):
            raise TypeError(f"Value is of wrong class for this container")

        return super().setdefault(key, default)

    def update(self, m: typing.Mapping[K, V], **kwargs: V):
        d = dict(m) | kwargs
        for k, v in d.items():
            if not isinstance(k, self._key_cls):
                raise KeyError(
                    f'Key "{k}" is not of class {self._key_cls.__name__}'
                )
            if not isinstance(v, self._value_cls):
                raise TypeError(f"A value is of wrong class for this container")

        super().update(m, **kwargs)

    def get(self, key: K) -> None | V:
        if not isinstance(key, self._key_cls):
            raise KeyError(
                f'Key "{key}" is not of class {self._key_cls.__name__}'
            )
        return super().get(key)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return (
                dict(o) == dict(self) and o._key_cls == self._key_cls
                and o._value_cls == self._value_cls
            )
        return super().__eq__(o)


class TemplatizedDict(dict[K, V]):
    def __init__(
        self,
        template: typing.Callable[[K], V] | typing.Dict[K, ValueFactory[V]],
    ):
        super().__init__()
        self._key_to_template: typing.Dict[K, ValueFactory[V]] = (
            template.copy() if isinstance(template, dict) else {}
        )
        self._default_instantiate: None | typing.Callable[[K], V] = (
            template if callable(template) else None
        )

    def _instantiate(self, key: K) -> V:
        if template := self._key_to_template.get(key):
            return template.instantiate()
        if not self._default_instantiate:
            raise Exception("Missing default instantiate")
        return self._default_instantiate(key)

    def compute_if_absent(self, key: K) -> V:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        if key not in self:
            self[key] = self._instantiate(key)
        return self[key]

    def instantiate_and_put(self, key: K) -> V:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        self[key] = self._instantiate(key)
        return self[key]

    def instantiate_and_put_all(self, keys: typing.List[K]) -> typing.List[V]:
        if any(k not in self._key_to_template and not self._default_instantiate
               for k in keys):
            raise KeyError(f"One or more key(s) is invalid for this container")
        values = []
        for key in keys:
            self[key] = self._instantiate(key)
            values.append(self[key])
        return values

    def __contains__(self, key: object) -> bool:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        return super().__contains__(key)

    def __getitem__(self, key: K) -> V:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        return super().__getitem__(key)

    def __setitem__(self, key: K, item: V):
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        if not self._default_instantiate and (
                key not in self._key_to_template
                or not isinstance(item, self._key_to_template[key].cls)):
            raise TypeError(
                f'Value of class "{item.__class__.__name__}"'
                + ' is of invalid class for this container'
            )

        super().__setitem__(key, item)

    def __delitem__(self, key: K) -> None:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        super().__delitem__(key)

    def copy(self) -> TemplatizedDict[K, V]:
        d = TemplatizedDict(self._key_to_template or self._default_instantiate)
        d.update(self)
        return d

    @classmethod
    def fromkeys(cls,
                 iterable: typing.Iterable[K],
                 value: None | V = ...) -> TemplatizedDict[K, V]:
        raise NotImplementedError(
            "Unsupported operation. (Cannot instantiate without template)"
        )

    def pop(self, key: K) -> V:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        return super().pop(key)

    def popitem(self) -> typing.Tuple[K, V]:
        return super().popitem()

    def setdefault(self, key: K, default: V) -> V:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        if not self._default_instantiate and (
                key not in self._key_to_template
                or not isinstance(default, self._key_to_template[key].cls)):
            raise TypeError(f"Value is of wrong class for this container")

        return super().setdefault(key, default)

    def update(self, m: typing.Mapping[K, V], **kwargs: V):
        d = dict(m) | kwargs
        for k, v in d.items():
            if k not in self._key_to_template and not self._default_instantiate:
                raise KeyError(f'Key "{k}" is invalid for this container')
            if not self._default_instantiate and (
                    k not in self._key_to_template
                    or not isinstance(v, self._key_to_template[k].cls)):
                raise TypeError(f"A value is of wrong class for this container")

        super().update(m, **kwargs)

    def get(self, key: K) -> None | V:
        if key not in self._key_to_template and not self._default_instantiate:
            raise KeyError(f'Key "{key}" is invalid for this container')
        return super().get(key)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return (
                dict(o) == dict(self)
                and o._default_instantiate == self._default_instantiate
                and o._key_to_template == self._key_to_template
            )
        return super().__eq__(o)


class TemplatizedList(list[T]):
    def __init__(self, template: ValueFactory[T]):
        super().__init__()
        self.template: ValueFactory[T] = template

    def instantiate_and_append(self) -> T:
        o = self.template.instantiate()
        super().append(o)
        return o

    def instantiate_and_insert(self, index: int) -> T:
        o = self.template.instantiate()
        super().insert(index, o)
        return o

    @property
    def cls(self) -> typing.Type:
        return self.template.cls

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.template == o.template and list(self) == list(o)

        return super().__eq__(o)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, self.template.cls):
            raise TypeError(f"Value is of wrong class for this container")
        return super().__contains__(item)

    def __setitem__(self, i: int, o: T):
        if not isinstance(o, self.template.cls):
            raise TypeError(f"Value is of wrong class for this container")
        super().__setitem__(i, o)

    def __add__(self, other: typing.Iterable[T]) -> TemplatizedList[T]:
        lst = list(other)
        if any(not isinstance(e, self.template.cls) for e in lst):
            raise TypeError(
                f"One or more value(s) is of wrong class for this container"
            )

        o = TemplatizedList(self.template)
        o.extend(self)
        o.extend(lst)
        return o

    def __iadd__(self, other: typing.Iterable[T]) -> TemplatizedList[T]:
        lst = list(other)
        if any(not isinstance(e, self.template.cls) for e in lst):
            raise TypeError(
                f"One or more value(s) is of wrong class for this container"
            )
        super().extend(lst)
        return self

    def append(self, item: T) -> None:
        if not isinstance(item, self.template.cls):
            raise TypeError(f"Value is of wrong class for this container")
        super().append(item)

    def insert(self, i: int, item: T) -> None:
        if not isinstance(item, self.template.cls):
            raise TypeError(f"Value is of wrong class for this container")
        super().insert(i, item)

    def remove(self, item: T):
        if not isinstance(item, self.template.cls):
            raise TypeError(f"Value is of wrong class for this container")
        super().remove(item)

    def copy(self) -> TemplatizedList[T]:
        o = TemplatizedList(self.template)
        o.extend(self)
        return o

    def count(self, item: T) -> int:
        if not isinstance(item, self.template.cls):
            raise TypeError(f"Value is of wrong class for this container")
        return super().count(item)

    def index(self, item: T, *args: typing.Any) -> int:
        if not isinstance(item, self.template.cls):
            raise TypeError(f"Value is of wrong class for this container")
        return super().index(item, *args)

    def extend(self, other: typing.Iterable[T]):
        lst = list(other)
        if any(not isinstance(e, self.template.cls) for e in lst):
            raise TypeError(
                f"One or more value(s) is of wrong class for this container"
            )
        super().extend(lst)
