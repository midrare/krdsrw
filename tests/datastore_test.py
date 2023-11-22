import typing
import pathlib

from krdsrw.datastore.containers import DataStore
from krdsrw.datastore.cursor import Cursor

NLH_FILE: typing.Final[pathlib.Path] = pathlib.Path(
    __file__).parent / "No Longer Human (Dazai & Keene).yjr"


class TestDataStore:
    def test_init(self):
        csr = Cursor()
        csr.load(NLH_FILE.read_bytes())

        root = DataStore()
        root.read(csr)
