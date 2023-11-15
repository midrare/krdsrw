from . import cursor


def test_cursor_init():
    csr = cursor.Cursor()
    assert csr.dump() == b''


def test_cursor_dump():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.dump() == b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def test_cursor_load():
    csr = cursor.Cursor()
    csr.load(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.dump() == b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def test_cursor_read():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.read(4) == b'ABCD'


def test_cursor_tell():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.tell() == 0


def test_cursor_seek():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.seek(8)
    assert csr.tell() == 8 and csr.read(1) == b'I'


def test_cursor_skip():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.seek(4)
    csr.skip(4)
    assert csr.read(1) == b'I'


def test_cursor_eat():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.seek(8)
    assert csr.eat(b'IJKL') and csr.tell() == 12


def test_cursor_peek():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.seek(8)
    assert csr.peek() == 73 and csr.tell() == 8


def test_cursor_peek_matches():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.seek(8)
    assert csr.peek_matches(b'IJKL') is True


def test_cursor_write():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.seek(8)
    csr.write(b'0123')
    assert csr.dump() == b'ABCDEFGH0123MNOPQRSTUVWXYZ'


def test_cursor_is_at_end():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.seek(25)
    assert csr.is_at_end() is True


def test_cursor_save():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.save()
    csr.seek(16)
    csr.restore()
    assert csr.tell() == 0


def test_cursor_unsave():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.save()
    csr.seek(8)
    csr.save()
    csr.seek(16)
    csr.unsave()
    csr.restore()
    assert csr.tell() == 0


def test_cursor_read_bool():
    csr = cursor.Cursor(b'\x00\x01')
    assert csr.read_bool() == True


def test_cursor_read_int():
    csr = cursor.Cursor(b'\x01\x00\xcc\x07\xc9')
    assert csr.read_int() == 13371337


def test_cursor_read_long():
    csr = cursor.Cursor(b'\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9')
    assert csr.read_long() == 1337133713371337


def test_cursor_read_utf8str():
    csr = cursor.Cursor(b'\x03\x00\x00\x03\x61\x62\x63')
    assert csr.read_utf8str() == "abc"


def test_cursor_read_double():
    csr = cursor.Cursor(b'\x04\x01\x23\x34\x56\x78\x9a\xbc\xde')
    assert csr.read_double() == 3.50054869405591e-303


def test_cursor_read_short():
    csr = cursor.Cursor(b'\x05\x05\x39')
    assert csr.read_short() == 1337


def test_cursor_read_float():
    csr = cursor.Cursor(b'\x06\x01\x23\x34\x56')
    assert csr.read_float() == 2.9975920941155183e-38


def test_cursor_read_byte():
    csr = cursor.Cursor(b'\x07\x46')
    assert csr.read_byte() == 70


def test_cursor_read_char():
    csr = cursor.Cursor(b'\x09\x46')
    assert csr.read_char() == 70


def test_cursor_write_bool():
    csr = cursor.Cursor()
    csr.write_bool(True)
    assert csr.dump() == b'\x00\x01'


def test_cursor_write_int():
    csr = cursor.Cursor()
    csr.write_int(13371337)
    assert csr.dump() == b'\x01\x00\xcc\x07\xc9'


def test_cursor_write_long():
    csr = cursor.Cursor()
    csr.write_long(1337133713371337)
    assert csr.dump() == b'\x02\x00\x04\xc0\x1d\xb4\x00\xb0\xc9'


def test_cursor_write_utf8str():
    csr = cursor.Cursor()
    csr.write_utf8str("abc")
    assert csr.dump() == b'\x03\x00\x00\x03\x61\x62\x63'


def test_cursor_write_double():
    csr = cursor.Cursor()
    csr.write_double(3.50054869405591e-303)
    assert csr.dump() == b'\x04\x01\x23\x34\x56\x78\x9a\xbc\xde'


def test_cursor_write_short():
    csr = cursor.Cursor()
    csr.write_short(1337)
    assert csr.dump() == b'\x05\x05\x39'


def test_cursor_write_float():
    csr = cursor.Cursor()
    csr.write_float(2.9975920941155183e-38)
    assert csr.dump() == b'\x06\x01\x23\x34\x56'


def test_cursor_write_byte():
    csr = cursor.Cursor()
    csr.write_byte(70)
    assert csr.dump() == b'\x07\x46'


def test_cursor_write_char():
    csr = cursor.Cursor()
    csr.write_char(70)
    assert csr.dump() == b'\x09\x46'


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
    o = cursor.Bool(True)
    assert o == True


def test_byte_cmp():
    o = cursor.Byte(0xab)
    assert o == 0xab


def test_char_cmp():
    o = cursor.Char(0xab)
    assert o == 0xab


def test_short_cmp():
    o = cursor.Short(1337)
    assert o == 1337


def test_int_cmp():
    o = cursor.Int(1337)
    assert o == 1337


def test_long_cmp():
    o = cursor.Long(1337)
    assert o == 1337


def test_float_cmp():
    o = cursor.Float(12.34)
    assert o == 12.34


def test_double_cmp():
    o = cursor.Double(12.34)
    assert o == 12.34


def test_utf8str_cmp():
    o = cursor.Utf8Str("foo")
    assert o == "foo"
