import pytest

from krdsrw.cursor import Cursor
from krdsrw.basics import Basic
from krdsrw.basics import Bool
from krdsrw.basics import Int
from krdsrw.basics import Long
from krdsrw.basics import Float
from krdsrw.basics import Double
from krdsrw.basics import Utf8Str
from krdsrw.specs import Spec
from krdsrw.specs import Index
from krdsrw.specs import Field
from krdsrw.objects import Array
from krdsrw.objects import DynamicMap
from krdsrw.objects import Record


class TestSpec:
    def test_create(self):
        o = Spec(Int, 1337)
        assert o.make() == 1337

    def test_read(self):
        o = Spec(Int)
        csr = Cursor(b'\x01\x00\xcc\x07\xc9')
        assert o.read(csr) == 13371337

    def test_write(self):
        spc = Spec(Int)
        o = spc.make(13371337)
        csr = Cursor()
        o._write(csr)
        assert csr.dump() == b'\x01\x00\xcc\x07\xc9'

    def test_is_basic(self):
        o = Spec(Int)
        assert issubclass(o.cls_, Basic)

    def test_cls(self):
        o = Spec(Int)
        assert o.cls_ == Int

    def test_make(self):
        spc = Spec(Int)
        assert spc.make(1337) == 1337

    def test_is_compatible(self):
        spc = Spec(Int)
        assert spc.is_compatible(Int) is True
        assert spc.is_compatible(int) is True
        assert spc.is_compatible(Float) is False
        assert spc.is_compatible(float) is False
