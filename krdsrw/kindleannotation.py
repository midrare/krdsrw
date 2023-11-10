# noinspection SpellCheckingInspection
_TEMPLATE: str = "0\ufffc0"


class KindleAnnotation:
    def __init__(self):
        self.created_epoch_milli: int = -1
        self.last_modified_epoch_milli: int = -1
        self.start_offset: int = -1
        self.end_offset: int = -1
        self.chunk_eid: int = -1
        self.chunk_pos: int = -1
        self.note: None | str = None

    def is_offsets_valid(self) -> bool:
        return 0 <= self.start_offset <= self.end_offset

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}{{@{self.start_offset}:{self.end_offset}%s}}"
            % (
                ' "' + self.note +
                '"' if self.note and not self.note.isspace() else ""
            )
        )
