class KRDSRWError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)


class UnexpectedStructureError(KRDSRWError):
    def __init__(self, *args: str, pos: int = -1):
        args_ = list(args)
        if pos >= 0:
            args_ = [f"@{pos}"] + list(args)
        super().__init__(" ".join(args_))


class UnexpectedBytesError(KRDSRWError):
    def __init__(
        self,
        pos: int,
        expected: int | bytes | tuple[int | bytes, ...] | list[int | bytes],
        actual: None | int | bytes = None,
    ):
        s = f"@{pos} expected "
        if isinstance(expected, tuple) or isinstance(expected, list):
            s += "[ "
            s += ", ".join([self._to_hex(e) for e in expected])
            s += "] "
        else:
            s += f"{self._to_hex(expected)} "

        if actual is None:
            s += "but not found."
        else:
            s += f"but got {self._to_hex(actual)}."

        super().__init__(s)

        self._pos: int = pos
        self._expected: list[int | bytes] = list(expected) \
                if isinstance(expected, (list, tuple)) else [expected]
        self._actual: None | int | bytes = actual

    @classmethod
    def _to_hex(cls, data: int | bytes, prefix: bool = True) -> str:
        if isinstance(data, int):
            return cls._int_to_hex(data, prefix)
        return cls._bytes_to_hex(data, prefix)

    @staticmethod
    def _int_to_hex(data: int, prefix: bool = True) -> str:
        return ("0x" if prefix else "") + f"{data:02x}"

    @staticmethod
    def _bytes_to_hex(data: bytes, prefix: bool = True) -> str:
        s = ''
        if prefix:
            s += '0x'
        for b in data:
            s += f"{b:02x}"
        return s

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def expected(self) -> list[int | bytes]:
        return self._expected

    @property
    def actual(self) -> None | int | bytes:
        return self._actual
