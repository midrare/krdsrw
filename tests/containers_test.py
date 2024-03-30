import typing

import pytest

from krdsrw.containers import DictBase
from krdsrw.containers import ListBase


class TestListBase:
    def test_instantiate(self):
        class CustomClass(ListBase[int]):
            pass

        o = CustomClass()  # no error
        assert o == []

        o = CustomClass([])  # no error
        assert o == []

        o = CustomClass([ 2, 4, 6, 8 ])  # no error
        assert o == [ 2, 4, 6, 8 ]

    def test_allowed(self):
        class CustomClass(ListBase[int]):
            @typing.override
            def _is_allowed(self, value: int) -> bool:
                return isinstance(value, int) and value % 2 == 0

        o = CustomClass([ 2, 4, 6, 8 ])  # no error

        o = CustomClass([ 2, 4, 6, 8 ])
        o[1] = 12  # no error

        o = CustomClass([ 2, 4, 6, 8 ])
        with pytest.raises(ValueError):
            o[1] = 7

        o = CustomClass()
        o.append(8)  # no error

        o = CustomClass()
        with pytest.raises(ValueError):
            o.append('ABC')

        o = CustomClass()
        with pytest.raises(ValueError):
            o.append(9)

    def test_transform(self):
        class CustomClass(ListBase[int]):
            @typing.override
            def _transform(self, value: int) -> int:
                return value**2

        o = CustomClass()
        o.append(8)
        assert o == [64]

        o = CustomClass([ 2, 4, 6, 8 ])
        assert o == [ 4, 16, 36, 64 ]

        o = CustomClass([ 2, 4, 6, 8 ])
        o[1] = 12  # no error
        assert o == [ 4, 144, 36, 64 ]

    def test_modified(self):
        class CustomClass(ListBase[int]):
            pass

        o = CustomClass()
        assert not o.is_modified

        o = CustomClass()
        o.append(2)
        assert o.is_modified

        o = CustomClass([ 2, 4, 6, 8 ])
        assert not o.is_modified

        o = CustomClass([ 2, 4, 6, 8 ])
        o[1] = 24
        assert o.is_modified

    def test_chain(self):
        class CustomClass(ListBase[typing.Any]):
            pass

        o2 = CustomClass()
        o = CustomClass([o2])
        assert not o.is_modified
        assert not o2.is_modified

        o2 = CustomClass()
        o = CustomClass([o2])
        o.append(o2)
        assert not o2.is_modified
        assert o.is_modified

        o = CustomClass([ 1, 2, 3 ])
        o2 = CustomClass([ 4, 5, 6 ])
        o.append(o2)
        assert o == [ 1, 2, 3, [ 4, 5, 6 ] ]


