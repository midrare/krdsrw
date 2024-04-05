import typing

from .basics import Bool
from .basics import Byte
from .basics import Char
from .basics import Short
from .basics import Int
from .basics import Long
from .basics import Float
from .basics import Double
from .basics import Utf8Str
from .specs import Spec

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
_timer_average_calculator_factory: None | Spec = None
_timer_average_calculator_distribution_normal_factory: None | Spec = None
_timer_average_calculator_calculator_outliers_factory: None | Spec = None
_datetime_factory: None | Spec = None
_position_factory: None | Spec = None
_dynamic_map_factory: None | Spec = None
_timezoneoffset_factory: None | Spec = None
_json_factory: None | Spec = None

_schema_to_factory: dict[str, None | Spec] = {}


def _timer_average_calculator_outliers() -> Spec:
    global _timer_average_calculator_calculator_outliers_factory
    if not _timer_average_calculator_calculator_outliers_factory:
        from .objects import Array
        _timer_average_calculator_calculator_outliers_factory \
            = Array.spec(_double)

    return _timer_average_calculator_calculator_outliers_factory


def _timer_average_calculator_distribution_normal() -> Spec:
    global _timer_average_calculator_distribution_normal_factory
    if not _timer_average_calculator_distribution_normal_factory:
        from .objects import Record
        _timer_average_calculator_distribution_normal_factory = Record.spec({
            "count":
            _long,
            "sum":
            _double,
            "sum_of_squares":
            _double,
        })

    return _timer_average_calculator_distribution_normal_factory


def _timer_average_calculator() -> Spec:
    global _timer_average_calculator_factory
    if not _timer_average_calculator_factory:
        from .objects import Array
        from .objects import Record
        _timer_average_calculator_factory = Record.spec({
            "samples1":
            Array.spec(_double),
            "samples2":
            Array.spec(_double),
            "normal_distributions":
            Array.spec(
                _timer_average_calculator_distribution_normal(),
                "timer.average.calculator.distribution.normal",
            ),
            "outliers":
            Array.spec(
                _timer_average_calculator_outliers(),
                "timer.average.calculator.outliers",
            ),
        })

    return _timer_average_calculator_factory


def _timer_model() -> Spec:
    global _timer_model_factory
    if not _timer_model_factory:
        from .objects import Record

        _timer_model_factory = Record.spec({
            "version":
            _long,
            "total_time":
            _long,
            "total_words":
            _long,
            "total_percent":
            _double,
            "average_calculator":
            (_timer_average_calculator(), "timer.average.calculator"),
        })

    return _timer_model_factory


