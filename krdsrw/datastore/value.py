from __future__ import annotations
import abc

from .cursor import Cursor


class Value(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self, cursor: Cursor):
        raise NotImplementedError(
            "This method must be implemented by the subclass."
        )

    @abc.abstractmethod
    def write(self, cursor: Cursor):
        raise NotImplementedError(
            "This method must be implemented by the subclass."
        )

    @abc.abstractmethod
    def __eq__(self, other: Value) -> bool:
        raise NotImplementedError(
            "This method must be implemented by the subclass."
        )
