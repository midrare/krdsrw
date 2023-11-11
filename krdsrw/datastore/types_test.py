from . import cursor
from . import types


def test_bool_read():
    csr = cursor.Cursor(b'\x00\x01')
    o = types.Bool()
    o.read(csr)
    assert o.value is True


def test_int_read():
    csr = cursor.Cursor(b'\x01\x00\xcc\x07\xc9')
    o = types.Int()
    o.read(csr)
    assert o.value == 13371337


def test_long_read():
    csr = cursor.Cursor(b'\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9')
    o = types.Long()
    o.read(csr)
    assert o.value == 1337133713371337


def test_utf8str_read():
    csr = cursor.Cursor(b'\x03\x00\x00\x03\x61\x62\x63')
    o = types.Utf8Str()
    o.read(csr)
    assert o.value == "abc"


def test_double_read():
    csr = cursor.Cursor(b'\x04\x01\x23\x34\x56\x78\x9a\xbc\xde')
    o = types.Double()
    o.read(csr)
    assert o.value == 3.50054869405591e-303


def test_short_read():
    csr = cursor.Cursor(b'\x05\x05\x39')
    o = types.Short()
    o.read(csr)
    assert o.value == 1337


def test_float_read():
    csr = cursor.Cursor(b'\x06\x01\x23\x34\x56')
    o = types.Float()
    o.read(csr)
    assert o.value == 2.9975920941155183e-38


def test_byte_read():
    csr = cursor.Cursor(b'\x07\x46')
    o = types.Byte()
    o.read(csr)
    assert o.value == 70


def test_char_read():
    csr = cursor.Cursor(b'\x09\x46')
    o = types.Char()
    o.read(csr)
    assert o.value == 70


def test_bool_write():
    csr = cursor.Cursor()
    o = types.Bool(True)
    o.write(csr)
    assert csr.dump() == b'\x00\x01'


def test_int_write():
    csr = cursor.Cursor()
    o = types.Int(13371337)
    o.write(csr)
    assert csr.dump() == b'\x01\x00\xcc\x07\xc9'


def test_long_write():
    csr = cursor.Cursor()
    o = types.Long(1337133713371337)
    o.write(csr)
    assert csr.dump() == b'\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9'


def test_utf8str_write():
    csr = cursor.Cursor()
    o = types.Utf8Str("abc")
    o.write(csr)
    assert csr.dump() == b'\x03\x00\x00\x03\x61\x62\x63'


def test_double_write():
    csr = cursor.Cursor()
    o = types.Double(3.50054869405591e-303)
    o.write(csr)
    assert csr.dump() == b'\x04\x01\x23\x34\x56\x78\x9a\xbc\xde'


def test_short_write():
    csr = cursor.Cursor()
    o = types.Short(1337)
    o.write(csr)
    assert csr.dump() == b'\x05\x05\x39'


def test_float_write():
    csr = cursor.Cursor()
    o = types.Float(2.9975920941155183e-38)
    o.write(csr)
    assert csr.dump() == b'\x06\x01\x23\x34\x56'


def test_byte_write():
    csr = cursor.Cursor()
    o = types.Byte(70)
    o.write(csr)
    assert csr.dump() == b'\x07\x46'


def test_char_write():
    csr = cursor.Cursor()
    o = types.Char(70)
    o.write(csr)
    assert csr.dump() == b'\x09\x46'
