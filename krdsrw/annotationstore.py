import abc
import typing

from .datastore import Position as KdsPosition
from .datastore import Cursor
from .datastore import DataStore
from .datastore import keys
from .datastore import NamedValue
from .datastore import names
from .datastore import SwitchMap
from .datastore import Value

# noinspection SpellCheckingInspection
_TEMPLATE: typing.Final[str] = "0\ufffc0"


class Position:
    def __init__(self, _value: None | KdsPosition = None):
        self._value: KdsPosition = _value or KdsPosition()

    @property
    def chunk_eid(self) -> None | int:
        return self._value.chunk_eid

    @chunk_eid.setter
    def chunk_eid(self, value: None | int):
        self._value.chunk_eid = value

    @property
    def chunk_offset(self) -> None | int:
        return self._value.chunk_pos

    @chunk_offset.setter
    def chunk_offset(self, value: None | int):
        self._value.chunk_pos = value

    @property
    def char_pos(self) -> int:
        return self._value.value if self._value.value is not None else -1

    @char_pos.setter
    def char_pos(self, value: int):
        self._value.value = value

    def __str__(self) -> str:
        s = ""
        if self._value.chunk_eid is not None \
        and self._value.chunk_eid >= 0 \
        and self._value.chunk_pos is not None \
        and self._value.chunk_pos >= 0:
            s = f" eid:{self._value.chunk_eid}+{self._value.chunk_pos}"
        return f"{self.__class__.__name__}{{@{self._value.value}%s}}" % s

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}" + str(
            {
            "pos": self._value.value,
            "chunk_eid": self._value.chunk_eid,
            "chunk_pos": self._value.chunk_pos,
            }
        )


class Annotation(abc.ABC):
    def __init__(self, _name: str, _value: None | NamedValue = None):
        if _value is None:
            _value = NamedValue(_name)
            _value.value.value.compute_if_absent(
                keys.ANNOTATION_TEMPLATE
            ).value = _TEMPLATE
        assert _value.name == _name, "wrong value class"
        # NamedValue{annotation.personal.*} -> FixedMap -> TemplatizedDict
        self._value: NamedValue = _value
        self._start_pos: Position = Position(
            _value.value.value.compute_if_absent(keys.ANNOTATION_START_POS)
        )
        self._end_pos: Position = Position(
            _value.value.value.compute_if_absent(keys.ANNOTATION_END_POS)
        )

    @property
    def start_pos(self) -> None | Position:
        return self._start_pos

    @start_pos.setter
    def start_pos(self, value: Position):
        self._start_pos = value
        self._value.value.value.compute_if_absent(
            keys.ANNOTATION_START_POS
        ).value = value._value

    @property
    def end_pos(self) -> None | Position:
        return self._end_pos

    @end_pos.setter
    def end_pos(self, value: Position):
        self._end_pos = value
        self._value.value.value.compute_if_absent(
            keys.ANNOTATION_END_POS
        ).value = value._value

    @property
    def created_epoch_milli(self) -> None | int:
        v = self._value.value.value.get(keys.ANNOTATION_CREATION_TIME)
        return v.value if v is not None else None

    @created_epoch_milli.setter
    def created_epoch_milli(self, value: int):
        self._value.value.value.compute_if_absent(
            keys.ANNOTATION_CREATION_TIME
        ).value = value

    @property
    def last_modified_epoch_milli(self) -> None | int:
        v = self._value.value.value.get(keys.ANNOTATION_LAST_MODIFICATION_TIME)
        return v.value if v is not None else None

    @last_modified_epoch_milli.setter
    def last_modified_epoch_milli(self, value: int):
        self._value.value.value.compute_if_absent(
            keys.ANNOTATION_LAST_MODIFICATION_TIME
        ).value = value

    @property
    def template(self) -> None | str:
        v = self._value.value.value.get(keys.ANNOTATION_TEMPLATE)
        return v.value if v is not None else None

    @template.setter
    def template(self, value: None | str):
        self._value.value.value.compute_if_absent(
            keys.ANNOTATION_TEMPLATE
        ).value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}%s" % str({
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "created": self.created_epoch_milli,
            "last_modified": self.last_modified_epoch_milli,
            "template": self.template,
        })


class Bookmark(Annotation):
    def __init__(self, _value: None | NamedValue = None):
        super().__init__(names.ANNOTATION_PERSONAL_BOOKMARK, _value)


class Note(Annotation):
    def __init__(self, _value: None | NamedValue = None):
        super().__init__(names.ANNOTATION_PERSONAL_NOTE, _value)

    @property
    def note(self) -> None | str:
        v = self._value.value.value.get(keys.ANNOTATION_NOTE)
        return v.value if v is not None else None

    @note.setter
    def note(self, value: None | str):
        self._value.value.value.compute_if_absent(
            keys.ANNOTATION_NOTE
        ).value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}%s" % str({
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "created": self.created_epoch_milli,
            "last_modified": self.last_modified_epoch_milli,
            "template": self.template,
            "note": self.note,
        })


class ClipArticle(Annotation):
    def __init__(self, _value: None | NamedValue = None):
        super().__init__(names.ANNOTATION_PERSONAL_CLIP_ARTICLE, _value)


