import os
import sys

from krdsrw import cursor


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
    assert csr.peek(1) == b'I' and csr.tell() == 8


def test_cursor_skip():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.skip(8)
    assert csr.peek(1) == b'I' and csr.tell() == 8


def test_cursor_eat():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.eat(b'ABCD') and csr.tell() == 4


def test_cursor_peek():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.peek() == 65 and csr.tell() == 0


def test_cursor_peek_len():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.peek(4) == b'ABCD'


def test_cursor_peek_matches():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert csr.peek_matches(b'ABCD')


def test_cursor_write():
    csr = cursor.Cursor(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    csr.write(b'0123')
    assert csr.dump() == b'0123EFGHIJKLMNOPQRSTUVWXYZ'


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
