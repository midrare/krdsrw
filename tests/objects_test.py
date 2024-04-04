import typing
import pathlib

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
from krdsrw.objects import LPR
from krdsrw.objects import DataStore
from krdsrw.objects import DynamicMap
from krdsrw.objects import IntMap
from krdsrw.objects import Json
from krdsrw.objects import Record
from krdsrw.objects import peek_object_schema
from krdsrw.objects import peek_object_type
from krdsrw.objects import Position
from krdsrw.objects import _TypedDict
from krdsrw.objects import read_object
from krdsrw.objects import write_object

TEMPEST_EPUB: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "the-tempest.epub"
TEMPEST_KFX: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "the-tempest.kfx"
TEMPEST_YJF: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "the-tempest.yjf"
TEMPEST_YJR: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "the-tempest.yjr"


def test_peek_object_schema():
    csr = Cursor(b'\xfe\x00\x00\x0a\x66\x6F\x6E\x74\x2E\x70\x72\x65\x66\x73')
    assert peek_object_schema(csr) == 'font.prefs'
    assert csr.tell() == 0


def test_peek_object_type():
    csr = Cursor(b'\xfe\x00\x00\x0a\x66\x6F\x6E\x74\x2E\x70\x72\x65\x66\x73')
    assert issubclass(peek_object_type(csr), Record)


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
    assert o['start_pos']['chunk_eid'] == 2788
    assert o['start_pos']['chunk_pos'] == 38
    assert o['start_pos']['char_pos'] == 15288
    assert o['end_pos']['chunk_eid'] == 3199
    assert o['end_pos']['chunk_pos'] == 28
    assert o['end_pos']['char_pos'] == 15330
    assert o['creation_time'] == 1700855241409
    assert o['last_modification_time'] == 1700855241409
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


