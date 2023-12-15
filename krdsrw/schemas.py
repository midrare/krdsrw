import typing

from .types import Bool
from .types import Byte
from .types import Char
from .types import Short
from .types import Int
from .types import Long
from .types import Float
from .types import Double
from .types import Utf8Str
from .types import Spec

_bool: typing.Final[Spec[Bool]] = Spec(Bool)
_byte: typing.Final[Spec[Byte]] = Spec(Byte)
_char: typing.Final[Spec[Char]] = Spec(Char)
_short: typing.Final[Spec[Short]] = Spec(Short)
_int: typing.Final[Spec[Int]] = Spec(Int)
_long: typing.Final[Spec[Long]] = Spec(Long)
_float: typing.Final[Spec[Float]] = Spec(Float)
_double: typing.Final[Spec[Double]] = Spec(Double)
_utf8str: typing.Final[Spec[Utf8Str]] = Spec(Utf8Str)

_timer_model_factory: None | Spec = None
_font_prefs_factory: None | Spec = None
_reader_state_preferences_factory: None | Spec = None
_annotation_object_cache_factory: None | Spec = None
_annotation_personal_element_factory: None | Spec = None
_name_to_factory_map: dict[str, None | Spec] = {}


def _timer_model() -> Spec:
    global _timer_model_factory
    if not _timer_model_factory:
        from .containers import Array
        from .containers import Record
        from .containers import Spec

        _timer_model_factory = Spec(
            Record, {
                "version":
                _long,
                "total_time":
                _long,
                "total_words":
                _long,
                "total_percent":
                _double,
                "average_calculator": (
                    "timer.average.calculator",
                    Spec(
                        Record, {
                            "samples1":
                            Spec(Array, _double),
                            "samples2":
                            Spec(Array, _double),
                            "normal_distributions":
                            Spec(
                                Array,
                                Spec(
                                    Record, {
                                        "count": _long,
                                        "sum": _double,
                                        "sum_of_squares": _double,
                                    })),
                            "outliers":
                            Spec(Array, Spec(Array, _double)),
                        })),
            })

    return _timer_model_factory


def _font_prefs() -> Spec:
    global _font_prefs_factory
    if not _font_prefs_factory:
        from .containers import Record

        _font_prefs_factory = Spec(
            Record, {
                "typeface": _utf8str,
                "line_sp": _int,
                "size": _int,
                "align": _int,
                "inset_top": _int,
                "inset_left": _int,
                "inset_bottom": _int,
                "inset_right": _int,
                "unknown1": _int,
            }, {
                "bold": _int,
                "user_sideloadable_font": _utf8str,
                "custom_font_index": _int,
                "mobi7_system_font": _utf8str,
                "mobi7_restore_font": _bool,
                "reading_preset_selected": _utf8str,
            })

    return _font_prefs_factory


def _reader_state_preferences() -> Spec:
    global _reader_state_preferences_factory
    if not _reader_state_preferences_factory:
        from .containers import Record

        _reader_state_preferences_factory = Spec(
            Record, {
                "font_preferences": _font_prefs(),
                "left_margin": _int,
                "right_margin": _int,
                "top_margin": _int,
                "bottom_margin": _int,
                "unknown1": _bool,
            })

    return _reader_state_preferences_factory


def _annotation_cache_object() -> Spec:
    global _annotation_object_cache_factory
    if not _annotation_object_cache_factory:
        from .containers import Array
        from .containers import IntMap

        _annotation_object_cache_factory = Spec(
            IntMap, [
                (
                    0, "bookmarks", "saved.avl.interval.tree",
                    Spec(
                        Array, _annotation_personal_element(),
                        "annotation.personal.bookmark")),
                (
                    1, "highlights", "saved.avl.interval.tree",
                    Spec(
                        Array, _annotation_personal_element(),
                        "annotation.personal.highlight")),
                (
                    2, "notes", "saved.avl.interval.tree",
                    Spec(
                        Array, _annotation_personal_element(),
                        "annotation.personal.note")),
                (
                    3, "clip_articles", "saved.avl.interval.tree",
                    Spec(
                        Array, _annotation_personal_element(),
                        "annotation.personal.clip_article")),
            ])

    return _annotation_object_cache_factory


def _annotation_personal_element() -> Spec:
    global _annotation_personal_element_factory
    if not _annotation_personal_element_factory:
        from .containers import DateTime
        from .containers import Record
        from .containers import Position

        _annotation_personal_element_factory = Spec(
            Record, {
                "start_pos": Spec(Position),
                "end_pos": Spec(Position),
                "creation_time": Spec(DateTime),
                "last_modification_time": Spec(DateTime),
                "template": _utf8str,
            }, {
                "note": _utf8str,
            })
    return _annotation_personal_element_factory


