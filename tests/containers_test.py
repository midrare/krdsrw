import pytest

from krdsrw.cursor import Cursor
from krdsrw.types import Int
from krdsrw.types import Spec
from krdsrw.containers import Array
from krdsrw.containers import DynamicMap


class TestSpec:
    def test_create(self):
        o = Spec(Int, 1337)
        assert o.make() == 1337

    def test_read(self):
        o = Spec(Int)
        csr = Cursor(b'\x01\x00\xcc\x07\xc9')
        assert o.read(csr) == 13371337

    def test_is_basic(self):
        o = Spec(Int)
        assert o.is_basic()


class TestArray:
    def test_init(self):
        fact = Spec(Int)
        o = Array(_schema_array_elmt_spec=fact)
        assert o.elmt_cls == Int

    def test_append_type_check_allow(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        o.append(1337)
        assert o[0] == 1337

    def test_append_type_check_disallow(self):
        o = Array(Spec(Int))
        with pytest.raises(ValueError):
            o.append("foo")

    def test_insert_type_check_allow(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        o.insert(0, 1337)
        assert o[0] == 1337

    def test_insert_type_check_disallow(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        with pytest.raises(ValueError):
            o.insert(0, "foo")

    def test_extend_type_check_allow(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        o.extend([ 0, 1, 2, 3, 4 ])
        assert o == [ 0, 1, 2, 3, 4 ]

    def test_extend_type_check_disallow(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        with pytest.raises(ValueError):
            o.extend([ "a", "b", "c", "d", "e"])

    def test_copy_contents(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        o.extend([ 0, 1, 2, 3, 4 ])
        o2 = o.copy()
        assert isinstance(o2, Array) and o2 == o

    def test_count(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        o.extend([ 0, 1, 2, 3, 4 ])
        assert o.count(2) == 1

    def test_read(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        csr = Cursor(
            b'\x01\x00\x00\x00\x03' + b'\x01\x00\x00\x00\x0a'
            + b'\x01\x00\x00\x00\x0b' + b'\x01\x00\x00\x00\x0c')
        o.read(csr)
        assert o == [ 0x0a, 0x0b, 0x0c ]

    def test_write(self):
        o = Array(_schema_array_elmt_spec=Spec(Int))
        o.extend([ 0x0a, 0x0b, 0x0c ])
        csr = Cursor()
        o.write(csr)
        assert csr.dump() == b'\x01\x00\x00\x00\x03' \
            + b'\x01\x00\x00\x00\x0a' \
            + b'\x01\x00\x00\x00\x0b' \
            + b'\x01\x00\x00\x00\x0c'


def test_dynamic_map_put_key():
    o = DynamicMap()
    o['a'] = Int(0x0a)
    with pytest.raises(ValueError):
        o['a'] = 0x0a  # type: ignore
