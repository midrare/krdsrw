from krdsrw.basics import Bool
from krdsrw.basics import Byte
from krdsrw.basics import Char
from krdsrw.basics import Short
from krdsrw.basics import Int
from krdsrw.basics import Long
from krdsrw.basics import Float
from krdsrw.basics import Double
from krdsrw.basics import Utf8Str


def test_bool_cmp():
    o = Bool(True)
    assert o == True


def test_byte_cmp():
    o = Byte(0xab)
    assert o == 0xab


def test_char_cmp():
    o = Char(0xab)
    assert o == 0xab


def test_short_cmp():
    o = Short(1337)
    assert o == 1337


def test_int_cmp():
    o = Int(1337)
    assert o == 1337


def test_long_cmp():
    o = Long(1337)
    assert o == 1337


def test_float_cmp():
    o = Float(12.34)
    assert o == 12.34


def test_double_cmp():
    o = Double(12.34)
    assert o == 12.34


def test_utf8str_cmp():
    o = Utf8Str("foo")
    assert o == "foo"