class TestDictBase:
    def test_instantiate(self):
        o = DictBase()  # no error
        assert o == {}

        o = DictBase({})  # no error
        assert o == {}

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'a': 1, 'b': 2, 'c': 3 }

    def test_eq_operator(self):
        o = DictBase()
        assert o == {}

        o = DictBase({})
        assert o == {}

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'a': 1, 'b': 2, 'c': 3 }

        o = DictBase()
        o['x'] = -1
        o['y'] = -2
        o['z'] = -3
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({})
        o['x'] = -1
        o['y'] = -2
        o['z'] = -3
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o['x'] = -1
        o['y'] = -2
        o['z'] = -3
        assert o == { 'a': 1, 'b': 2, 'c': 3, 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase()
        o.update({ 'x': -1, 'y': -2, 'z': -3 })
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({})
        o.update({ 'x': -1, 'y': -2, 'z': -3 })
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.update({ 'x': -1, 'y': -2, 'z': -3 })
        assert o == { 'a': 1, 'b': 2, 'c': 3, 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase()
        o.setdefault('x', -1)
        o.setdefault('y', -2)
        o.setdefault('z', -3)
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({})
        o.setdefault('x', -1)
        o.setdefault('y', -2)
        o.setdefault('z', -3)
        assert o == { 'x': -1, 'y': -2, 'z': -3 }

        o = DictBase({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('x', -1)
        o.setdefault('y', -2)
        o.setdefault('z', -3)
        assert o == { 'a': 1, 'b': 2, 'c': 3, 'x': -1, 'y': -2, 'z': -3 }

    def test_or_operator(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _is_key_value_writable(
                self,
                key: typing.Any,
                value: typing.Any,
            ) -> bool:
                return isinstance(key, str) and isinstance(value, int)

        o = CustomClass({ 'a': 123 }) | { 'b': 456 }  # no error
        with pytest.raises(ValueError):
            o = CustomClass({ 'a': 123 }) | { 'b': b'ZZZ'}

        o = { 'float': 1.23 } | CustomClass({ 'int': 456 })
        o = { 'bytes': b'ZZZ'} | CustomClass({ 'int': 456 })

        o = CustomClass({ 'a': 1 })
        o |= { 'b': 2 }

        with pytest.raises(ValueError):
            o = CustomClass({ 'a': 123 })
            o |= { 'b': b'ZZZ'}

        o = { 'float': 1.23 }
        o |= CustomClass({ 'int': 456 })

        o = { 'bytes': b'ZZZ'}
        o |= CustomClass({ 'int': 456 })

    def test_write_filter(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _is_key_value_writable(
                self,
                key: typing.Any,
                value: typing.Any,
            ) -> bool:
                return len(key) <= 1 and isinstance(value, int)

        CustomClass({ 'a': 1, 'b': 2, 'c': 3 })

        with pytest.raises(ValueError):
            CustomClass({ 'a': b'AAA', 'b': b'BBB', 'c': b'CustomClassC'})

        with pytest.raises(ValueError):
            CustomClass({ 'aa': 1, 'bb': 2, 'cc': 3 })

        o = CustomClass()
        o.setdefault('a', 9)
        assert o == { 'a': 9 }

        with pytest.raises(ValueError):
            o = CustomClass()
            o.setdefault('aa', 4)

        with pytest.raises(ValueError):
            o = CustomClass()
            o.setdefault('a', b'ZZZ')  # pyright: ignore  # type: ignore

        o = CustomClass()
        o.update({ 'a': 123, 'b': 456 })
        assert o == { 'a': 123, 'b': 456 }

        with pytest.raises(ValueError):
            o = CustomClass()
            o.update({
                'a': 12,
                'b': 4.5,  # pyright: ignore  # type: ignore
            })

    def test_write_transform(self):
        class CustomClass(DictBase[str, int]):
            @typing.override
            def _transform_key_value(
                self,
                key: typing.Any,
                value: typing.Any,
            ) -> tuple[str, int]:
                return key.capitalize(), value * 2

        o = CustomClass()
        assert o == {}

        o = CustomClass({})
        assert o == {}

        o = CustomClass({ 'a': 1 })
        assert o == { 'A': 2 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o == { 'A': 2, 'B': 4, 'C': 6 }

    def test_read_filter(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _is_key_readable(self, key: typing.Any) -> bool:
                return isinstance(key, str) and len(key) <= 1

        with pytest.raises(KeyError):
            o = CustomClass()
            o['a']

        o = CustomClass()
        assert o.get('a') is None

        o = CustomClass()
        assert o.get('a', 0) == 0

        with pytest.raises(KeyError):
            o = CustomClass()
            o['aa']

        with pytest.raises(KeyError):
            o = CustomClass()
            o.get('aa')

        with pytest.raises(KeyError):
            o = CustomClass()
            o.get('aa', 0)

    def test_read_transform(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _transform_key(self, key: typing.Any) -> typing.Any:
                if isinstance(key, str):
                    key = key.lower()
                return key

        with pytest.raises(KeyError):
            o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
            o['z']

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('A') == 1

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert o.get('B', 0) == 2

        with pytest.raises(KeyError):
            o = CustomClass()
            o['aa']

        o = CustomClass()
        assert o.get('aa') is None

        o = CustomClass()
        assert o.get('aa', 0) == 0

    def test_del_filter(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _is_key_deletable(self, key: typing.Any) -> typing.Any:
                return not isinstance(key, str) or not key.startswith('req_')

        with pytest.raises(KeyError):
            o = CustomClass()
            del o['a']

        with pytest.raises(KeyError):
            o = CustomClass()
            del o['req_a']

        with pytest.raises(KeyError):
            o = CustomClass({})
            del o['a']

        with pytest.raises(KeyError):
            o = CustomClass({})
            del o['req_a']

        o = CustomClass({ 'a': 1 })
        del o['a']

        with pytest.raises(KeyError):
            o = CustomClass({ 'req_a': 1 })
            del o['req_a']

        with pytest.raises(KeyError):
            o = CustomClass({ 'a': 1 })
            del o['req_a']

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        del o['a']

        with pytest.raises(KeyError):
            o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
            del o['req_a']

        with pytest.raises(KeyError):
            o = CustomClass({ 'req_a': 1, 'req_b': 2, 'req_c': 3 })
            del o['req_a']

    def test_del_transform(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _transform_key(self, key: typing.Any) -> typing.Any:
                if isinstance(key, str):
                    key = key.lower()
                return key

        with pytest.raises(KeyError):
            o = CustomClass()
            del o['a']

        with pytest.raises(KeyError):
            o = CustomClass()
            del o['A']

        with pytest.raises(KeyError):
            o = CustomClass({})
            del o['a']

        with pytest.raises(KeyError):
            o = CustomClass({})
            del o['A']

        o = CustomClass({ 'a': 1 })
        del o['a']
        assert o == {}

        o = CustomClass({ 'a': 1 })
        del o['A']
        assert o == {}

        o = CustomClass({ 'a': 1 })
        del o['A']
        assert o == {}

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        del o['a']
        assert o == { 'b': 2, 'c': 3 }

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        del o['A']
        assert o == { 'b': 2, 'c': 3 }

    def test_modified_hook(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            pass

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        assert not o.is_modified

        o = CustomClass()
        o.setdefault('a', 9)
        assert o.is_modified

        o = CustomClass({ 'a': 1, 'b': 2, 'c': 3 })
        o.setdefault('a', 9)
        assert not o.is_modified

        o = CustomClass()
        o.update({ 'a': 123, 'b': 456 })
        assert o.is_modified

    def test_chain_single_read(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = CustomClass()
        o['a0']
        assert o == {}

    def test_chain_single_write(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = CustomClass()
        o['a0'] = 'hello'
        assert o == { 'a0': 'hello'}

    def test_chain_nested_lvl2_read(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = CustomClass()
        o['a0']['b0']
        assert o == {}

    def test_chain_nested_lvl2_write(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = CustomClass()
        o['a0']['b0'] = 'hello'
        assert o == { 'a0': { 'b0': 'hello'} }

    def test_chain_nested_lvl3_read(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = CustomClass()
        o['a0']['b0']['c0']
        assert o == {}

    def test_chain_nested_lvl3_write(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = CustomClass()
        o['a0']['b0']['c0'] = 'hello'
        assert o == { 'a0': { 'b0': { 'c0': 'hello'} } }

    def test_chain_nested_lvl4_write(self):
        class CustomClass(DictBase[typing.Any, typing.Any]):
            @typing.override
            def _make_postulate(self, key: typing.Any) -> None | typing.Any:
                return self.__class__()

        o = CustomClass()
        o['a0']['b0']['c0'] = 'hello'
        o['a0']['b0']['c1'] = 'world'
        o['a0']['b1'] = 'lorem'
        o['a0']['b2'] = 'ipsum'
        o['a0']['b3']['c2']['d0']
        o['a0']['b3']['c2']['d1'] = True

        assert o == {
            'a0': {
                'b0': {
                    'c0': 'hello',
                    'c1': 'world',
                },
                'b1': 'lorem',
                'b2': 'ipsum',
                'b3': {
                    'c2': {
                        'd1': True,
                    }
                }
            },
        }
