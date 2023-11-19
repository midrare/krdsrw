class NameNotSupportedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UnexpectedNameError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DemarcationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FieldNotFoundError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)


class UnexpectedFieldError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)


class MagicStrNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UnexpectedBytesError(Exception):
    def __init__(
            self, pos: int, expected: int | bytes, actual: None | int | bytes):
        s = f"@{pos} expected "
        s += f"0x{expected:02x} " if isinstance(
            expected, int) else f"{str(bytes)} "

        if actual is None:
            s += "but not found."
        else:
            s += f"but got "
            s += f"0x{actual:02x}" if isinstance(
                actual, int) else f"{str(actual)}"
            s += "."

        super().__init__(s)

        self._pos: int = pos
        self._expected: int | bytes = expected
        self._actual: None | int | bytes = actual

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def expected(self) -> int | bytes:
        return self._expected

    @property
    def actual(self) -> None | int | bytes:
        return self._actual
