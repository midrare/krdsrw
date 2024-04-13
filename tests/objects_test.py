import pathlib
import typing

import pytest

from krdsrw.basics import Bool
from krdsrw.basics import Double
from krdsrw.basics import Float
from krdsrw.basics import Int
from krdsrw.basics import Utf8Str
from krdsrw.cursor import Cursor
from krdsrw.objects import Array
from krdsrw.objects import DynamicMap
from krdsrw.objects import Field
from krdsrw.objects import IntMap
from krdsrw.objects import Json
from krdsrw.objects import LPR
from krdsrw.objects import Position
from krdsrw.objects import Protoform
from krdsrw.objects import Record
from krdsrw.objects import Store
from krdsrw.objects import _TypedDict
from krdsrw.objects import _make_object
from krdsrw.objects import _read_object

TEMPEST_EPUB: typing.Final[pathlib.Path] = (
    pathlib.Path(__file__).parent / "the-tempest.epub"
)
TEMPEST_KFX: typing.Final[pathlib.Path] = (
    pathlib.Path(__file__).parent / "the-tempest.kfx"
)
TEMPEST_YJF: typing.Final[pathlib.Path] = (
    pathlib.Path(__file__).parent / "the-tempest.yjf"
)
TEMPEST_YJR: typing.Final[pathlib.Path] = (
    pathlib.Path(__file__).parent / "the-tempest.yjr"
)


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

        o = Json("hello")  # no error
        assert isinstance(o, str) and isinstance(o, Json)

        o = Json(b"abc")  # no error
        assert isinstance(o, bytes) and isinstance(o, Json)

        o = Json(("a", "b", "c"))  # no error
        assert isinstance(o, tuple) and isinstance(o, Json)

        o = Json(["a", "b", "c"])  # no error
        assert isinstance(o, list) and isinstance(o, Json)

        o = Json({"a": 1, "b": 2, "c": 3})  # no error
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

        o = Json("hello")  # no error
        assert o == "hello"

        o = Json(b"abc")  # no error
        assert o == b"abc"

        o = Json(("a", "b", "c"))  # no error
        assert o == ("a", "b", "c")

        o = Json(["a", "b", "c"])  # no error
        assert o == ["a", "b", "c"]

        o = Json({"a": 1, "b": 2, "c": 3})  # no error
        assert o == {"a": 1, "b": 2, "c": 3}

    def test_read_null(self):
        csr = Cursor(b"\x03\x01")
        o = Json._create(csr)
        assert not o
        assert isinstance(o, Json) and not isinstance(
            o, (bool, int, float, str, bytes, tuple, list, dict)
        )

    def test_read(self):
        csr = Cursor(
            b"\x03\x00\x00\xeF\x5B\x22\x61\x22"
            + b"\x2C\x20\x22\x62\x22\x2C\x20\x22"
            + b"\x63\x22\x5D"
        )
        o = Json._create(csr)
        assert isinstance(o, list) and isinstance(o, Json)
        assert o == ["a", "b", "c"]

    def test_write_null(self):
        csr = Cursor()
        o = Json()
        o._write(csr)
        assert csr.dump() in [b"\x03\x01", b"\x03\x00\x00\x00"]

    def test_write(self):
        csr = Cursor()
        o = Json(["a", "b", "c"])
        o._write(csr)
        assert csr.dump() == (
            b"\x03\x00\x00\x0F\x5B\x22\x61\x22"
            + b"\x2C\x20\x22\x62\x22\x2C\x20\x22"
            + b"\x63\x22\x5D"
        )