class Highlight(Annotation):
    def __init__(self, _value: None | NamedValue = None):
        super().__init__(names.ANNOTATION_PERSONAL_HIGHLIGHT, _value)


class AnnotationCache:
    def __init__(self, _value: None | NamedValue[SwitchMap] = None):
        if _value is None:
            _value = NamedValue(names.ANNOTATION_CACHE_OBJECT)
        assert _value.name == names.ANNOTATION_CACHE_OBJECT, "wrong value class"

        self._value: NamedValue[SwitchMap] = _value
        self._bookmarks: None | typing.List[Bookmark] = None
        self._notes: None | WrappedList = None
        self._highlights: None | WrappedList = None
        self._clip_articles: None | WrappedList = None

    @staticmethod
    def _from_obj(obj: Bookmark | Highlight | Note | ClipArticle) -> NamedValue:
        return obj._value

    @staticmethod
    def _to_obj(value: NamedValue) -> Bookmark | Highlight | Note | ClipArticle:
        if value.name == names.ANNOTATION_PERSONAL_BOOKMARK:
            return Bookmark(value)
        elif value.name == names.ANNOTATION_PERSONAL_HIGHLIGHT:
            return Highlight(value)
        elif value.name == names.ANNOTATION_PERSONAL_NOTE:
            return Note(value)
        elif value.name == names.ANNOTATION_PERSONAL_CLIP_ARTICLE:
            return ClipArticle(value)

    @property
    def bookmarks(self) -> typing.List[Bookmark]:
        if self._bookmarks is None:
            backing = self._get_or_compute(keys.ANNOTATION_BOOKMARKS, True)
            # asserts to placate IntelliJ intellisense
            assert isinstance(backing, NamedValue)
            assert backing.name == "saved.avl.interval.tree"
            self._bookmarks = WrappedList(
                Bookmark, backing.value, self._from_obj, self._to_obj
            )
        return self._bookmarks

    @property
    def notes(self) -> typing.List[Note]:
        if self._notes is None:
            backing = self._get_or_compute(keys.ANNOTATION_NOTES, True)
            # asserts to placate IntelliJ intellisense
            assert isinstance(backing, NamedValue)
            assert backing.name == "saved.avl.interval.tree"
            self._notes = WrappedList(
                Note, backing.value, self._from_obj, self._to_obj
            )
        return self._notes

    @property
    def highlights(self) -> typing.List[Highlight]:
        if self._highlights is None:
            backing = self._get_or_compute(keys.ANNOTATION_HIGHLIGHTS, True)
            # asserts to placate IntelliJ intellisense
            assert isinstance(backing, NamedValue)
            assert backing.name == "saved.avl.interval.tree"
            self._highlights = WrappedList(
                Highlight, backing.value, self._from_obj, self._to_obj
            )
        return self._highlights

    @property
    def clip_articles(self) -> typing.List[ClipArticle]:
        if self._clip_articles is None:
            backing = self._get_or_compute(keys.ANNOTATION_CLIP_ARTICLES, True)
            # asserts to placate IntelliJ intellisense
            assert isinstance(backing, NamedValue)
            assert backing.name == "saved.avl.interval.tree"
            self._clip_articles = WrappedList(
                ClipArticle, backing.value, self._from_obj, self._to_obj
            )
        return self._clip_articles

    def _get_or_compute(
        self, name_id: int, compute_if_absent: bool = False
    ) -> Value:
        wrapper = None
        if compute_if_absent:
            wrapper = self._value.value.value.compute_if_absent(name_id)
        else:
            wrapper = self._value.value.value.get(name_id)
        return wrapper


class AnnotationStore:
    def __init__(self):
        self._value: DataStore = DataStore()
        self._annotation_cache: None | AnnotationCache = None

    def read(self, data: bytes):
        cursor = Cursor(data)
        self._value.read(cursor)

    def write(self) -> bytes:
        cursor = Cursor()
        self._value.write(cursor)
        return cursor.dump()

    @property
    def sync_lpr(self) -> bool:
        root = self._get_datastore_map()
        return root.compute_if_absent(names.SYNC_LPR).value.value

    @sync_lpr.setter
    def sync_lpr(self, value: bool):
        root = self._get_datastore_map()
        root.compute_if_absent(names.SYNC_LPR).value.value = value

    @property
    def annotation_cache(self) -> AnnotationCache:
        if self._annotation_cache is None:
            backing = self._get_annotation_cache(True)
            self._annotation_cache = AnnotationCache(backing)
        return self._annotation_cache

    def _get_annotation_cache(
        self, compute_if_absent: bool = False
    ) -> None | NamedValue:
        root = self._get_datastore_map()

        # NamedValue{annotation.cache.object}
        anno_cache_obj = None
        if root:
            anno_cache_obj = (
                root.compute_if_absent(names.ANNOTATION_CACHE_OBJECT) if
                compute_if_absent else root.get(names.ANNOTATION_CACHE_OBJECT)
            )
        return anno_cache_obj

    def _get_datastore_map(self):
        # top-level container
        return self._value.value.value
