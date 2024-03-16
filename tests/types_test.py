import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from krdsrw import types
sys.path.pop(0)


def test_bool_cmp():
    o = types.Bool(True)
    assert o == True


def test_byte_cmp():
    o = types.Byte(0xab)
    assert o == 0xab


def test_char_cmp():
    o = types.Char(0xab)
    assert o == 0xab


def test_short_cmp():
    o = types.Short(1337)
    assert o == 1337


def test_int_cmp():
    o = types.Int(1337)
    assert o == 1337


def test_long_cmp():
    o = types.Long(1337)
    assert o == 1337


def test_float_cmp():
    o = types.Float(12.34)
    assert o == 12.34


def test_double_cmp():
    o = types.Double(12.34)
    assert o == 12.34


def test_utf8str_cmp():
    o = types.Utf8Str("foo")
    assert o == "foo"