class TestArray:
    def test_instantiate(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)  # no error
        assert o is not None

    def test_append_type_check_allow(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        o.append(1337)
        assert o[0] == 1337

    def test_append_type_check_disallow(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        with pytest.raises(ValueError):
            o.append("foo")

    def test_insert_type_check_allow(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        o.insert(0, 1337)
        assert o[0] == 1337

    def test_insert_type_check_disallow(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        with pytest.raises(ValueError):
            o.insert(0, "foo")

    def test_extend_type_check_allow(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        o.extend([0, 1, 2, 3, 4])
        assert o == [0, 1, 2, 3, 4]

    def test_extend_type_check_disallow(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        with pytest.raises(ValueError):
            o.extend(["a", "b", "c", "d", "e"])

    def test_copy_contents(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        o.extend([0, 1, 2, 3, 4])
        o2 = o.copy()
        assert isinstance(o2, Array) and o2 == o

    def test_count(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        o.extend([0, 1, 2, 3, 4])
        assert o.count(2) == 1

    def test_read(self):
        csr = Cursor(
            b"\x01\x00\x00\x00\x03"
            + b"\x01\x00\x00\x00\x0a"
            + b"\x01\x00\x00\x00\x0b"
            + b"\x01\x00\x00\x00\x0c"
        )
        sch = Array._schema(Protoform(Int))
        o = Array._create(csr, _schema=sch)
        assert o == [0x0A, 0x0B, 0x0C]

    def test_write(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        o.extend([0x0A, 0x0B, 0x0C])
        csr = Cursor()
        o._write(csr)
        assert (
            csr.dump()
            == b"\x01\x00\x00\x00\x03"
            + b"\x01\x00\x00\x00\x0a"
            + b"\x01\x00\x00\x00\x0b"
            + b"\x01\x00\x00\x00\x0c"
        )

    def test_elmt_cls(self):
        sch = Array._schema(Protoform(Int))
        o = Array(_schema=sch)
        assert o.elmt_schema_cls == Int

    def test_elmt_schema(self):
        sch = Array._schema(Protoform(Int), schema_id="abc")
        o = Array(_schema=sch)
        assert o.elmt_schema_id == "abc"

    def test_make_element(self):
        sch = Array._schema(Protoform(Int))
        arr = Array(_schema=sch)
        o = arr.make_element(1337)
        assert o == 1337

    def test_make_and_append(self):
        sch = Array._schema(Protoform(Int))
        arr = Array(_schema=sch)
        o = arr.make_and_append(1337)
        assert o == 1337
        assert arr == [1337]


class TestTypedDict:
    def test_instantiate(self):
        class Custom(_TypedDict):
            def __init__(self, *args, **kwargs):
                schema = {
                    "a": Field(Protoform(Bool)),
                    "b": Field(Protoform(Int)),
                    "c": Field(Protoform(Utf8Str)),
                    "x": Field(Protoform(Bool), required=False),
                    "y": Field(Protoform(Int), required=False),
                    "z": Field(Protoform(Utf8Str), required=False),
                }
                super().__init__(*args, _schema=schema, **kwargs)

        o = Custom()  # no error
        assert o is not None

        o = Custom()  # no error
        assert o == {"a": False, "b": 0, "c": ""}

    def test_delete_required(self):
        class Custom(_TypedDict):
            def __init__(self, *args, **kwargs):
                schema = {
                    "a": Field(Protoform(Bool)),
                    "b": Field(Protoform(Int)),
                    "c": Field(Protoform(Utf8Str)),
                    "x": Field(Protoform(Bool), required=False),
                    "y": Field(Protoform(Int), required=False),
                    "z": Field(Protoform(Utf8Str), required=False),
                }
                super().__init__(*args, _schema=schema, **kwargs)

        o = Custom()
        with pytest.raises(KeyError):
            del o["a"]

        o = Custom()
        with pytest.raises(KeyError):
            del o["b"]

        o = Custom()
        with pytest.raises(KeyError):
            del o["c"]

        o = Custom({"x": True, "y": 8, "z": "hello"})
        del o["x"]  # no error
        assert "x" not in o

        o = Custom({"x": True, "y": 8, "z": "hello"})
        del o["y"]  # no error
        assert "y" not in o

        o = Custom({"x": True, "y": 8, "z": "hello"})
        del o["z"]  # no error
        assert "z" not in o


class TestRecord:
    def test_instantiate(self):
        sch = Record._schema(
            {
                "a": Int,
                "b": Float,
                "c": Field(Protoform(Double), required=False),
                "d": Field(Protoform(Utf8Str), required=False),
            }
        )

        o = _make_object(
            Record,
            {
                "a": 123,
                "b": 4.56,
                "c": 7.89,
                "d": "hello",
            },
            schema=sch,
        )  # no error
        assert o and isinstance(o, Record)

    def test_required_optional(self):
        sch = Record._schema(
            {
                "a": Int,
                "b": Float,
                "c": Field(Protoform(Double), required=False),
                "d": Field(Protoform(Utf8Str), required=False),
            }
        )

        with pytest.raises(KeyError):
            o = _make_object(
                Record,
                {"a": 123, "b": 4.56, "c": 7.89, "d": "hello"},
                schema=sch,
            )
            del o["a"]  # no error

        with pytest.raises(KeyError):
            o = _make_object(
                Record,
                {"a": 123, "b": 4.56, "c": 7.89, "d": "hello"},
                schema=sch,
            )
            del o["b"]  # no error

        o = _make_object(
            Record, {"a": 123, "b": 4.56, "c": 7.89, "d": "hello"}, schema=sch
        )
        del o["c"]  # no error
        assert "c" not in o

        o = _make_object(
            Record, {"a": 123, "b": 4.56, "c": 7.89, "d": "hello"}, schema=sch
        )
        del o["d"]  # no error
        assert "d" not in o

    def test_read(self):
        sch = Record._schema(
            {
                "a": Int,
                "b": Float,
                "c": Field(Protoform(Double), required=False),
                "d": Field(Protoform(Utf8Str), required=False),
            }
        )

        csr = Cursor(
            b"\x01\x00\x00\x05\x39\x06\x00\x00"
            + b"\x00\x00\x04\x00\x00\x00\x00\x00"
            + b"\x00\x00\x00\x03\x00\x00\x03\x61"
            + b"\x62\x63"
        )

        o = _read_object(csr, Record, sch)
        assert o == {"a": 1337, "b": 0.0, "c": 0.0, "d": "abc"}

    def test_write(self):
        sch = Record._schema(
            {
                "a": Int,
                "b": Float,
                "c": Field(Protoform(Double), required=False),
                "d": Field(Protoform(Utf8Str), required=False),
            }
        )

        o = _make_object(
            Record, {"a": 123, "b": 4.56, "c": 7.89, "d": "xyz"}, schema=sch
        )

        csr = Cursor()
        o._write(csr)

        assert (
            csr.dump()
            == b"\x01\x00\x00\x00\x7b\x06\x40\x91"
            + b"\xeb\x85\x04\x40\x1f\x8f\x5c\x28"
            + b"\xf5\xc2\x8f\x03\x00\x00\x03\x78"
            + b"\x79\x7a"
        )

    def test_access(self):
        sch = Record._schema(
            {
                "a": Int,
                "b": Float,
                "c": Field(Protoform(Double), required=False),
                "d": Field(Protoform(Utf8Str), required=False),
            }
        )

        o = _make_object(
            Record,
            {"a": 123, "b": 4.56, "c": 7.89, "d": "hello"},
            schema=sch,
        )
        assert o["a"] == 123
        assert o["b"] == 4.56
        assert o["c"] == 7.89
        assert o["d"] == "hello"


class TestIntMap:
    def test_instantiate(self):
        sch = IntMap._schema(
            {
                "apple": Field(
                    Protoform(
                        Array, Array._schema(Protoform(Int), schema_id="x")
                    ),
                    "name.a",
                ),
                "banana": Field(
                    Protoform(
                        Array, Array._schema(Protoform(Int), schema_id="y")
                    ),
                    "name.b",
                ),
                "pear": Field(
                    Protoform(
                        Array, Array._schema(Protoform(Int), schema_id="z")
                    ),
                    "name.c",
                ),
            }
        )
        o = _make_object(IntMap, schema=sch)  # no error
        assert o is not None

    def test_make_element(self):
        sch = IntMap._schema(
            {
                "apple": Field(
                    Protoform(
                        Array, Array._schema(Protoform(Int), schema_id="x")
                    ),
                    "name.a",
                ),
                "banana": Field(
                    Protoform(
                        Array, Array._schema(Protoform(Int), schema_id="y")
                    ),
                    "name.b",
                ),
                "pear": Field(
                    Protoform(
                        Array, Array._schema(Protoform(Int), schema_id="z")
                    ),
                    "name.c",
                ),
            }
        )

        o = _make_object(IntMap, schema=sch)
        o["apple"].make_and_append(111)  # no error
        o["banana"].make_and_append(222)  # no error
        o["pear"].make_and_append(333)  # no error


class TestDynamicMap:
    def test_put_key(self):
        o = DynamicMap()
        o["a"] = Int(0x0A)
        with pytest.raises(ValueError):
            o["a"] = 0x0A  # type: ignore


class TestPosition:
    def test_instantiate(self):
        o = Position()  # no error
        assert o is not None

        o = Position({"char_pos": 12345})  # no error
        assert o is not None

    def test_read_v1(self):
        csr = Cursor(b"\x03\x00\x00\x05\x31\x32\x33\x34\x35")
        o = Position._create(csr)  # no error
        assert o == {"char_pos": 12345}

    def test_read_chunk_v1(self):
        csr = Cursor(
            b"\x03\x00\x00\x11\x41\x64\x49\x45"
            + b"\x41\x41\x41\x75\x46\x67\x41\x41"
            + b"\x3A\x35\x30\x35\x30"
        )
        o = Position._create(csr)  # no error
        assert o == {
            "char_pos": 5050,
            "chunk_eid": 1234,
            "chunk_pos": 5678,
        }

    def test_write_v1(self):
        csr = Cursor()
        o = Position({"char_pos": 12345})
        o._write(csr)
        assert csr.dump() == b"\x03\x00\x00\x05\x31\x32\x33\x34\x35"

    def test_write_chunk_v1(self):
        csr = Cursor()
        o = Position(
            {
                "char_pos": 5050,
                "chunk_eid": 1234,
                "chunk_pos": 5678,
            }
        )
        o._write(csr)
        assert csr.dump() == (
            b"\x03\x00\x00\x11\x41\x64\x49\x45"
            + b"\x41\x41\x41\x75\x46\x67\x41\x41"
            + b"\x3A\x35\x30\x35\x30"
        )


class TestLPR:
    def test_instantiate(self):
        o = LPR()  # no error
        assert o is not None

    def test_read_v1(self):
        csr = Cursor(b"\x03\x00\x00\x05\x31\x32\x33\x34\x35")
        o = LPR._create(csr)  # no error
        assert o == {"pos": {"char_pos": 12345}}


class TestStore:
    def test_instantiate(self):
        o = _make_object(Store)  # no error
        assert o is not None

    def test_read(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = Store._create(csr)  # no error
        assert root is not None

    def test_read_write(self):
        orig_data = TEMPEST_YJR.read_bytes()

        csr = Cursor(orig_data)
        root = Store._create(csr)

        csr = Cursor()
        root._write(csr)

        assert csr.dump() == orig_data

    def test_annotation_cache_object_len(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = Store._create(csr)
        assert len(root["annotation.cache.object"]) == 3

    def test_bookmark(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = Store._create(csr)

        o = root["annotation.cache.object"]["bookmarks"][0]
        assert o["start_pos"]["chunk_eid"] == 5525
        assert o["start_pos"]["chunk_pos"] == 0
        assert o["start_pos"]["char_pos"] == 76032
        assert o["end_pos"]["chunk_eid"] == 5525
        assert o["end_pos"]["chunk_pos"] == 0
        assert o["end_pos"]["char_pos"] == 76032
        assert o["creation_time"] == 1701332599082
        assert o["last_modification_time"] == 1701332599082

    def test_read_object(self):
        csr = Cursor(
            b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
            + b"\x02\x00\x00\x00\x00\x00\x00\x00"
            + b"\x01\x01\x00\x00\x00\x01\xFE\x00"
            + b"\x00\x1D\x61\x6E\x6E\x6F\x74\x61"
            + b"\x74\x69\x6F\x6E\x2E\x70\x65\x72"
            + b"\x73\x6F\x6E\x61\x6C\x2E\x68\x69"
            + b"\x67\x68\x6C\x69\x67\x68\x74\x03"
            + b"\x00\x00\x12\x41\x65\x51\x4B\x41"
            + b"\x41\x41\x6D\x41\x41\x41\x41\x3A"
            + b"\x31\x35\x32\x38\x38\x03\x00\x00"
            + b"\x12\x41\x58\x38\x4D\x41\x41\x41"
            + b"\x63\x41\x41\x41\x41\x3A\x31\x35"
            + b"\x33\x33\x30\x02\x00\x00\x01\x8C"
            + b"\x02\xDF\x5A\xC1\x02\x00\x00\x01"
            + b"\x8C\x02\xDF\x5A\xC1\x03\x00\x00"
            + b"\x05\x30\xEF\xBF\xBC\x30\xFF"
        )
        store = Store._create(csr)
        n = store["annotation.personal.highlight"]
        assert n["start_pos"]["chunk_eid"] == 2788
        assert n["start_pos"]["chunk_pos"] == 38
        assert n["start_pos"]["char_pos"] == 15288
        assert n["end_pos"]["chunk_eid"] == 3199
        assert n["end_pos"]["chunk_pos"] == 28
        assert n["end_pos"]["char_pos"] == 15330
        assert n["creation_time"] == 1700855241409
        assert n["last_modification_time"] == 1700855241409
        assert n["template"] == "0￼0"

    def test_write_object(self):
        o = _make_object(
            Store,
            {
                "font.prefs": {
                    "typeface": "_INVALID_,und:helvetica neue lt",
                    "line_sp": 1,
                    "size": 0,
                    "align": 1,
                    "inset_top": 63,
                    "inset_left": 80,
                    "inset_bottom": 0,
                    "inset_right": 80,
                    "unknown1": 0,
                    "bold": 1,
                    "user_sideloadable_font": "",
                    "custom_font_index": -1,
                    "mobi7_system_font": "",
                    "mobi7_restore_font": False,
                    "reading_preset_selected": "",
                }
            },
        )

        csr = Cursor()
        o._write(csr)

        assert csr.dump() == (
            b"\x00\x00\x00\x00\x00\x1A\xB1\x26"
            + b"\x02\x00\x00\x00\x00\x00\x00\x00"
            + b"\x01\x01\x00\x00\x00\x01\xFE\x00"
            + b"\x00\x0A\x66\x6F\x6E\x74\x2E\x70"
            + b"\x72\x65\x66\x73\x03\x00\x00\x1F"
            + b"\x5F\x49\x4E\x56\x41\x4C\x49\x44"
            + b"\x5F\x2C\x75\x6E\x64\x3A\x68\x65"
            + b"\x6C\x76\x65\x74\x69\x63\x61\x20"
            + b"\x6E\x65\x75\x65\x20\x6C\x74\x01"
            + b"\x00\x00\x00\x01\x01\x00\x00\x00"
            + b"\x00\x01\x00\x00\x00\x01\x01\x00"
            + b"\x00\x00\x3F\x01\x00\x00\x00\x50"
            + b"\x01\x00\x00\x00\x00\x01\x00\x00"
            + b"\x00\x50\x01\x00\x00\x00\x00\x01"
            + b"\x00\x00\x00\x01\x03\x01\x01\xFF"
            + b"\xFF\xFF\xFF\x03\x01\x00\x00\x03"
            + b"\x01\xFF"
        )
