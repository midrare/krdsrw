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
from .cursor import ValFactory

_bool: typing.Final[ValFactory[Bool]] = ValFactory(Bool)
_byte: typing.Final[ValFactory[Byte]] = ValFactory(Byte)
_char: typing.Final[ValFactory[Char]] = ValFactory(Char)
_short: typing.Final[ValFactory[Short]] = ValFactory(Short)
_int: typing.Final[ValFactory[Int]] = ValFactory(Int)
_long: typing.Final[ValFactory[Long]] = ValFactory(Long)
_float: typing.Final[ValFactory[Float]] = ValFactory(Float)
_double: typing.Final[ValFactory[Double]] = ValFactory(Double)
_utf8str: typing.Final[ValFactory[Utf8Str]] = ValFactory(Utf8Str)

_timer_model_factory: None | ValFactory = None
_font_prefs_factory: None | ValFactory = None
_reader_state_preferences_factory: None | ValFactory = None
_annotation_object_cache_factory: None | ValFactory = None
_annotation_personal_factory: None | ValFactory = None
_name_to_factory_map: dict[str, None | ValFactory] = {}


def _timer_model() -> ValFactory:
    global _timer_model_factory
    if not _timer_model_factory:
        from .containers import Array
        from .containers import FixedMap
        from .containers import ValFactory

        # timer.model
        _timer_model_factory = ValFactory(
            FixedMap,
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
            ValFactory(
            FixedMap,
            {
            "samples1":
            ValFactory(Array, _double),
            "samples2":
            ValFactory(Array, _double),

            # timer.average.calculator.distribution.normal
            "normal_distributions":
            ValFactory(
            Array,
            ValFactory(
            FixedMap, {
            "count": _long,
            "sum": _double,
            "sum_of_squares": _double,
            }
            )
            ),

  # timer.average.calculator.outliers
            "outliers":
            ValFactory(Array, ValFactory(Array, _double)),
            }
            ),
            }
        )

    return _timer_model_factory


def _font_prefs() -> ValFactory:
    global _font_prefs_factory
    if not _font_prefs_factory:
        from .containers import FixedMap

        _font_prefs_factory = ValFactory(
            FixedMap,
            {
            "typeface": _utf8str,
            "line_sp": _int,
            "size": _int,
            "align": _int,
            "inset_top": _int,
            "inset_left": _int,
            "inset_bottom": _int,
            "inset_right": _int,
            "unknown1": _int,
            },
            {
            "bold": _int,
            "user_sideloadable_font": _utf8str,
            "custom_font_index": _int,
            "mobi7_system_font": _utf8str,
            "mobi7_restore_font": _bool,
            "reading_preset_selected": _utf8str,
            }
        )

    return _font_prefs_factory


def _reader_state_preferences() -> ValFactory:
    global _reader_state_preferences_factory
    if not _reader_state_preferences_factory:
        from .containers import FixedMap

        # reader.state.preferences
        _reader_state_preferences_factory = ValFactory(
            FixedMap,
            {
            "font_preferences": _font_prefs(),
            "left_margin": _int,
            "right_margin": _int,
            "top_margin": _int,
            "bottom_margin": _int,
            "unknown1": _bool,
            }
        )

    return _reader_state_preferences_factory


def _annotation_object_cache() -> ValFactory:
    global _annotation_object_cache_factory
    if not _annotation_object_cache_factory:
        from .containers import Array
        from .containers import SwitchMap
        from .cursor import Value

        # annotation.cache.object
        _annotation_object_cache_factory = ValFactory(
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
            ValFactory(
            Array,
            ValFactory(Value, _name="annotation.personal.bookmark"),
            ),  # annotation.personal.highlight
            1:
            ValFactory(
            Array,
            ValFactory(Value, _name="annotation.personal.highlight"),
            ),  # annotation.personal.note
            2:
            ValFactory(
            Array,
            ValFactory(Value, _name="annotation.personal.note"),
            ),  # annotation.personal.clip_article
            3:
            ValFactory(
            Array,
            ValFactory(Value, _name="annotation.personal.clip_article"),
            ),
            }
        )

    return _annotation_object_cache_factory


