import abc
import collections.abc
import copy
import typing
import weakref

K = typing.TypeVar("K", bound=int | float | str)
T = typing.TypeVar("T", bound=typing.Any)
_VOID = object()


class _Observable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _add_observer(self, receiver: typing.Any):
        raise NotImplementedError("Must be implemented by subclass.")

    @abc.abstractmethod
    def _remove_observer(self, receiver: typing.Any):
        raise NotImplementedError("Must be implemented by subclass.")

    @abc.abstractmethod
    def _on_observed(self, sender: typing.Any):
        raise NotImplementedError("Must be implemented by subclass.")


class ByteBase(int):
    _builtin: typing.Final[type] = int

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __str__(self) -> str:
        return f"0x{hex(self)}"

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{0x{hex(self)}}}"

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self,
        other: int,
        modulo: None | int = None,
    ) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return int(self) != 0


class CharBase(int):
    _builtin: typing.Final[type] = int

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __str__(self) -> str:
        return str(chr(self))

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{chr(self)}}}"

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self,
        other: int,
        modulo: None | int = None,
    ) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return int(self) != 0


class BoolBase(int):
    _builtin: typing.Final[type] = int

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __str__(self) -> str:
        return str(bool(self))

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{bool(self)}}}"

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self,
        other: int,
        modulo: None | int = None,
    ) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return int(self) != 0


class ShortBase(int):
    _builtin: typing.Final[type] = int

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self,
        other: int,
        modulo: None | int = None,
    ) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return int(self) != 0


class IntBase(int):
    _builtin: typing.Final[type] = int

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self,
        other: int,
        modulo: None | int = None,
    ) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return int(self) != 0


class LongBase(int):
    _builtin: typing.Final[type] = int

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{int(self)}}}"

    @typing.override
    def __add__(self, other: int) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: int) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: int) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: int) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: int) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: int) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(  # type: ignore
        self,
        other: int,
        modulo: None | int = None,
    ) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __lshift__(self, other: int) -> typing.Self:
        o = super().__lshift__(other)
        return self.__class__(o)

    @typing.override
    def __rshift__(self, other: int) -> typing.Self:
        o = super().__rshift__(other)
        return self.__class__(o)

    @typing.override
    def __and__(self, other: int) -> typing.Self:
        o = super().__and__(other)
        return self.__class__(o)

    @typing.override
    def __xor__(self, other: int) -> typing.Self:
        o = super().__xor__(other)
        return self.__class__(o)

    @typing.override
    def __or__(self, other: int) -> typing.Self:
        o = super().__or__(other)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: int) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: int) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: int) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: int) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: int) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: int) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: int) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: int, modulo: None | int = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __rlshift__(self, other: int) -> typing.Self:
        o = super().__rlshift__(other)
        return self.__class__(o)

    @typing.override
    def __rrshift__(self, other: int) -> typing.Self:
        o = super().__rrshift__(other)
        return self.__class__(o)

    @typing.override
    def __rand__(self, other: int) -> typing.Self:
        o = super().__rand__(other)
        return self.__class__(o)

    @typing.override
    def __rxor__(self, other: int) -> typing.Self:
        o = super().__rxor__(other)
        return self.__class__(o)

    @typing.override
    def __ror__(self, other: int) -> typing.Self:
        o = super().__ror__(other)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __invert__(self) -> typing.Self:
        o = super().__invert__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return int(self) != 0


class FloatBase(float):
    _builtin: typing.Final[type] = float

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @typing.override
    def __add__(self, other: float) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: float) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: float) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: float) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: float) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: float) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: float) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: float) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: float) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: float) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: float) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: float) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return float(self) != 0.0


