import os
import sys
import typing

import pytest

sys.path.insert(0, os.path.abspath(\
    os.path.join(os.path.dirname(__file__), '..')))
from krdsrw.restricted import RestrictedDict
from krdsrw.restricted import RestrictedList
from krdsrw.restricted import RestrictionError
from krdsrw.restricted import InvalidKeyError
from krdsrw.restricted import InvalidValueError

sys.path.pop(0)


class _List(RestrictedList[int]):
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


class TestRestrictedList:
    def test_instantiate(self):
        o = _List()  # no error
        assert o is not None

    def test_init(self):
        _List([ 2, 4, 6, 8 ])  # no error
        with pytest.raises(ValueError):
            _List([ 1, 2, 3, 4 ])

    def test_append(self):
        o = _List()
        o.append(8)  # no error
        with pytest.raises(ValueError):
            o.append('ABC')
        with pytest.raises(ValueError):
            o.append(9)

    def test_read_index(self):
        o = _List([ 2, 4, 6, 8 ])
        assert o[1] == 16  # no error
        with pytest.raises(IndexError):
            o[99]

    def test_write_index(self):
        o = _List([ 2, 4, 6, 8 ])
        o[1] = 12  # no error
        with pytest.raises(ValueError):
            o[1] = 7

    def test_modified(self):
        o = _List()
        assert not o.is_modified
        o.append(2)
        assert o.is_modified

        o = _List([ 2, 4, 6, 8 ])
        assert not o.is_modified
        o[1] = 24
        assert o.is_modified


class _Dict(RestrictedDict[typing.Any, typing.Any]):
    def __init__(self, *args, **kwargs):
        self._schema: typing.Final[dict[typing.Any, type]] = {
            'bool': bool,
            'int': int,
            'float': float,
        }
        super().__init__(*args, **kwargs)
        self.is_modified: bool = False

    @typing.override
    def _pre_del_filter(self, key: typing.Any) -> bool:
        if isinstance(key, str):
            key = key.lower()
        return key in self._schema

    @typing.override
    def _pre_del_transform(self, key: typing.Any) -> typing.Any:
        if isinstance(key, str):
            key = key.lower()
        return key

    @typing.override
    def _post_write_hook(self):
        self.is_modified = True


class TestRestrictedDict:
    def test_instantiate(self):
        o = RestrictedDict()  # no error
        assert o is not None

    def test_eq_operator(self):
        o = RestrictedDict()
        assert o == {}

        o = RestrictedDict({})
        assert o == {}

        o = RestrictedDict({ 'a': 'A'})
        assert o == { 'a': 'A'}

        o = RestrictedDict({ 'a': 'A', 'b': 'B', 'c': 'C'})
        assert o == { 'a': 'A', 'b': 'B', 'c': 'C'}

    def test_or_operator(self):
        class CC(RestrictedDict[str, int]):
            @typing.override
            def _pre_write_filter(
                self,
                key: typing.Any,
                value: typing.Any,
            ) -> bool:
                return isinstance(key, str) and isinstance(value, int)

        o = CC({ 'a': 123 }) | { 'b': 456 }  # no error
        with pytest.raises(ValueError):
            o = CC({ 'a': 123 }) | { 'b': b'ZZZ'}

        o = { 'float': 1.23 } | CC({ 'int': 456 })
        o = { 'bytes': b'ZZZ'} | CC({ 'int': 456 })

        o = CC({ 'a': 1 })
        o |= { 'b': 2 }

        with pytest.raises(ValueError):
            o = CC({ 'a': 123 })
            o |= { 'b': b'ZZZ'}

        o = { 'float': 1.23 }
        o |= CC({ 'int': 456 })

        o = { 'bytes': b'ZZZ'}
        o |= CC({ 'int': 456 })

    def test_write_filter(self):
        class CC(RestrictedDict[str, int]):
            @typing.override
            def _pre_write_filter(
                self,
                key: typing.Any,
                value: typing.Any,
            ) -> bool:
                return len(key) <= 1 and isinstance(value, int)

        CC({ 'a': 1, 'b': 2, 'c': 3 })

        with pytest.raises(ValueError):
            CC({ 'a': b'AAA', 'b': b'BBB', 'c': b'CCC'})

        with pytest.raises(ValueError):
            CC({ 'aa': 1, 'bb': 2, 'cc': 3 })

        o = CC()
        o.setdefault('a', 9)
        assert o == { 'a': 9 }

        with pytest.raises(ValueError):
            o = CC()
            o.setdefault('aa', 4)

        with pytest.raises(ValueError):
            o = CC()
            o.setdefault('a', b'ZZZ')  # pyright: ignore  # type: ignore

        o = CC()
        o.update({'a': 123, 'b': 456})
        assert o == {'a': 123, 'b': 456}

        with pytest.raises(ValueError):
            o = CC()
            o.update({
                'a': 12,
                'b': 4.5,   # pyright: ignore  # type: ignore
            })

    def test_write_transform(self):
        class CC(RestrictedDict[str, int]):
            @typing.override
            def _pre_write_transform(
                self,
                key: typing.Any,
                value: typing.Any,
            ) -> tuple[str, int]:
                return key.capitalize(), value * 2

        o = CC()
        assert o == {}

        o = CC({})
        assert o == {}

        o = CC({ 'a': 1 })
        assert o == { 'A': 2 }

        o = CC({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'A': 2, 'B': 4, 'C': 6 }

    def test_read_filter(self):
        class CC(RestrictedDict[typing.Any, typing.Any]):
            @typing.override
            def _pre_read_filter(self, key: typing.Any) -> bool:
                return isinstance(key, str) and len(key) <= 1

        with pytest.raises(KeyError):
            o = CC()
            o['a']

        o = CC()
        assert o.get('a') is None

        o = CC()
        assert o.get('a', 0) == 0

        with pytest.raises(KeyError):
            o = CC()
            o['aa']

        with pytest.raises(KeyError):
            o = CC()
            o.get('aa')

        with pytest.raises(KeyError):
            o = CC()
            o.get('aa', 0)

    def test_read_transform(self):
        class CC(RestrictedDict[typing.Any, typing.Any]):
            @typing.override
            def _pre_read_transform(self, key: typing.Any) -> typing.Any:
                if isinstance(key, str):
                    key = key.lower()
                return key


        with pytest.raises(KeyError):
            o = CC({'a': 1, 'b': 2, 'c': 3})
            o['z']

        o = CC({'a': 1, 'b': 2, 'c': 3})
        assert o.get('A') == 1

        o = CC({'a': 1, 'b': 2, 'c': 3})
        assert o.get('B', 0) == 2

        with pytest.raises(KeyError):
            o = CC()
            o['aa']

        o = CC()
        assert o.get('aa') is None

        o = CC()
        assert o.get('aa', 0) == 0