class TestJson:
    def test_instantiate(self):
        o = Json()  # no error
        assert o is not None

        o = Json(True)  # no error
        assert isinstance(o, int) and isinstance(o, Json)
        assert o
        assert o == True

        o = Json(False)  # no error
        assert isinstance(o, int) and isinstance(o, Json)
        assert not o
        assert o == False

        o = Json(0)  # no error
        assert isinstance(o, int) and isinstance(o, Json)

        o = Json(1.0)  # no error
        assert isinstance(o, float) and isinstance(o, Json)

        o = Json('hello')  # no error
        assert isinstance(o, str) and isinstance(o, Json)

        o = Json(b'abc')  # no error
        assert isinstance(o, bytes) and isinstance(o, Json)

        o = Json(('a', 'b', 'c'))  # no error
        assert isinstance(o, tuple) and isinstance(o, Json)

        o = Json([ 'a', 'b', 'c'])  # no error
        assert isinstance(o, list) and isinstance(o, Json)

        o = Json({ 'a': 1, 'b': 2, 'c': 3 })  # no error
        assert isinstance(o, dict) and isinstance(o, Json)

    def test_eq_operator(self):
        o = Json()  # no error
        assert bool(o) is False
        assert not o

        o = Json(True)  # no error
        assert o

        o = Json(False)  # no error
        assert not o

        o = Json(0)  # no error
        assert o == 0

        o = Json(1.0)  # no error
        assert o == 1.0

        o = Json('hello')  # no error
        assert o == 'hello'

        o = Json(b'abc')  # no error
        assert o == b'abc'

        o = Json(('a', 'b', 'c'))  # no error
        assert o == ('a', 'b', 'c')

        o = Json([ 'a', 'b', 'c'])  # no error
        assert o == [ 'a', 'b', 'c']

        o = Json({ 'a': 1, 'b': 2, 'c': 3 })  # no error
        assert o == { 'a': 1, 'b': 2, 'c': 3 }

    def test_read_null(self):
        csr = Cursor(b'\x03\x01')
        o = Json._create(csr)
        assert not o
        assert isinstance(o, Json) and not isinstance(
            o, (bool, int, float, str, bytes, tuple, list, dict))

    def test_read(self):
        csr = Cursor(
            b'\x03\x00\x00\xeF\x5B\x22\x61\x22'\
            + b'\x2C\x20\x22\x62\x22\x2C\x20\x22' \
            + b'\x63\x22\x5D')
        o = Json._create(csr)
        assert isinstance(o, list) and isinstance(o, Json)
        assert o == [ 'a', 'b', 'c']

    def test_write_null(self):
        csr = Cursor()
        o = Json()
        o._write(csr)
        assert csr.dump() in [ b'\x03\x01', b'\x03\x00\x00\x00']

    def test_write(self):
        csr = Cursor()
        o = Json([ 'a', 'b', 'c'])
        o._write(csr)
        assert csr.dump() == (
            b'\x03\x00\x00\x0F\x5B\x22\x61\x22'\
            + b'\x2C\x20\x22\x62\x22\x2C\x20\x22' \
            + b'\x63\x22\x5D')


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
        csr = Cursor(
            b'\x01\x00\x00\x00\x03' + b'\x01\x00\x00\x00\x0a'
            + b'\x01\x00\x00\x00\x0b' + b'\x01\x00\x00\x00\x0c')
        o = spc.read(csr)
        assert o == [ 0x0a, 0x0b, 0x0c ]

    def test_write(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        o.extend([ 0x0a, 0x0b, 0x0c ])
        csr = Cursor()
        o._write(csr)
        assert csr.dump() == b'\x01\x00\x00\x00\x03' \
            + b'\x01\x00\x00\x00\x0a' \
            + b'\x01\x00\x00\x00\x0b' \
            + b'\x01\x00\x00\x00\x0c'

    def test_elmt_cls(self):
        spc = Array.spec(Spec(Int))
        o = spc.make()
        assert o.elmt_cls == Int

    def test_elmt_name(self):
        spc = Array.spec(Spec(Int), 'abc')
        o = spc.make()
        assert o.elmt_name == 'abc'

    def test_make_element(self):
        spc = Array.spec(Spec(Int))
        arr = spc.make()
        o = arr.make_element(1337)
        assert o == 1337

    def test_make_and_append(self):
        spc = Array.spec(Spec(Int))
        arr = spc.make()
        o = arr.make_and_append(1337)
        assert o == 1337
        assert arr == [1337]


class TestTypedDict:
    def test_instantiate(self):
        class Custom(_TypedDict):
            @property
            @typing.override
            def _key_to_field(self) -> dict[str, _TypedDict._TypedField]:
                return {
                    'a': _TypedDict._TypedField(Spec(Bool), None, None, True),
                    'b': _TypedDict._TypedField(Spec(Int), None, None, True),
                    'c':
                    _TypedDict._TypedField(Spec(Utf8Str), None, None, True),
                    'x': _TypedDict._TypedField(Spec(Bool), None, None, False),
                    'y': _TypedDict._TypedField(Spec(Int), None, None, False),
                    'z':
                    _TypedDict._TypedField(Spec(Utf8Str), None, None, False),
                }

        o = Custom()  # no error
        assert o is not None

        o = Custom()  # no error
        assert o == { 'a': False, 'b': 0, 'c': ''}


class TestRecord:
    def test_instantiate(self):
        spc = Record.spec({
            'a': Spec(Int),
            'b': Spec(Float)
        }, {
            'c': Spec(Double),
            'd': Spec(Utf8Str)
        })

        o = spc.make({
            'a': 123,
            'b': 4.56,
            'c': 7.89,
            'd': 'hello',
        })  # no error

        assert o and isinstance(o, Record)

    def test_required_optional(self):
        spc = Record.spec({
            'a': Spec(Int),
            'b': Spec(Float)
        }, {
            'c': Spec(Double),
            'd': Spec(Utf8Str)
        })

        with pytest.raises(KeyError):
            o = spc.make({ 'a': 123, 'b': 4.56, 'c': 7.89, 'd': 'hello'})
            del o['a']  # no error

        with pytest.raises(KeyError):
            o = spc.make({ 'a': 123, 'b': 4.56, 'c': 7.89, 'd': 'hello'})
            del o['b']  # no error

        o = spc.make({ 'a': 123, 'b': 4.56, 'c': 7.89, 'd': 'hello'})
        del o['c']  # no error
        assert 'c' not in o

        o = spc.make({ 'a': 123, 'b': 4.56, 'c': 7.89, 'd': 'hello'})
        del o['d']  # no error
        assert 'd' not in o

    def test_read(self):
        spc = Record.spec({
            'a': Spec(Int),
            'b': Spec(Float)
        }, {
            'c': Spec(Double),
            'd': Spec(Utf8Str)
        })

        csr = Cursor(
            b'\x01\x00\x00\x05\x39\x06\x00\x00' \
            + b'\x00\x00\x04\x00\x00\x00\x00\x00' \
            + b'\x00\x00\x00\x03\x00\x00\x03\x61' \
            + b'\x62\x63')

        o = spc.read(csr)
        assert o == { 'a': 1337, 'b': 0.0, 'c': 0.0, 'd': 'abc'}

    def test_write(self):
        spc = Record.spec({
            'a': Spec(Int),
            'b': Spec(Float)
        }, {
            'c': Spec(Double),
            'd': Spec(Utf8Str)
        })

        o = spc.make({ 'a': 123, 'b': 4.56, 'c': 7.89, 'd': 'xyz'})

        csr = Cursor()
        o._write(csr)

        assert csr.dump() == \
            b'\x01\x00\x00\x00\x7b\x06\x40\x91' \
            + b'\xeb\x85\x04\x40\x1f\x8f\x5c\x28' \
            + b'\xf5\xc2\x8f\x03\x00\x00\x03\x78' \
            + b'\x79\x7a'

    def test_access(self):
        spc = Record.spec({
            'a': Spec(Int),
            'b': Spec(Float)
        }, {
            'c': Spec(Double),
            'd': Spec(Utf8Str)
        })

        o = spc.make({ 'a': 123, 'b': 4.56, 'c': 7.89, 'd': 'hello'})
        assert o['a'] == 123
        assert o['b'] == 4.56
        assert o['c'] == 7.89
        assert o['d'] == 'hello'


class TestIntMap:
    def test_instantiate(self):
        spc = IntMap.spec([
            ("apple", "name.a", Array.spec(Spec(Int), "x")),
            ("banana", "name.b", Array.spec(Spec(Int), "y")),
            ("pear", "name.c", Array.spec(Spec(Int), "z")),
        ])
        spc.make()

    def test_make_element(self):
        spc = IntMap.spec([
            ("apple", "name.a", Array.spec(Spec(Int), "x")),
            ("banana", "name.b", Array.spec(Spec(Int), "y")),
            ("pear", "name.c", Array.spec(Spec(Int), "z")),
        ])

        o = spc.make()
        o['apple'].make_and_append(111)
        o['banana'].make_and_append(222)
        o['pear'].make_and_append(333)


class TestDynamicMap:
    def test_put_key(self):
        o = DynamicMap()
        o['a'] = Int(0x0a)
        with pytest.raises(ValueError):
            o['a'] = 0x0a  # type: ignore


class TestPosition:
    def test_instantiate(self):
        o = Position()  # no error
        assert o is not None

        o = Position({ 'char_pos': 12345 })  # no error
        assert o is not None

    def test_read_v1(self):
        csr = Cursor(b'\x03\x00\x00\x05\x31\x32\x33\x34\x35')
        o = Position._create(csr)  # no error
        assert o == { 'char_pos': 12345 }

    def test_read_chunk_v1(self):
        csr = Cursor(
            b'\x03\x00\x00\x11\x41\x64\x49\x45' \
            + b'\x41\x41\x41\x75\x46\x67\x41\x41' \
            + b'\x3A\x35\x30\x35\x30')
        o = Position._create(csr)  # no error
        assert o == {
            'char_pos': 5050,
            'chunk_eid': 1234,
            'chunk_pos': 5678,
        }

    def test_write_v1(self):
        csr = Cursor()
        o = Position({ 'char_pos': 12345 })
        o._write(csr)
        assert csr.dump() == b'\x03\x00\x00\x05\x31\x32\x33\x34\x35'

    def test_write_chunk_v1(self):
        csr = Cursor()
        o = Position({
            'char_pos': 5050,
            'chunk_eid': 1234,
            'chunk_pos': 5678,
        })
        o._write(csr)
        assert csr.dump() == \
            (b'\x03\x00\x00\x11\x41\x64\x49\x45' \
            + b'\x41\x41\x41\x75\x46\x67\x41\x41' \
            + b'\x3A\x35\x30\x35\x30')


class TestLPR:
    def test_instantiate(self):
        o = LPR()  # no error
        assert o is not None

    def test_read_v1(self):
        csr = Cursor(b'\x03\x00\x00\x05\x31\x32\x33\x34\x35')
        o = LPR._create(csr)  # no error
        assert o == { 'pos': { 'char_pos': 12345 } }


class TestDataStore:
    def test_init(self):
        root = DataStore()

    def test_read(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = DataStore._create(csr)

    def test_read_write(self):
        orig_data = TEMPEST_YJR.read_bytes()

        csr = Cursor(orig_data)
        root = DataStore._create(csr)

        csr = Cursor()
        root._write(csr)

        assert csr.dump() == orig_data

    def test_annotation_cache_object_len(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = DataStore._create(csr)
        assert len(root["annotation.cache.object"]) == 3

    def test_bookmark(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = DataStore._create(csr)

        o = root["annotation.cache.object"]["bookmarks"][0]
        assert o["start_pos"]['chunk_eid'] == 5525
        assert o["start_pos"]['chunk_pos'] == 0
        assert o["start_pos"]['char_pos'] == 76032
        assert o["end_pos"]['chunk_eid'] == 5525
        assert o["end_pos"]['chunk_pos'] == 0
        assert o["end_pos"]['char_pos'] == 76032
        assert o["creation_time"] == 1701332599082
        assert o["last_modification_time"] == 1701332599082