class DoubleBase(float):
    _builtin: typing.Final[type] = float

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, **kwargs)

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{{float(self)}}}"

    @typing.override
    def __add__(self, other: float) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __sub__(self, other: float) -> typing.Self:
        o = super().__sub__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: float) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __truediv__(self, other: float) -> typing.Self:
        o = super().__truediv__(other)
        return self.__class__(o)

    @typing.override
    def __floordiv__(self, other: float) -> typing.Self:
        o = super().__floordiv__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: float) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __divmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__divmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __pow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__pow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __radd__(self, other: float) -> typing.Self:
        o = super().__radd__(other)
        return self.__class__(o)

    @typing.override
    def __rsub__(self, other: float) -> typing.Self:
        o = super().__rsub__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: float) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    @typing.override
    def __rtruediv__(self, other: float) -> typing.Self:
        o = super().__rtruediv__(other)
        return self.__class__(o)

    @typing.override
    def __rfloordiv__(self, other: float) -> typing.Self:
        o = super().__rfloordiv__(other)
        return self.__class__(o)

    @typing.override
    def __rmod__(self, other: float) -> typing.Self:
        o = super().__rmod__(other)
        return self.__class__(o)

    @typing.override
    def __rdivmod__(self, other: float) -> tuple[typing.Self, typing.Self]:
        q, r = super().__rdivmod__(other)
        return self.__class__(q), self.__class__(r)

    @typing.override
    def __rpow__(self, other: float, modulo: None = None) -> typing.Self:
        o = super().__rpow__(other, modulo)
        return self.__class__(o)

    @typing.override
    def __neg__(self) -> typing.Self:
        o = super().__neg__()
        return self.__class__(o)

    @typing.override
    def __pos__(self) -> typing.Self:
        o = super().__pos__()
        return self.__class__(o)

    @typing.override
    def __abs__(self) -> typing.Self:
        o = super().__abs__()
        return self.__class__(o)

    @typing.override
    def __bool__(self) -> bool:
        return float(self) != 0.0


class Utf8StrBase(str):
    _builtin: typing.Final[type] = str

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, *kwargs)

    @typing.override
    def __init__(self, *args, **kwargs):
        super().__init__()

    @typing.override
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{{"{str(self)}"}}'

    @typing.override
    def __add__(self, other: str) -> typing.Self:
        o = super().__add__(other)
        return self.__class__(o)

    @typing.override
    def __mul__(self, other: typing.SupportsIndex) -> typing.Self:
        o = super().__mul__(other)
        return self.__class__(o)

    @typing.override
    def __mod__(self, other: str) -> typing.Self:
        o = super().__mod__(other)
        return self.__class__(o)

    @typing.override
    def __rmul__(self, other: typing.SupportsIndex) -> typing.Self:
        o = super().__rmul__(other)
        return self.__class__(o)

    def __bool__(self) -> bool:
        return len(str(self)) > 0

    def __copy__(self) -> typing.Self:
        return self.__class__(self)

    def __deepcopy__(self) -> typing.Self:
        return self.__class__(self)


