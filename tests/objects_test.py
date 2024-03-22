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
from krdsrw.objects import Object
from krdsrw.objects import Record
from krdsrw.objects import peek_object_schema
from krdsrw.objects import peek_object_type
from krdsrw.objects import read_object
from krdsrw.objects import write_object


def test_peek_object_schema():
    csr = Cursor(b'\xfe\x00\x00\x0a\x66\x6F\x6E\x74\x2E\x70\x72\x65\x66\x73')
    assert peek_object_schema(csr) == 'font.prefs'
    assert csr.tell() == 0


def test_peek_object_type():
    csr = Cursor(b'\xfe\x00\x00\x0a\x66\x6F\x6E\x74\x2E\x70\x72\x65\x66\x73')
    assert peek_object_type(csr) == Record


def test_read_object():
    csr = Cursor(
        b'\xFE\x00\x00\x1D\x61\x6E\x6E\x6F\x74\x61\x74\x69\x6F\x6E\x2E\x70'
        + b'\x65\x72\x73\x6F\x6E\x61\x6C\x2E\x68\x69\x67\x68\x6C\x69\x67\x68'
        + b'\x74\x03\x00\x00\x12\x41\x65\x51\x4B\x41\x41\x41\x6D\x41\x41\x41'
        + b'\x41\x3A\x31\x35\x32\x38\x38\x03\x00\x00\x12\x41\x58\x38\x4D\x41'
        + b'\x41\x41\x63\x41\x41\x41\x41\x3A\x31\x35\x33\x33\x30\x02\x00\x00'
        + b'\x01\x8C\x02\xDF\x5A\xC1\x02\x00\x00\x01\x8C\x02\xDF\x5A\xC1\x03'
        + b'\x00\x00\x05\x30\xEF\xBF\xBC\x30\xFF')
    o, n = read_object(csr, 'annotation.personal.highlight')
    assert n == 'annotation.personal.highlight'
    assert o['start_pos'].chunk_eid == 2788
    assert o['start_pos'].chunk_pos == 38
    assert o['start_pos'].char_pos == 15288
    assert o['end_pos'].chunk_eid == 3199
    assert o['end_pos'].chunk_pos == 28
    assert o['end_pos'].char_pos == 15330
    assert o['creation_time'].epoch_ms == 1700855241409
    assert o['last_modification_time'].epoch_ms == 1700855241409
    assert o['template'] == "0￼0"


def test_write_object():
    csr = Cursor()

    spc = Record.spec({
        "typeface": Spec(Utf8Str),
        "line_sp": Spec(Int),
        "size": Spec(Int),
        "align": Spec(Int),
        "inset_top": Spec(Int),
        "inset_left": Spec(Int),
        "inset_bottom": Spec(Int),
        "inset_right": Spec(Int),
        "unknown1": Spec(Int),
    }, {
        "bold": Spec(Int),
        "user_sideloadable_font": Spec(Utf8Str),
        "custom_font_index": Spec(Int),
        "mobi7_system_font": Spec(Utf8Str),
        "mobi7_restore_font": Spec(Bool),
        "reading_preset_selected": Spec(Utf8Str),
    })

    o = spc.make({
        "typeface": '_INVALID_,und:helvetica neue lt',
        "line_sp": 1,
        "size": 0,
        "align": 1,
        "inset_top": 63,
        "inset_left": 80,
        "inset_bottom": 0,
        "inset_right": 80,
        "unknown1": 0,
        "bold": 1,
        "user_sideloadable_font": '',
        "custom_font_index": -1,
        "mobi7_system_font": '',
        "mobi7_restore_font": False,
        "reading_preset_selected": '',
    })

    write_object(csr, o, "font.prefs")
    assert csr.dump() == \
        b'\xFE\x00\x00\x0A\x66\x6F\x6E\x74\x2E\x70\x72\x65\x66\x73\x03\x00' \
        + b'\x00\x1F\x5F\x49\x4E\x56\x41\x4C\x49\x44\x5F\x2C\x75\x6E\x64\x3A' \
        + b'\x68\x65\x6C\x76\x65\x74\x69\x63\x61\x20\x6E\x65\x75\x65\x20\x6C' \
        + b'\x74\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01' \
        + b'\x01\x00\x00\x00\x3F\x01\x00\x00\x00\x50\x01\x00\x00\x00\x00\x01' \
        + b'\x00\x00\x00\x50\x01\x00\x00\x00\x00\x01\x00\x00\x00\x01\x03\x01' \
        + b'\x01\xFF\xFF\xFF\xFF\x03\x01\x00\x00\x03\x01\xFF'


class TestObject:
    def test_create(self):
        with pytest.raises(TypeError):
            Object()  # type: ignore


class TestArray:
    def test_init(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        assert o.elmt_cls == Int

    def test_append_type_check_allow(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        o.append(1337)
        assert o[0] == 1337

    def test_append_type_check_disallow(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        with pytest.raises(ValueError):
            o.append("foo")

    def test_insert_type_check_allow(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        o.insert(0, 1337)
        assert o[0] == 1337

    def test_insert_type_check_disallow(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        with pytest.raises(ValueError):
            o.insert(0, "foo")

    def test_extend_type_check_allow(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        o.extend([ 0, 1, 2, 3, 4 ])
        assert o == [ 0, 1, 2, 3, 4 ]

    def test_extend_type_check_disallow(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        with pytest.raises(ValueError):
            o.extend([ "a", "b", "c", "d", "e"])

    def test_copy_contents(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        o.extend([ 0, 1, 2, 3, 4 ])
        o2 = o.copy()
        assert isinstance(o2, Array) and o2 == o

    def test_count(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        o.extend([ 0, 1, 2, 3, 4 ])
        assert o.count(2) == 1

    def test_read(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        csr = Cursor(
            b'\x01\x00\x00\x00\x03' + b'\x01\x00\x00\x00\x0a'
            + b'\x01\x00\x00\x00\x0b' + b'\x01\x00\x00\x00\x0c')
        o.read(csr)
        assert o == [ 0x0a, 0x0b, 0x0c ]

    def test_write(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
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
