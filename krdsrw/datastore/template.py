import typing

from .value import Value

T = typing.TypeVar("T", bound=Value)


class Template(typing.Generic[T]):
    def __init__(self, cls: typing.Type, *args, **kwargs):
        self.cls: typing.Type = cls
        self._constructor_args: typing.List[typing.Any] = list(args)
        self._constructor_kwargs: typing.Dict[str, typing.Any] = dict(kwargs)

    def instantiate(self) -> T:
        return self.cls(*self._constructor_args, **self._constructor_kwargs)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return (
                self.cls == o.cls
                and self._constructor_args == o._constructor_args
                and self._constructor_kwargs == o._constructor_kwargs
            )

        return super().__eq__(o)

    def __str__(self) -> str:
        args = []
        for arg in self._constructor_args:
            args.append(str(arg))
        for key, value in self._constructor_kwargs.items():
            args.append(str(key) + ":" + str(value))
        return "%s{%s[%s]}" % (
            self.__class__.__name__,
            self.cls.__name__,
            ", ".join(args),
        )