class ListBase(list[T], _Observable, metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        self._modified: bool = False
        self._parents: list[weakref.ReferenceType[_Observable]] = []
        self._postulates: list[typing.Any] = []
        super().__init__(map(self._transform, list(*args, **kwargs)))

    @property
    def is_modified(self) -> bool:
        return self._modified

    def _is_allowed(self, value: typing.Any) -> bool:
        return True

    def _transform(self, value: typing.Any) -> T:
        return value

    def _add_postulate(self, child: typing.Any):
        if any(e is child for e in self._postulates) or any(
            e is child for e in self
        ):
            return
        self._postulates.append(child)
        if isinstance(child, _Observable):
            child._add_observer(self)

    @typing.override
    def _add_observer(self, receiver: typing.Any):
        if not isinstance(receiver, _Observable) or any(
            e() is receiver for e in self._parents
        ):
            return
        self._parents.append(weakref.ref(receiver))

    @typing.override
    def _remove_observer(self, receiver: typing.Any):
        self._parents[:] = [e for e in self._parents if e() is not receiver]

    def _notify_observers(self):
        while self._parents:
            ref = self._parents.pop()
            if ref is None:
                continue
            parent = ref()
            if parent is None or not isinstance(parent, _Observable):
                continue
            parent._on_observed(self)

    @typing.override
    def _on_observed(self, sender: typing.Any):
        assert self._is_allowed(sender), (
            f'Invalid value "{sender}" '
            + "(should have been screened out before this point)"
        )

        found = False
        for i, e in reversed(list(enumerate(self._postulates))):
            if e is sender:
                self._postulates.pop(i)
                found = True

        if found:
            super().append(sender)
            self._modified = True
            self._notify_observers()

    @typing.overload
    def __setitem__(
        self,
        i: typing.SupportsIndex,
        o: int | float | str | T,
    ): ...

    @typing.overload
    def __setitem__(
        self,
        i: slice,
        o: typing.Iterable[int | float | str | T],
    ): ...

    @typing.override
    def __setitem__(
        self,
        i: typing.SupportsIndex | slice,
        o: (
            bool
            | int
            | float
            | str
            | bytes
            | T
            | typing.Iterable[bool | int | float | str | bytes | T]
        ),
    ):
        if isinstance(i, slice):
            assert isinstance(
                o, collections.abc.Iterable
            ), "when index is slice the value must be iterable"

            o = list(o)
            for e in o:
                if not self._is_allowed(e):
                    raise ValueError(
                        f'The value "{e}" is invalid for this container.'
                    )

            super().__setitem__(i, list(self._transform(e) for e in o))
        else:
            if not self._is_allowed(o):
                raise ValueError(
                    f'The value "{o}" is invalid for this container.'
                )

            super().__setitem__(i, self._transform(o))

        self._modified = True
        self._notify_observers()

    @typing.override
    def __add__(  # type: ignore
        self,
        other: typing.Sequence[int | float | str | T],
    ) -> typing.Self:
        other = list(other)
        for e in other:
            if not self._is_allowed(e):
                raise ValueError(
                    f'The value "{e}" is invalid for this container.'
                )

        result = self.copy()
        super(result.__class__, result).extend(
            self._transform(e) for e in other
        )
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
                    f'The value "{e}" is invalid for this container.'
                )

        result = super().__iadd__(self._transform(e) for e in other)
        self._modified = True
        self._notify_observers()

        return result

    @typing.override
    def append(self, o: int | float | str | T):
        if not self._is_allowed(o):
            raise ValueError(
                f'The value "{o}" is invalid for this container.'
            )

        super().append(self._transform(o))
        self._modified = True
        self._notify_observers()

    @typing.override
    def insert(self, i: typing.SupportsIndex, o: int | float | str | T):
        if not self._is_allowed(o):
            raise ValueError(
                f'The value "{o}" is invalid for this container.'
            )

        super().insert(i, self._transform(o))
        self._modified = True
        self._notify_observers()

    @typing.override
    def copy(self) -> typing.Self:
        return copy.copy(self)

    @typing.override
    def extend(self, other: typing.Iterable[int | float | str | T]):
        other = list(other)
        for e in other:
            if not self._is_allowed(e):
                raise ValueError(
                    f'The value "{e}" is invalid for this container.'
                )

        super().extend(self._transform(e) for e in other)
        self._modified = True
        self._notify_observers()

    @typing.override
    def count(self, o: bool | int | float | str | bytes | T) -> int:
        return super().count(o)  # type: ignore

    @typing.override
    def pop(self, idx: typing.SupportsIndex = -1) -> T:
        result = super().pop(idx)
        self._modified = True
        self._notify_observers()
        return result

    @typing.override
    def remove(self, value: T):
        while True:
            try:
                super().remove(value)
                self._modified = True
                self._notify_observers()
                break
            except ValueError:
                pass

            try:
                self._postulates.remove(value)
                self._modified = True
                self._notify_observers()
                break
            except ValueError:
                pass

            raise ValueError(f'Value "{value}" not in container.')

    @typing.override
    def clear(self):
        super().clear()
        self._postulates.clear()
        self._modified = True
        self._notify_observers()


