import pytest

from .cursor import Cursor
from .cursor import Int
from .cursor import ValueFactory
from .containers import Array
from .containers import DynamicMap


def test_val_factory_create():
    o = ValueFactory(Int, 1337)
    assert o.create() == 1337


def test_val_factory_read():
    o = ValueFactory(Int)
    csr = Cursor(b'\x01\x00\xcc\x07\xc9')
    assert o.create(csr) == 13371337


def test_val_factory_is_basic():
    o = ValueFactory(Int)
    assert o.is_basic()


def test_array_init():
    fact = ValueFactory(Int)
    o = Array(fact)
    assert o.cls_ == Int


def test_array_append_type_check_allow():
    o = Array(ValueFactory(Int))
    o.append(1337)
    assert o[0] == 1337


def test_array_append_type_check_disallow():
    o = Array(ValueFactory(Int))
    with pytest.raises(TypeError):
        o.append("foo")


def test_array_insert_type_check_allow():
    o = Array(ValueFactory(Int))
    o.insert(0, 1337)
    assert o[0] == 1337


def test_array_insert_type_check_disallow():
    o = Array(ValueFactory(Int))
    with pytest.raises(TypeError):
        o.insert(0, "foo")


def test_array_extend_type_check_allow():
    o = Array(ValueFactory(Int))
    o.extend([ 0, 1, 2, 3, 4 ])
    assert o == [ 0, 1, 2, 3, 4 ]


def test_array_extend_type_check_disallow():
    o = Array(ValueFactory(Int))
    with pytest.raises(TypeError):
        o.extend([ "a", "b", "c", "d", "e"])


def test_array_copy_contents():
    o = Array(ValueFactory(Int))
    o.extend([ 0, 1, 2, 3, 4 ])
    o2 = o.copy()
    assert isinstance(o2, Array) and o2 == o


def test_array_count():
    o = Array(ValueFactory(Int))
    o.extend([ 0, 1, 2, 3, 4 ])
    assert o.count(2) == 1


def test_array_read():
    o = Array(ValueFactory(Int))
    csr = Cursor(
        b'\x01\x00\x00\x00\x03' + b'\x01\x00\x00\x00\x0a'
        + b'\x01\x00\x00\x00\x0b' + b'\x01\x00\x00\x00\x0c')
    o.read(csr)
    assert o == [ 0x0a, 0x0b, 0x0c ]


def test_array_write():
    o = Array(ValueFactory(Int))
    o.extend([ 0x0a, 0x0b, 0x0c ])
    csr = Cursor()
    o.write(csr)
    assert csr.dump() == b'\x01\x00\x00\x00\x03' \
        + b'\x01\x00\x00\x00\x0a' \
        + b'\x01\x00\x00\x00\x0b' \
        + b'\x01\x00\x00\x00\x0c'


def test_dynamic_map_put_key_allow():
    o = DynamicMap(str, ValueFactory(Int))
    o['a'] = 0x0a
    assert o == { 'a': 0x0a }


def test_dynamic_map_put_key_disallow():
    o = DynamicMap(str, ValueFactory(Int))
    with pytest.raises(TypeError):
        o[777] = 0x0a  # type: ignore
