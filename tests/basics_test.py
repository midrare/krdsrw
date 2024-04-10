from krdsrw.basics import Bool
from krdsrw.basics import Byte
from krdsrw.basics import Char
from krdsrw.basics import Short
from krdsrw.basics import Int
from krdsrw.basics import Long
from krdsrw.basics import Float
from krdsrw.basics import Double
from krdsrw.basics import Utf8Str
from krdsrw.basics import read_bool
from krdsrw.basics import write_bool
from krdsrw.basics import read_byte
from krdsrw.basics import write_byte
from krdsrw.basics import read_char
from krdsrw.basics import write_char
from krdsrw.basics import read_short
from krdsrw.basics import write_short
from krdsrw.basics import read_int
from krdsrw.basics import write_int
from krdsrw.basics import read_long
from krdsrw.basics import write_long
from krdsrw.basics import read_float
from krdsrw.basics import write_float
from krdsrw.basics import read_double
from krdsrw.basics import write_double
from krdsrw.basics import read_utf8str
from krdsrw.basics import write_utf8str
from krdsrw.cursor import Cursor


def test_bool_cmp():
    o = Bool(True)
    assert o == True


def test_byte_cmp():
    o = Byte(0xAB)
    assert o == 0xAB


def test_char_cmp():
    o = Char(0xAB)
    assert o == 0xAB


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


def test_cursor_read_bool():
    csr = Cursor(b"\x00\x01")
    assert read_bool(csr) == True


def test_cursor_read_int():
    csr = Cursor(b"\x01\x00\xcc\x07\xc9")
    assert read_int(csr) == 13371337


def test_cursor_read_long():
    csr = Cursor(b"\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9")
    assert read_long(csr) == 1337133713371337


def test_cursor_read_utf8str():
    csr = Cursor(b"\x03\x00\x00\x03\x61\x62\x63")
    assert read_utf8str(csr) == "abc"


def test_cursor_read_double():
    csr = Cursor(b"\x04\x01\x23\x34\x56\x78\x9a\xbc\xde")
    assert read_double(csr) == 3.50054869405591e-303


def test_cursor_read_short():
    csr = Cursor(b"\x05\x05\x39")
    assert read_short(csr) == 1337


def test_cursor_read_float():
    csr = Cursor(b"\x06\x01\x23\x34\x56")
    assert read_float(csr) == 2.9975920941155183e-38


def test_cursor_read_byte():
    csr = Cursor(b"\x07\x46")
    assert read_byte(csr) == 70


def test_cursor_read_char():
    csr = Cursor(b"\x09\x46")
    assert read_char(csr) == 70


def test_cursor_write_bool():
    csr = Cursor()
    write_bool(csr, True)
    assert csr.dump() == b"\x00\x01"


def test_cursor_write_int():
    csr = Cursor()
    write_int(csr, 13371337)
    assert csr.dump() == b"\x01\x00\xcc\x07\xc9"


def test_cursor_write_long():
    csr = Cursor()
    write_long(csr, 1337133713371337)
    assert csr.dump() == b"\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9"


def test_cursor_write_utf8str():
    csr = Cursor()
    write_utf8str(csr, "abc")
    assert csr.dump() == b"\x03\x00\x00\x03\x61\x62\x63"


def test_cursor_write_double():
    csr = Cursor()
    write_double(csr, 3.50054869405591e-303)
    assert csr.dump() == b"\x04\x01\x23\x34\x56\x78\x9a\xbc\xde"


def test_cursor_write_short():
    csr = Cursor()
    write_short(csr, 1337)
    assert csr.dump() == b"\x05\x05\x39"


def test_cursor_write_float():
    csr = Cursor()
    write_float(csr, 2.9975920941155183e-38)
    assert csr.dump() == b"\x06\x01\x23\x34\x56"


def test_cursor_write_byte():
    csr = Cursor()
    write_byte(csr, 70)
    assert csr.dump() == b"\x07\x46"


def test_cursor_write_char():
    csr = Cursor()
    write_char(csr, 70)
    assert csr.dump() == b"\x09\x46"


def test_bool_read():
    csr = Cursor(b"\x00\x01")
    o = read_bool(csr)
    assert o == True


def test_int_read():
    csr = Cursor(b"\x01\x00\xcc\x07\xc9")
    o = read_int(csr)
    assert o == 13371337


def test_long_read():
    csr = Cursor(b"\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9")
    o = read_long(csr)
    assert o == 1337133713371337


def test_utf8str_read():
    csr = Cursor(b"\x03\x00\x00\x03\x61\x62\x63")
    o = read_utf8str(csr)
    assert o == "abc"


def test_double_read():
    csr = Cursor(b"\x04\x01\x23\x34\x56\x78\x9a\xbc\xde")
    o = read_double(csr)
    assert o == 3.50054869405591e-303


def test_short_read():
    csr = Cursor(b"\x05\x05\x39")
    o = read_short(csr)
    assert o == 1337


def test_float_read():
    csr = Cursor(b"\x06\x01\x23\x34\x56")
    o = read_float(csr)
    assert o == 2.9975920941155183e-38


def test_byte_read():
    csr = Cursor(b"\x07\x46")
    o = read_byte(csr)
    assert o == 70


def test_char_read():
    csr = Cursor(b"\x09\x46")
    o = read_char(csr)
    assert o == 70


def test_bool_write():
    csr = Cursor()
    write_bool(csr, True)
    assert csr.dump() == b"\x00\x01"


def test_int_write():
    csr = Cursor()
    write_int(csr, 13371337)
    assert csr.dump() == b"\x01\x00\xcc\x07\xc9"


def test_long_write():
    csr = Cursor()
    write_long(csr, 1337133713371337)
    assert csr.dump() == b"\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9"


def test_utf8str_write():
    csr = Cursor()
    write_utf8str(csr, "abc")
    assert csr.dump() == b"\x03\x00\x00\x03\x61\x62\x63"


def test_double_write():
    csr = Cursor()
    write_double(csr, 3.50054869405591e-303)
    assert csr.dump() == b"\x04\x01\x23\x34\x56\x78\x9a\xbc\xde"


def test_short_write():
    csr = Cursor()
    write_short(csr, 1337)
    assert csr.dump() == b"\x05\x05\x39"


def test_float_write():
    csr = Cursor()
    write_float(csr, 2.9975920941155183e-38)
    assert csr.dump() == b"\x06\x01\x23\x34\x56"


def test_byte_write():
    csr = Cursor()
    write_byte(csr, 70)
    assert csr.dump() == b"\x07\x46"


def test_char_write():
    csr = Cursor()
    write_char(csr, 70)
    assert csr.dump() == b"\x09\x46"