class DictBase(dict[K, T], _Observable):
    def __init__(self, *args, **kwargs):
        self._modified: bool = False
        self._key_to_postulate: dict[K, T] = {}
        self._parents: list[weakref.ReferenceType[_Observable]] = []
        init = self._transform_for_write(dict(*args, **kwargs))
        super().__init__(init)

    @property
    def is_modified(self) -> bool:
        return self._modified

    def _is_key_readable(self, key: typing.Any) -> bool:
        return True

    def _is_key_deletable(self, key: typing.Any) -> bool:
        return True

    def _is_key_writable(self, key: typing.Any) -> bool:
        return True

    def _is_value_writable(self, value: typing.Any, key: typing.Any) -> bool:
        return True

    def _transform_key(self, key: typing.Any) -> K:
        return key

    def _transform_value(self, value: typing.Any, key: typing.Any) -> T:
        return value

    def _make_postulate(self, key: typing.Any) -> None | T:
        return None

    def _add_postulate(self, key: typing.Any, child: typing.Any):
        assert key not in self.keys(), (
            f"Cannot create postulate for key-value ({key}, {child}) "
            + "that already exists (should have been screened out "
            + "before this point)"
        )
        self._key_to_postulate[key] = child
        if isinstance(child, _Observable):
            child._add_observer(self)

    @typing.override
    def _add_observer(self, receiver: typing.Any):
        if not isinstance(receiver, _Observable) or any(
            e() is receiver for e in self._parents
        ):
            return
        self._parents.append(weakref.ref(receiver))

    @typing.override
    def _remove_observer(self, receiver: typing.Any):
        self._parents[:] = [e for e in self._parents if e() is not receiver]

    def _notify_observers(self):
        while self._parents:
            ref = self._parents.pop()
            if ref is None:
                continue
            parent = ref()
            if parent is None or not isinstance(parent, _Observable):
                continue
            parent._on_observed(self)

    @typing.override
    def _on_observed(self, sender: typing.Any):
        found = False
        for k, v in list(self._key_to_postulate.items()):
            if v is not sender:
                continue
            self._key_to_postulate.pop(k)
            if k in self.keys():
                continue
            assert self._is_key_readable(k), (
                f'Key "{k}" is not readable '
                + "(should have been screened out before this point)."
            )
            assert self._is_key_writable(k), (
                f'Key "{k}" is not writable '
                + "(should have been screened out before this point)."
            )
            assert self._is_value_writable(sender, k), (
                f"Key-value pair ({k}, {sender}) is not writable "
                + "(should have been screened out before this point)."
            )
            super().__setitem__(k, sender)
            found = True

        if found:
            self._modified = True
            self._notify_observers()

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

        if not self._is_key_readable(key):
            raise KeyError(
                f'The key "{key}" is '
                + "not readable (in addition to writable) "
                + "for this container."
            )

        if not self._is_key_writable(key):
            raise KeyError(
                f'The key "{key}" is ' + "not writable for this container."
            )

        if not self._is_value_writable(default, key):
            raise ValueError(
                f"The key-value pair "
                + f"({key}, {default}) "
                + f"is invalid for this container."
            )

        default_ = self._transform_value(default, key)
        key_ = self._transform_key(key)
        result = super().setdefault(key_, default_)
        self._modified = True
        self._notify_observers()

        return result

    def _transform_for_write(self, other: dict) -> dict[K, T]:
        result = {}  # deliberate plain dict
        for key, value in other.items():
            if not self._is_key_readable(key):
                raise KeyError(
                    f'The key "{key}" is '
                    + "not readable (in addition to writable) "
                    + "for this container."
                )
            if not self._is_key_writable(key):
                raise KeyError(
                    f'The key "{key}" is '
                    + "not writable for this container."
                )
            if not self._is_value_writable(value, key):
                raise ValueError(
                    f"The key-value pair "
                    + f"({key}, {value}) "
                    + f"is invalid for this container."
                )

            value_ = self._transform_value(value, key)
            key_ = self._transform_key(key)
            result[key_] = value_
        return result

    @typing.override
    def update(  # type: ignore
        self,
        *args: typing.Mapping[K, T],
        **kwargs: T,
    ):
        other = self._transform_for_write(dict(*args, **kwargs))
        super().update(other)
        if other:
            self._modified = True
            self._notify_observers()

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
            raise KeyError(
                f'The key "{key}" is required '
                + "for this container and cannot be deleted."
            )

        key_ = self._transform_key(key)
        is_contained = super().__contains__(key_)
        super().__delitem__(key_)  # type: ignore
        if is_contained:
            self._modified = True
            self._notify_observers()

    @typing.override
    def __getitem__(self, key: K) -> T:
        if not self._is_key_readable(key):
            raise KeyError(f'Key "{key}" is invalid for this container.')

        key_ = self._transform_key(key)
        if super().__contains__(key_):
            return super().__getitem__(key_)  # type: ignore

        if key_ in self._key_to_postulate:
            return self._key_to_postulate[key_]

        value = self._make_postulate(key_)
        if value is not None:
            self._add_postulate(key_, value)
            return value

        raise KeyError(f'Key "{key}" not found.')

    @typing.override
    def __setitem__(self, key: K, item: int | float | str | T):
        if not self._is_key_readable(key):
            raise KeyError(
                f'The key "{key}" is '
                + "not readable (in addition to writable) "
                + "for this container."
            )
        if not self._is_key_writable(key):
            raise KeyError(
                f'The key "{key}" is ' + "not writable for this container."
            )

        if not self._is_value_writable(item, key):
            raise ValueError(
                f"The key-value pair "
                + f"({key}, {item}) "
                + f"is invalid for this container."
            )

        item_ = self._transform_value(item, key)
        key_ = self._transform_key(key)
        super().__setitem__(key_, item_)  # type: ignore
        self._modified = True
        self._notify_observers()

    @typing.override
    def get(self, key: K, default: None | T = None) -> T:  # type: ignore
        if not self._is_key_readable(key):
            # raise KeyError(f"Key \"{key}\" is invalid for this container.")
            return default  # type: ignore

        key_ = self._transform_key(key)
        return super().get(key_, default)  # type: ignore

    @typing.override
    def pop(
        self,
        key: K,
        default: None | typing.Any = _VOID,
    ) -> T | typing.Any:  # type: ignore
        if not self._is_key_readable(key) and default is not _VOID:
            return default

        key_ = self._transform_key(key)
        if not super().__contains__(key_):
            if default is _VOID:
                raise KeyError(f'Key "{key}" not found.')
            return default

        if not self._is_key_readable(key):
            raise KeyError(f'The key "{key}" is invalid for this container.')

        if not self._is_key_deletable(key):
            raise KeyError(
                f'The key "{key}" is required '
                + "for this container and cannot be deleted."
            )

        result = super().pop(key_)
        self._modified = True
        self._notify_observers()

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
                self._modified = True
                self._notify_observers()
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
                if (clr := getattr(value, "clear", None)) and callable(clr):
                    clr()

        if self._key_to_postulate:
            is_modified = True
            self._key_to_postulate.clear()

        if is_modified:
            self._modified = True
            self._notify_observers()

    @typing.override
    def copy(self) -> typing.Self:
        return copy.copy(self)

    @typing.override
    def __or__(
        self,
        other: typing.Mapping[typing.Any, typing.Any],
    ) -> typing.Self:
        return self.__class__({**self, **dict(other)})

    @typing.override
    def __ior__(  # type: ignore
        self,
        other: typing.Mapping[typing.Any, typing.Any],
    ) -> typing.Self:
        o = self._transform_for_write(dict(other))
        o = filter(lambda e: e[0] not in self, o.items())
        if o:
            super().update(o)
            self._modified = True
            self._notify_observers()
        return self
