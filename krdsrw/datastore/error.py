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


class UnexpectedDataTypeError(Exception):
    def __init__(self, pos: int, expected: int, actual: None | int):
        super().__init__(
            "@%d expected data type indicator byte with value of 0x%02x but got %s"
            % (
                pos,
                expected,
                hex(actual) if isinstance(actual,
                                          int) else str(actual),
            )
        )
        self.pos: int = pos
        self.expected: int = expected
        self.actual: None | int = actual