def _annotation_personal() -> ValFactory:
    global _annotation_personal_factory
    if not _annotation_personal_factory:
        from .containers import DateTime
        from .containers import FixedMap
        from .containers import Position

        # annotation.personal.bookmark
        # annotation.personal.clip_article
        # annotation.personal.highlight
        # annotation.personal.note
        _annotation_personal_factory = ValFactory(
            FixedMap,
            {
            "start_pos": Position,
            "end_pos": Position,
            "creation_time": DateTime,
            "last_modification_time": DateTime,
            "template": _utf8str,
            }, {
            "note": _utf8str,
            }
        )
    return _annotation_personal_factory


def _name_to_factory() -> dict[str, None | ValFactory]:
    global _name_to_factory_map
    if not _name_to_factory_map:
        from .containers import Array
        from .containers import DateTime
        from .containers import DynamicMap
        from .containers import FixedMap
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
            ValFactory(DynamicMap),
            "EndActions":
            ValFactory(DynamicMap),
            "ReaderMetrics":
            ValFactory(DynamicMap),
            "StartActions":
            ValFactory(DynamicMap),
            "Translator":
            ValFactory(DynamicMap),
            "Wikipedia":
            ValFactory(DynamicMap),
            "buy.asin.response.data":
            ValFactory(Json),
            "next.in.series.info.data":
            ValFactory(Json),
            "price.info.data":
            ValFactory(Json),
            "erl":
            ValFactory(Position),
            "lpr":
            ValFactory(LastPageRead),
            "fpr":
            ValFactory(
            FixedMap, {
            "pos": ValFactory(Position),
            },
            {
            "timestamp": ValFactory(DateTime),
            "timezone_offset": TimeZoneOffset,
            "country": _utf8str,
            "device": _utf8str,
            }
            ),
            "updated_lpr":
            ValFactory(
            FixedMap, {
            "pos": ValFactory(Position),
            },
            {
            "timestamp": ValFactory(DateTime),
            "timezone_offset": TimeZoneOffset,
            "country": _utf8str,
            "device": _utf8str,
            }
            ),

  # amzn page num xref (i.e. page num map)
            "apnx.key":
            ValFactory(
            FixedMap,
            {
            "asin": _utf8str,
            "cde_type": _utf8str,
            "sidecar_available": _bool,
            "opn_to_pos": ValFactory(Array, _int),
            "first": _int,
            "unknown1": _int,
            "unknown2": _int,
            "page_map": _utf8str,
            }
            ),
            "fixed.layout.data":
            ValFactory(
            FixedMap, {
            "unknown1": _bool,
            "unknown2": _bool,
            "unknown3": _bool,
            }
            ),
            "sharing.limits":
            ValFactory(
            FixedMap,
            {
            # TODO discover structure for sharing.limits
            "accumulated": None
            }
            ),
            "language.store":
            ValFactory(FixedMap, {
            "language": _utf8str,
            "unknown1": _int,
            }),
            "periodicals.view.state":
            ValFactory(FixedMap, {
            "unknown1": _utf8str,
            "unknown2": _int,
            }),
            "purchase.state.data":
            ValFactory(
            FixedMap, {
            "state": _int,
            "time": ValFactory(DateTime),
            }
            ),
            "timer.data.store":
            ValFactory(
            FixedMap,
            {
            "on": _bool,
            "reading_timer_model": _timer_model(),
            "version": _int,
            }
            ),
            "timer.data.store.v2":
            ValFactory(
            FixedMap,
            {
            "on": _bool,
            "reading_timer_model": _timer_model(),
            "version": _int,
            "last_option": _int,
            }
            ),
            "book.info.store":
            ValFactory(
            FixedMap, {
            "num_words": _long,
            "percent_of_book": _double,
            }
            ),
            "page.history.store":
            ValFactory(
            Array,
            ValFactory(
            FixedMap, {
            "pos": ValFactory(Position),
            "time": ValFactory(DateTime),
            }
            )
            ),
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


def get_maker_by_name(name: str) -> None | ValFactory:
    return _name_to_factory().get(name)
