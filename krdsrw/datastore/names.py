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
from .types import ValueFactory

_bool: typing.Final[ValueFactory[Bool]] = ValueFactory(Bool)
_byte: typing.Final[ValueFactory[Byte]] = ValueFactory(Byte)
_char: typing.Final[ValueFactory[Char]] = ValueFactory(Char)
_short: typing.Final[ValueFactory[Short]] = ValueFactory(Short)
_int: typing.Final[ValueFactory[Int]] = ValueFactory(Int)
_long: typing.Final[ValueFactory[Long]] = ValueFactory(Long)
_float: typing.Final[ValueFactory[Float]] = ValueFactory(Float)
_double: typing.Final[ValueFactory[Double]] = ValueFactory(Double)
_utf8str: typing.Final[ValueFactory[Utf8Str]] = ValueFactory(Utf8Str)

_timer_model_factory: None | ValueFactory = None
_font_prefs_factory: None | ValueFactory = None
_reader_state_preferences_factory: None | ValueFactory = None
_annotation_object_cache_factory: None | ValueFactory = None
_annotation_personal_factory: None | ValueFactory = None
_name_to_factory_map: dict[str, None | ValueFactory] = {}


def _timer_model() -> ValueFactory:
    global _timer_model_factory
    if not _timer_model_factory:
        from .containers import Array
        from .containers import Record
        from .containers import ValueFactory

        # timer.model
        _timer_model_factory = ValueFactory(
            Record,
            {
                "version":
                _long,
                "total_time":
                _long,
                "total_words":
                _long,
                "total_percent":
                _double,

                # timer.average.calculator
                "average_calculator":
                ValueFactory(
                    Record,
                    {
                        "samples1":
                        ValueFactory(Array, _double),
                        "samples2":
                        ValueFactory(Array, _double),

                        # timer.average.calculator.distribution.normal
                        "normal_distributions":
                        ValueFactory(
                            Array,
                            ValueFactory(
                                Record, {
                                    "count": _long,
                                    "sum": _double,
                                    "sum_of_squares": _double,
                                })),

                        # timer.average.calculator.outliers
                        "outliers":
                        ValueFactory(Array, ValueFactory(Array, _double)),
                    }),
            })

    return _timer_model_factory


