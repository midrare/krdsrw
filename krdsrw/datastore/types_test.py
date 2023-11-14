from . import cursor
from . import factory
from . import types


def test_bool_read():
    csr = cursor.Cursor(b'\x00\x01')
    o = csr.read_bool()
    assert o == True


def test_int_read():
    csr = cursor.Cursor(b'\x01\x00\xcc\x07\xc9')
    o = csr.read_int()
    assert o == 13371337


def test_long_read():
    csr = cursor.Cursor(b'\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9')
    o = csr.read_long()
    assert o == 1337133713371337


def test_utf8str_read():
    csr = cursor.Cursor(b'\x03\x00\x00\x03\x61\x62\x63')
    o = csr.read_utf8str()
    assert o == "abc"


def test_double_read():
    csr = cursor.Cursor(b'\x04\x01\x23\x34\x56\x78\x9a\xbc\xde')
    o = csr.read_double()
    assert o == 3.50054869405591e-303


def test_short_read():
    csr = cursor.Cursor(b'\x05\x05\x39')
    o = csr.read_short()
    assert o == 1337


def test_float_read():
    csr = cursor.Cursor(b'\x06\x01\x23\x34\x56')
    o = csr.read_float()
    assert o == 2.9975920941155183e-38


def test_byte_read():
    csr = cursor.Cursor(b'\x07\x46')
    o = csr.read_byte()
    assert o == 70


def test_char_read():
    csr = cursor.Cursor(b'\x09\x46')
    o = csr.read_char()
    assert o == 70


def test_bool_write():
    csr = cursor.Cursor()
    csr.write_bool(True)
    assert csr.dump() == b'\x00\x01'


def test_int_write():
    csr = cursor.Cursor()
    csr.write_int(13371337)
    assert csr.dump() == b'\x01\x00\xcc\x07\xc9'


def test_long_write():
    csr = cursor.Cursor()
    csr.write_long(1337133713371337)
    assert csr.dump() == b'\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9'


def test_utf8str_write():
    csr = cursor.Cursor()
    csr.write_utf8str("abc")
    assert csr.dump() == b'\x03\x00\x00\x03\x61\x62\x63'


def test_double_write():
    csr = cursor.Cursor()
    csr.write_double(3.50054869405591e-303)
    assert csr.dump() == b'\x04\x01\x23\x34\x56\x78\x9a\xbc\xde'


def test_short_write():
    csr = cursor.Cursor()
    csr.write_short(1337)
    assert csr.dump() == b'\x05\x05\x39'


def test_float_write():
    csr = cursor.Cursor()
    csr.write_float(2.9975920941155183e-38)
    assert csr.dump() == b'\x06\x01\x23\x34\x56'


def test_byte_write():
    csr = cursor.Cursor()
    csr.write_byte(70)
    assert csr.dump() == b'\x07\x46'


def test_char_write():
    csr = cursor.Cursor()
    csr.write_char(70)
    assert csr.dump() == b'\x09\x46'


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