def _name_to_factory() -> dict[str, None | Spec]:
    global _name_to_factory_map
    if not _name_to_factory_map:
        from .containers import DateTime
        from .containers import DynamicMap
        from .containers import Array
        from .containers import Record
        from .containers import Json
        from .containers import LastPageRead
        from .containers import Position
        from .containers import TimeZoneOffset

        _name_to_factory_map = {
            "clock.data.store":
            None,
            "dictionary":
            _utf8str,
            "lpu":
            None,
            "pdf.contrast":
            None,
            "sync_lpr":
            _bool,
            "tpz.line.spacing":
            None,
            "XRAY_OTA_UPDATE_STATE":
            None,
            "XRAY_SHOWING_SPOILERS":
            None,
            "XRAY_SORTING_STATE":
            None,
            "XRAY_TAB_STATE":
            None,
            "dict.prefs.v2":
            Spec(DynamicMap),
            "EndActions":
            Spec(DynamicMap),
            "ReaderMetrics":
            Spec(DynamicMap),
            "StartActions":
            Spec(DynamicMap),
            "Translator":
            Spec(DynamicMap),
            "Wikipedia":
            Spec(DynamicMap),
            "buy.asin.response.data":
            Spec(Json),
            "next.in.series.info.data":
            Spec(Json),
            "price.info.data":
            Spec(Json),
            "erl":
            Spec(Position),
            "lpr":
            Spec(LastPageRead),
            "fpr":
            Spec(
                Record, {
                    "pos": Spec(Position),
                }, {
                    "timestamp": Spec(DateTime),
                    "timezone_offset": Spec(TimeZoneOffset),
                    "country": _utf8str,
                    "device": _utf8str,
                }),
            "updated_lpr":
            Spec(
                Record, {
                    "pos": Spec(Position),
                }, {
                    "timestamp": Spec(DateTime),
                    "timezone_offset": Spec(TimeZoneOffset),
                    "country": _utf8str,
                    "device": _utf8str,
                }),

            # amzn page num xref (i.e. page num map)
            "apnx.key":
            Spec(
                Record, {
                    "asin": _utf8str,
                    "cde_type": _utf8str,
                    "sidecar_available": _bool,
                    "opn_to_pos": Spec(Array, _int),
                    "first": _int,
                    "unknown1": _int,
                    "unknown2": _int,
                    "page_map": _utf8str,
                }),
            "fixed.layout.data":
            Spec(
                Record, {
                    "unknown1": _bool,
                    "unknown2": _bool,
                    "unknown3": _bool,
                }),
            "sharing.limits":
            Spec(
                Record,
                {
                    # TODO discover structure for sharing.limits
                    "accumulated": None
                }),
            "language.store":
            Spec(Record, {
                "language": _utf8str,
                "unknown1": _int,
            }),
            "periodicals.view.state":
            Spec(Record, {
                "unknown1": _utf8str,
                "unknown2": _int,
            }),
            "purchase.state.data":
            Spec(Record, {
                "state": _int,
                "time": Spec(DateTime),
            }),
            "timer.model":
            _timer_model(),
            "timer.data.store":
            Spec(
                Record, {
                    "on": _bool,
                    "reading_timer_model": _timer_model(),
                    "version": _int,
                }),
            "timer.data.store.v2":
            Spec(
                Record, {
                    "on": _bool,
                    "reading_timer_model": _timer_model(),
                    "version": _int,
                    "last_option": _int,
                }),
            "book.info.store":
            Spec(Record, {
                "num_words": _long,
                "percent_of_book": _double,
            }),
            "page.history.store":
            Spec(
                Array,
                Spec(
                    Record, {
                        "pos": Spec(Position),
                        "time": Spec(DateTime),
                    })),
            "reader.state.preferences":
            _reader_state_preferences(),
            "font.prefs":
            _font_prefs(),
            "annotation.cache.object":
            _annotation_cache_object(),
            "annotation.personal.bookmark":
            _annotation_personal_element(),
            "annotation.personal.highlight":
            _annotation_personal_element(),
            "annotation.personal.note":
            _annotation_personal_element(),
            "annotation.personal.clip_article":
            _annotation_personal_element(),
        }
    return _name_to_factory_map


def get_spec_by_name(name: str) -> None | Spec:
    return _name_to_factory().get(name)