def _font_prefs() -> ValueFactory:
    global _font_prefs_factory
    if not _font_prefs_factory:
        from .containers import Record

        _font_prefs_factory = ValueFactory(
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


def _reader_state_preferences() -> ValueFactory:
    global _reader_state_preferences_factory
    if not _reader_state_preferences_factory:
        from .containers import Record

        # reader.state.preferences
        _reader_state_preferences_factory = ValueFactory(
            Record, {
                "font_preferences": _font_prefs(),
                "left_margin": _int,
                "right_margin": _int,
                "top_margin": _int,
                "bottom_margin": _int,
                "unknown1": _bool,
            })

    return _reader_state_preferences_factory


def _annotation_object_cache() -> ValueFactory:
    global _annotation_object_cache_factory
    if not _annotation_object_cache_factory:
        from .containers import Array
        from .containers import SwitchMap
        from .types import Object

        # annotation.cache.object
        _annotation_object_cache_factory = ValueFactory(
            SwitchMap,
            {
                0: "saved.avl.interval.tree",  # bookmarks
                1: "saved.avl.interval.tree",  # highlights
                2: "saved.avl.interval.tree",  # notes
                3: "saved.avl.interval.tree",  # clip articles
            },
            {
                # annotation.personal.bookmark
                0:
                ValueFactory(
                    Array,
                    ValueFactory(Object, _name="annotation.personal.bookmark"),
                ),  # annotation.personal.highlight
                1:
                ValueFactory(
                    Array,
                    ValueFactory(Object, _name="annotation.personal.highlight"),
                ),  # annotation.personal.note
                2:
                ValueFactory(
                    Array,
                    ValueFactory(Object, _name="annotation.personal.note"),
                ),  # annotation.personal.clip_article
                3:
                ValueFactory(
                    Array,
                    ValueFactory(
                        Object, _name="annotation.personal.clip_article"),
                ),
            })

    return _annotation_object_cache_factory


def _annotation_personal() -> ValueFactory:
    global _annotation_personal_factory
    if not _annotation_personal_factory:
        from .containers import DateTime
        from .containers import Record
        from .containers import Position

        # annotation.personal.bookmark
        # annotation.personal.clip_article
        # annotation.personal.highlight
        # annotation.personal.note
        _annotation_personal_factory = ValueFactory(
            Record, {
                "start_pos": Position,
                "end_pos": Position,
                "creation_time": DateTime,
                "last_modification_time": DateTime,
                "template": _utf8str,
            }, {
                "note": _utf8str,
            })
    return _annotation_personal_factory


def _name_to_factory() -> dict[str, None | ValueFactory]:
    global _name_to_factory_map
    if not _name_to_factory_map:
        from .containers import Array
        from .containers import DateTime
        from .containers import DynamicMap
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
            ValueFactory(DynamicMap),
            "EndActions":
            ValueFactory(DynamicMap),
            "ReaderMetrics":
            ValueFactory(DynamicMap),
            "StartActions":
            ValueFactory(DynamicMap),
            "Translator":
            ValueFactory(DynamicMap),
            "Wikipedia":
            ValueFactory(DynamicMap),
            "buy.asin.response.data":
            ValueFactory(Json),
            "next.in.series.info.data":
            ValueFactory(Json),
            "price.info.data":
            ValueFactory(Json),
            "erl":
            ValueFactory(Position),
            "lpr":
            ValueFactory(LastPageRead),
            "fpr":
            ValueFactory(
                Record, {
                    "pos": ValueFactory(Position),
                }, {
                    "timestamp": ValueFactory(DateTime),
                    "timezone_offset": TimeZoneOffset,
                    "country": _utf8str,
                    "device": _utf8str,
                }),
            "updated_lpr":
            ValueFactory(
                Record, {
                    "pos": ValueFactory(Position),
                }, {
                    "timestamp": ValueFactory(DateTime),
                    "timezone_offset": TimeZoneOffset,
                    "country": _utf8str,
                    "device": _utf8str,
                }),

            # amzn page num xref (i.e. page num map)
            "apnx.key":
            ValueFactory(
                Record, {
                    "asin": _utf8str,
                    "cde_type": _utf8str,
                    "sidecar_available": _bool,
                    "opn_to_pos": ValueFactory(Array, _int),
                    "first": _int,
                    "unknown1": _int,
                    "unknown2": _int,
                    "page_map": _utf8str,
                }),
            "fixed.layout.data":
            ValueFactory(
                Record, {
                    "unknown1": _bool,
                    "unknown2": _bool,
                    "unknown3": _bool,
                }),
            "sharing.limits":
            ValueFactory(
                Record,
                {
                    # TODO discover structure for sharing.limits
                    "accumulated": None
                }),
            "language.store":
            ValueFactory(Record, {
                "language": _utf8str,
                "unknown1": _int,
            }),
            "periodicals.view.state":
            ValueFactory(Record, {
                "unknown1": _utf8str,
                "unknown2": _int,
            }),
            "purchase.state.data":
            ValueFactory(
                Record, {
                    "state": _int,
                    "time": ValueFactory(DateTime),
                }),
            "timer.data.store":
            ValueFactory(
                Record, {
                    "on": _bool,
                    "reading_timer_model": _timer_model(),
                    "version": _int,
                }),
            "timer.data.store.v2":
            ValueFactory(
                Record, {
                    "on": _bool,
                    "reading_timer_model": _timer_model(),
                    "version": _int,
                    "last_option": _int,
                }),
            "book.info.store":
            ValueFactory(
                Record, {
                    "num_words": _long,
                    "percent_of_book": _double,
                }),
            "page.history.store":
            ValueFactory(
                Array,
                ValueFactory(
                    Record, {
                        "pos": ValueFactory(Position),
                        "time": ValueFactory(DateTime),
                    })),
            "reader.state.preferences":
            _reader_state_preferences(),
            "font.prefs":
            _font_prefs(),
            "annotation.cache.object":
            _annotation_object_cache(),
            "annotation.personal.bookmark":
            _annotation_personal(),
            "annotation.personal.highlight":
            _annotation_personal(),
            "annotation.personal.note":
            _annotation_personal(),
            "annotation.personal.clip_article":
            _annotation_personal(),
        }
    return _name_to_factory_map


def get_maker_by_name(name: str) -> None | ValueFactory:
    return _name_to_factory().get(name)
