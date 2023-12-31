import typing
import pathlib

from krdsrw.containers import DataStore
from krdsrw.cursor import Cursor

TEMPEST_EPUB: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "The Tempest.epub"
TEMPEST_KFX: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "The Tempest.kfx"
TEMPEST_YJF: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "The Tempest.yjf"
TEMPEST_YJR: typing.Final[
    pathlib.Path] = pathlib.Path(__file__).parent / "The Tempest.yjr"


class TestDataStore:
    def test_init(self):
        root = DataStore()

    def test_read(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = DataStore()
        root.read(csr)

    def test_read_write(self):
        orig_data = TEMPEST_YJR.read_bytes()

        csr = Cursor(orig_data)
        root = DataStore()
        root.read(csr)

        csr = Cursor()
        root.write(csr)

        assert csr.dump() == orig_data

    def test_annotation_cache_object_len(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = DataStore()
        root.read(csr)
        assert len(root["annotation.cache.object"]) == 3

    def test_bookmark(self):
        csr = Cursor(TEMPEST_YJR.read_bytes())
        root = DataStore()
        root.read(csr)

        o = root["annotation.cache.object"]["bookmarks"][0]
        assert o["start_pos"].chunk_eid == 5525
        assert o["start_pos"].chunk_pos == 0
        assert o["start_pos"].char_pos == 76032
        assert o["end_pos"].chunk_eid == 5525
        assert o["end_pos"].chunk_pos == 0
        assert o["end_pos"].char_pos == 76032
        assert o["creation_time"].epoch_ms == 1701332599082
        assert o["last_modification_time"].epoch_ms == 1701332599082
