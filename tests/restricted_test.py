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
        with pytest.raises(InvalidValueError):
            _List([ 1, 2, 3, 4 ])

    def test_append(self):
        o = _List()
        o.append(8)  # no error
        with pytest.raises(InvalidValueError):
            o.append('ABC')
        with pytest.raises(InvalidValueError):
            o.append(9)

    def test_read_index(self):
        o = _List([ 2, 4, 6, 8 ])
        assert o[1] == 16  # no error
        with pytest.raises(IndexError):
            o[99]

    def test_write_index(self):
        o = _List([ 2, 4, 6, 8 ])
        o[1] = 12  # no error
        with pytest.raises(InvalidValueError):
            o[1] = 7

    def test_modified(self):
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
    def _pre_default_filter(
        self,
        key: typing.Any,
        default: typing.Any,
    ) -> bool:
        if isinstance(key, str):
            key = key.lower()

        return key in self._schema \
        and (default is None or isinstance(default, self._schema[key]))

    @typing.override
    def _pre_default_transform(
        self: typing.Any,
        key: typing.Any,
        default: typing.Any,
    ) -> typing.Any:
        return default

    @typing.override
    def _pre_read_filter(self, key: typing.Any) -> bool:
        if isinstance(key, str):
            key = key.lower()
        return key in self._schema

    @typing.override
    def _pre_read_transform(self, key: typing.Any) -> typing.Any:
        if isinstance(key, str):
            key = key.lower()
        return key

    @typing.override
    def _pre_write_filter(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> bool:
        if isinstance(key, str):
            key = key.lower()
        return key in self._schema and isinstance(value, self._schema[key])

    @typing.override
    def _pre_write_transform(
        self,
        key: typing.Any,
        value: typing.Any,
    ) -> tuple[typing.Any, typing.Any]:
        if isinstance(key, str):
            key = key.lower()
        return key, value

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
        o = _Dict()  # no error
        assert o is not None

    def test_init(self):
        _Dict({ 'bool': True, 'int': 123, 'float': 123.456})  # no error

        with pytest.raises(InvalidValueError):
            _Dict({ 'a': b'AAA', 'b': b'BBB', 'c': b'CCC'})

    def test_setdefault(self):
        o = _Dict()
        o.setdefault('int', 789)  # no error
        with pytest.raises(InvalidValueError):
            o.setdefault('float', b'ZZZ')

    def test_update(self):
        o = _Dict()
        o.update({'int': 123, 'float': 123.456})  # no error

        with pytest.raises(InvalidValueError):
            o = _Dict()
            o.update({'int': b'ZZZ'})

    def test_add_operator(self):
        o = _Dict({'int': 123}) | {'float': 123.456} # no error
        with pytest.raises(InvalidValueError):
            o = _Dict({'int': 123}) | {'float': b'ZZZ'}

        o = {'float': 123.456} | _Dict({'int': 123})  # no error
        o = {'float': b'ZZZ'} | _Dict({'int': 123})  # no error

        o = _Dict({'int': 123})
        o |= {'float': 123.456} # no error
        with pytest.raises(InvalidValueError):
            o = _Dict({'int': 123})
            o |= {'float': b'ZZZ'}

        o = {'float': 123.456}
        o |= _Dict({'int': 123})  # no error

        o = {'float': b'ZZZ'}
        o |= _Dict({'int': 123})  # no error