def _font_prefs() -> Spec:
    global _font_prefs_factory
    if not _font_prefs_factory:
        from .objects import Record

        _font_prefs_factory = Record.spec({
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
        from .objects import Record

        _reader_state_preferences_factory = Record.spec({
            "font_preferences":
            _font_prefs(),
            "left_margin":
            _int,
            "right_margin":
            _int,
            "top_margin":
            _int,
            "bottom_margin":
            _int,
            "unknown1":
            _bool,
        })

    return _reader_state_preferences_factory


def _annotation_cache_object() -> Spec:
    global _annotation_object_cache_factory
    if not _annotation_object_cache_factory:
        from .objects import Array
        from .objects import IntMap

        _annotation_object_cache_factory = IntMap.spec([
            (
                "bookmarks", "saved.avl.interval.tree",
                Array.spec(
                    _annotation_personal_element(),
                    "annotation.personal.bookmark")),
            (
                "highlights", "saved.avl.interval.tree",
                Array.spec(
                    _annotation_personal_element(),
                    "annotation.personal.highlight")),
            (
                "notes", "saved.avl.interval.tree",
                Array.spec(
                    _annotation_personal_element(),
                    "annotation.personal.note")),
            (
                "clip_articles", "saved.avl.interval.tree",
                Array.spec(
                    _annotation_personal_element(),
                    "annotation.personal.clip_article")),
        ])

    return _annotation_object_cache_factory


def _annotation_personal_element() -> Spec:
    global _annotation_personal_element_factory
    if not _annotation_personal_element_factory:
        from .objects import Record

        _annotation_personal_element_factory = Record.spec(
            {
                "start_pos": _position(),
                "end_pos": _position(),
                "creation_time": _datetime(),
                "last_modification_time": _datetime(),
                "template": _utf8str,
            }, {
                "note": _utf8str,
            })
    return _annotation_personal_element_factory


def _datetime() -> Spec:
    global _datetime_factory
    if not _datetime_factory:
        from .objects import DateTime
        _datetime_factory = Spec(DateTime)
    return _datetime_factory


def _position() -> Spec:
    global _position_factory
    if not _position_factory:
        from .objects import Position
        _position_factory = Spec(Position)
    return _position_factory


def _dynamic_map() -> Spec:
    global _dynamic_map_factory
    if not _dynamic_map_factory:
        from .objects import DynamicMap
        _dynamic_map_factory = Spec(DynamicMap)
    return _dynamic_map_factory


def _timezone_offset() -> Spec:
    global _timezoneoffset_factory
    if not _timezoneoffset_factory:
        from .objects import TimeZoneOffset
        _timezoneoffset_factory = Spec(TimeZoneOffset)
    return _timezoneoffset_factory


def _json() -> Spec:
    global _json_factory
    if not _json_factory:
        from .objects import Json
        _json_factory = Spec(Json)
    return _json_factory


def _get_schema_to_factory() -> dict[str, None | Spec]:
    global _schema_to_factory
    if not _schema_to_factory:
        from .objects import Array
        from .objects import Record
        from .objects import LPR

        # NOTE if you update this schema map update the type hint maker too
        _schema_to_factory = {
            "clock.data.store":
            NotImplemented,
            "dictionary":
            _utf8str,
            "lpu":
            NotImplemented,
            "pdf.contrast":
            NotImplemented,
            "sync_lpr":
            _bool,
            "tpz.line.spacing":
            NotImplemented,
            "XRAY_OTA_UPDATE_STATE":
            NotImplemented,
            "XRAY_SHOWING_SPOILERS":
            NotImplemented,
            "XRAY_SORTING_STATE":
            NotImplemented,
            "XRAY_TAB_STATE":
            NotImplemented,
            "dict.prefs.v2":
            _dynamic_map(),
            "EndActions":
            _dynamic_map(),
            "ReaderMetrics":
            _dynamic_map(),
            "StartActions":
            _dynamic_map(),
            "Translator":
            _dynamic_map(),
            "Wikipedia":
            _dynamic_map(),
            "buy.asin.response.data":
            _json(),
            "next.in.series.info.data":
            _json(),
            "price.info.data":
            _json(),
            "erl":
            _position(),
            "lpr":
            Spec(LPR),
            "fpr":
            Record.spec({
                "pos": _position(),
            }, {
                "timestamp": _datetime(),
                "timezone_offset": _timezone_offset(),
                "country": _utf8str,
                "device": _utf8str,
            }),
            "updated_lpr":
            Record.spec({
                "pos": _position(),
            }, {
                "timestamp": _datetime(),
                "timezone_offset": _timezone_offset(),
                "country": _utf8str,
                "device": _utf8str,
            }),

            # amzn page num xref (i.e. page num map)
            "apnx.key":
            Record.spec({
                "asin": _utf8str,
                "cde_type": _utf8str,
                "sidecar_available": _bool,
                "opn_to_pos": Array.spec(_int),
                "first": _int,
                "unknown1": _int,
                "unknown2": _int,
                "page_map": _utf8str,
            }),
            "fixed.layout.data":
            Record.spec({
                "unknown1": _bool,
                "unknown2": _bool,
                "unknown3": _bool,
            }),
            "sharing.limits":
            Record.spec({
                # TODO discover structure for sharing.limits
                "accumulated": NotImplemented
            }),
            "language.store":
            Record.spec({
                "language": _utf8str,
                "unknown1": _int,
            }),
            "periodicals.view.state":
            Record.spec({
                "unknown1": _utf8str,
                "unknown2": _int,
            }),
            "purchase.state.data":
            Record.spec({
                "state": _int,
                "time": _datetime(),
            }),
            "timer.model":
            _timer_model(),
            "timer.data.store":
            Record.spec({
                "on": _bool,
                "reading_timer_model": _timer_model(),
                "version": _int,
            }),
            "timer.data.store.v2":
            Record.spec({
                "on": _bool,
                "reading_timer_model": _timer_model(),
                "version": _int,
                "last_option": _int,
            }),
            "book.info.store":
            Record.spec({
                "num_words": _long,
                "percent_of_book": _double,
            }),
            "page.history.store":
            Array.spec(
                Record.spec({
                    "pos": _position(),
                    "time": _datetime(),
                }),
                "page.history.record",
            ),
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
            "whisperstore.migration.status":
            Record.spec({
                "unknown1": _bool,
                "unknown2": _bool,
            }),
            "timer.average.calculator.distribution.normal":
            _timer_average_calculator_distribution_normal(),
            "timer.average.calculator.outliers":
            _timer_average_calculator_outliers(),
        }
    return _schema_to_factory


def get_factory_by_schema(schema: str) -> None | Spec:
    return _get_schema_to_factory().get(schema)
