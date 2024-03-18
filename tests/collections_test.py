import os
import sys
import typing

import pytest

sys.path.insert(0, os.path.abspath(\
    os.path.join(os.path.dirname(__file__), '..')))
from krdsrw.containers import StrictList

sys.path.pop(0)


class _List(StrictList[int]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_modified: bool = False

    @typing.override
    def _pre_write_filter(self, value: int) -> bool:
        return isinstance(value, int) and value % 2 == 0

    @typing.override
    def _pre_write_transform(self, value: int) -> int:
        return value**2

    @typing.override
    def _post_write_hook(self):
        self.is_modified = True



class TestStrictList:
    def test_instantiate(self):
        o = _List()  # no error
        assert o is not None

    def test_init(self):
        _List([ 2, 4, 6, 8 ])  # no error
        with pytest.raises(TypeError):
            _List([ 1, 2, 3, 4 ])

    def test_append(self):
        o = _List()
        o.append(8)  # no error
        with pytest.raises(TypeError):
            o.append(9)

    def test_read_index(self):
        o = _List([ 2, 4, 6, 8 ])
        assert o[1] == 16  # no error
        with pytest.raises(IndexError):
            o[99]

    def test_write_index(self):
        o = _List([ 2, 4, 6, 8 ])
        o[1] = 12  # no error
        with pytest.raises(TypeError):
            o[1] = 7

    def test_modified(self):
        o = _List([ 2, 4, 6, 8 ])
        assert not o.is_modified
        o[1] = 24
        assert o.is_modified


