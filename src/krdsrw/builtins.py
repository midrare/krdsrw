import typing


class _Byte(int):
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


class _Char(int):
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


class _Bool(int):
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


class _Short(int):
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


class _Int(int):
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


class _Long(int):
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


class _Float(float):
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


class _Double(float):
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


class _Utf8Str(str):
    _builtin: typing.Final[type] = str

    @typing.override
    def __new__(cls, *args, **kwargs) -> typing.Self:
        return super().__new__(cls, *args, *kwargs)

    @typing.override
    def __init__(self, *args, **kwargs):
        super().__init__()

    @typing.override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{{\"{str(self)}\"}}"

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
