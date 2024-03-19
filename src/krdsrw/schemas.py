import argparse
import os
import sys
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
_timer_average_calculator_factory: None | Spec = None
_timer_average_calculator_distribution_normal_factory: None | Spec = None
_timer_average_calculator_calculator_outliers_factory: None | Spec = None

_name_to_factory_map: dict[str, None | Spec] = {}


def _timer_average_calculator_outliers() -> Spec:
    global _timer_average_calculator_calculator_outliers_factory
    if not _timer_average_calculator_calculator_outliers_factory:
        from .containers import Array
        _timer_average_calculator_calculator_outliers_factory = Spec(
            Array,
            _schema_array_elmt_spec=_double,
        )

    return _timer_average_calculator_calculator_outliers_factory


def _timer_average_calculator_distribution_normal() -> Spec:
    global _timer_average_calculator_distribution_normal_factory
    if not _timer_average_calculator_distribution_normal_factory:
        from .containers import Record
        from .containers import Spec
        _timer_average_calculator_distribution_normal_factory = Spec(
            Record,
            _schema_record_required={
                "count": _long,
                "sum": _double,
                "sum_of_squares": _double,
            })

    return _timer_average_calculator_distribution_normal_factory


def _timer_average_calculator() -> Spec:
    global _timer_average_calculator_factory
    if not _timer_average_calculator_factory:
        from .containers import Array
        from .containers import Record
        from .containers import Spec
        _timer_average_calculator_factory = Spec(
            Record,
            _schema_record_required={
                "samples1":
                Spec(Array, _schema_array_elmt_spec=_double),
                "samples2":
                Spec(Array, _schema_array_elmt_spec=_double),
                "normal_distributions":
                Spec(
                    Array,
                    _schema_array_elmt_spec=
                    _timer_average_calculator_distribution_normal(),
                    _schema_array_elmt_name=
                    "timer.average.calculator.distribution.normal",
                ),
                "outliers":
                Spec(
                    Array,
                    _schema_array_elmt_spec=_timer_average_calculator_outliers(
                    ),
                    _schema_array_elmt_name="timer.average.calculator.outliers",
                ),
            })

    return _timer_average_calculator_factory


def _timer_model() -> Spec:
    global _timer_model_factory
    if not _timer_model_factory:
        from .containers import Record
        from .containers import Spec

        _timer_model_factory = Spec(
            Record,
            _schema_record_required={
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
        from .containers import Record

        _font_prefs_factory = Spec(
            Record,
            _schema_record_required={
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
            _schema_record_optional={
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
            Record,
            _schema_record_required={
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
            IntMap,
            _schema_intmap_idx_alias_name_spec=[
                (
                    0, "bookmarks", "saved.avl.interval.tree",
                    Spec(
                        Array,
                        _schema_array_elmt_spec=_annotation_personal_element(),
                        _schema_array_elmt_name="annotation.personal.bookmark")
                ),
                (
                    1, "highlights", "saved.avl.interval.tree",
                    Spec(
                        Array,
                        _schema_array_elmt_spec=_annotation_personal_element(),
                        _schema_array_elmt_name="annotation.personal.highlight")
                ),
                (
                    2, "notes", "saved.avl.interval.tree",
                    Spec(
                        Array,
                        _schema_array_elmt_spec=_annotation_personal_element(),
                        _schema_array_elmt_name="annotation.personal.note")),
                (
                    3, "clip_articles", "saved.avl.interval.tree",
                    Spec(
                        Array,
                        _schema_array_elmt_spec=_annotation_personal_element(),
                        _schema_array_elmt_name=
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
            Record,
            _schema_record_required={
                "start_pos": Spec(Position),
                "end_pos": Spec(Position),
                "creation_time": Spec(DateTime),
                "last_modification_time": Spec(DateTime),
                "template": _utf8str,
            },
            _schema_record_optional={
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

        # NOTE if you update this schema map update the type hint maker too
        _name_to_factory_map = {
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
                Record,
                _schema_record_required={
                    "pos": Spec(Position),
                },
                _schema_record_optional={
                    "timestamp": Spec(DateTime),
                    "timezone_offset": Spec(TimeZoneOffset),
                    "country": _utf8str,
                    "device": _utf8str,
                }),
            "updated_lpr":
            Spec(
                Record,
                _schema_record_required={
                    "pos": Spec(Position),
                },
                _schema_record_optional={
                    "timestamp": Spec(DateTime),
                    "timezone_offset": Spec(TimeZoneOffset),
                    "country": _utf8str,
                    "device": _utf8str,
                }),

            # amzn page num xref (i.e. page num map)
            "apnx.key":
            Spec(
                Record,
                _schema_record_required={
                    "asin": _utf8str,
                    "cde_type": _utf8str,
                    "sidecar_available": _bool,
                    "opn_to_pos": Spec(Array, _schema_array_elmt_spec=_int),
                    "first": _int,
                    "unknown1": _int,
                    "unknown2": _int,
                    "page_map": _utf8str,
                }),
            "fixed.layout.data":
            Spec(
                Record,
                _schema_record_required={
                    "unknown1": _bool,
                    "unknown2": _bool,
                    "unknown3": _bool,
                }),
            "sharing.limits":
            Spec(
                Record,
                _schema_record_required={
                    # TODO discover structure for sharing.limits
                    "accumulated": NotImplemented
                }),
            "language.store":
            Spec(
                Record,
                _schema_record_required={
                    "language": _utf8str,
                    "unknown1": _int,
                }),
            "periodicals.view.state":
            Spec(
                Record,
                _schema_record_required={
                    "unknown1": _utf8str,
                    "unknown2": _int,
                }),
            "purchase.state.data":
            Spec(
                Record,
                _schema_record_required={
                    "state": _int,
                    "time": Spec(DateTime),
                }),
            "timer.model":
            _timer_model(),
            "timer.data.store":
            Spec(
                Record,
                _schema_record_required={
                    "on": _bool,
                    "reading_timer_model": _timer_model(),
                    "version": _int,
                }),
            "timer.data.store.v2":
            Spec(
                Record,
                _schema_record_required={
                    "on": _bool,
                    "reading_timer_model": _timer_model(),
                    "version": _int,
                    "last_option": _int,
                }),
            "book.info.store":
            Spec(
                Record,
                _schema_record_required={
                    "num_words": _long,
                    "percent_of_book": _double,
                }),
            "page.history.store":
            Spec(
                Array,
                _schema_array_elmt_spec=Spec(
                    Record,
                    _schema_record_required={
                        "pos": Spec(Position),
                        "time": Spec(DateTime),
                    }),
                _schema_array_elmt_name="page.history.record",
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
            Spec(
                Record,
                _schema_record_required={
                    "unknown1": _bool,
                    "unknown2": _bool,
                },
            ),
            "timer.average.calculator.distribution.normal":
            _timer_average_calculator_distribution_normal(),
            "timer.average.calculator.outliers":
            _timer_average_calculator_outliers(),
        }
    return _name_to_factory_map


def get_spec_by_name(name: str) -> None | Spec:
    return _name_to_factory().get(name)


def _path_arg(
    exists: bool | None,
    type: str | None,
    alt: None | typing.Literal['file', 'dir']
    | list[typing.Literal['file', 'dir']] = None,
) -> typing.Callable[[str], str]:
    if isinstance(alt, str):
        alt = [alt]
    if not alt:
        alt = []

    def check(arg: str) -> str:
        if arg in alt:
            return arg

        if exists is True and not os.path.exists(arg):
            raise argparse.ArgumentTypeError(f'Path "{arg}" does not exist.')

        if exists is True and type == "file" and not os.path.isfile(arg):
            raise argparse.ArgumentTypeError(f'"{arg}" is not a file.')

        if exists is True and type == "dir" and not os.path.isdir(arg):
            raise argparse.ArgumentTypeError(f'"{arg}" is not a directory.')

        if exists is False and os.path.exists(arg):
            raise argparse.ArgumentTypeError(f'Path "{arg}" exists.')

        if type == "file" and os.path.exists(arg) and not os.path.isfile(arg):
            raise argparse.ArgumentTypeError(
                f'Path "{arg}" exists and is not a file.')

        if type == "dir" and os.path.exists(arg) and not os.path.isdir(arg):
            raise argparse.ArgumentTypeError(
                f'Path "{arg}" exists and is not a directory.')

        return arg

    return check


def _make_dict_methods(
    key: str,
    value: None | str = None,
    overload_: bool = True,
) -> str:
    decorator = ''
    if overload_:
        decorator = '@typing.overload'

    if key is None:
        key = "typing.Any"

    if value is None:
        value = "typing.Any"

    return f"""\n\n
    {decorator}
    def __getitem__(
        self,
        key: {key},  # type: ignore
    ) -> {value}:  # type: ignore
        {'return super().__getitem__(key)' if not overload_ else '...'}

    {decorator}
    def __contains__(
        self,
        key: {key},  # type: ignore
    ) -> bool:
        {'return super().__contains__(key)' if not overload_ else '...'}

    {decorator}
    def __delitem__(
        self,
        key: {key},  # type: ignore
    ):
        {'super().__delitem__(key)' if not overload_ else '...'}

    {decorator}
    def __setitem__(
        self,
        key: {key},  # type: ignore
        item: {value},  # type: ignore
    ):
        {'super().__setitem__(key, item)' if not overload_ else '...'}

    {decorator}
    def get(
        self,
        key: {key},  # type: ignore
        default: None | {value} = None,  # type: ignore
    ) -> None | {value}:  # type: ignore
        {'return super().get(key, default)' if not overload_ else '...'}

    {decorator}
    def pop(
        self,
        key: {key},  # type: ignore
        default: None | {value} = None,  # type: ignore
    ) -> None | {value}:  # type: ignore
        {'return super().pop(key, default)' if not overload_ else '...'}

    {decorator}
    def setdefault(
        self,
        key: {key},  # type: ignore
        default: None | {value} = None,  # type: ignore
    ):
        {'return super().setdefault(key, default)' if not overload_ else '...'}
    \n\n"""


def _main(argv: list[str]) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="generate container type hints")

    parser.add_argument(
        "-o",
        "--output",
        help="path to output file",
        type=_path_arg(exists=None, type="file"),
    )

    args = parser.parse_args(argv)
    with open(args.output, 'w') as f:
        f.write('# THIS FILE IS AUTOMATICALLY GENERATED. DO NOT\n')
        f.write('# MODIFY. ALL CHANGES WILL BE UNDONE.\n')
        f.write('\n')
        f.write("# NOLINTBEGIN\n")
        f.write("# @formatter:off\n")
        f.write('import typing\n')
        f.write('\n')
        f.write('from .types import *\n')
        f.write('from .containers import *\n')
        f.write('from .containers import RestrictedDict\n')
        f.write('\n')
        f.write('class _SchemaDict(RestrictedDict[str, typing.Any]):\n')

        # NOTE if the schema map above is updated, this block should be too
        f.write(_make_dict_methods("typing.Literal['dictionary']", "Utf8Str"))
        f.write(_make_dict_methods("typing.Literal['sync_lpr']", "Bool"))
        f.write(
            _make_dict_methods("typing.Literal['dict.prefs.v2']", "DynamicMap"))
        f.write(
            _make_dict_methods("typing.Literal['EndActions']", "DynamicMap"))
        f.write(
            _make_dict_methods("typing.Literal['ReaderMetrics']", "DynamicMap"))
        f.write(
            _make_dict_methods("typing.Literal['StartActions']", "DynamicMap"))
        f.write(_make_dict_methods("typing.Literal['Translator']", "Utf8Str"))
        f.write(_make_dict_methods("typing.Literal['Wikipedia']", "Utf8Str"))
        f.write(
            _make_dict_methods(
                "typing.Literal['buy.asin.response.data']", "Json"))
        f.write(
            _make_dict_methods(
                "typing.Literal['next.in.series.info.data']", "Json"))
        f.write(_make_dict_methods("typing.Literal['price.info.data']", "Json"))
        f.write(_make_dict_methods("typing.Literal['erl']", "Position"))
        f.write(_make_dict_methods("typing.Literal['lpr']", "LastPageRead"))
        f.write(_make_dict_methods("typing.Literal['fpr']", "PageReadPos"))
        f.write(
            _make_dict_methods("typing.Literal['updated_lpr']", "PageReadPos"))
        f.write(_make_dict_methods("typing.Literal['apnx.key']", "APNXKey"))
        f.write(
            _make_dict_methods(
                "typing.Literal['fixed.layout.data']", "FixedLayoutData"))
        f.write(
            _make_dict_methods(
                "typing.Literal['sharing.limits']", "SharingLimits"))
        f.write(
            _make_dict_methods(
                "typing.Literal['language.store']", "LanguageStore"))
        f.write(
            _make_dict_methods(
                "typing.Literal['periodicals.view.state']",
                "PeriodicalsViewState"))
        f.write(
            _make_dict_methods(
                "typing.Literal['purchase.state.data']", "PurchaseStateData"))
        f.write(
            _make_dict_methods("typing.Literal['timer.model']", "TimerModel"))
        f.write(
            _make_dict_methods(
                "typing.Literal['timer.data.store']", "TimerDataStore"))
        f.write(
            _make_dict_methods(
                "typing.Literal['timer.data.store.v2']", "TimerDataStoreV2"))
        f.write(
            _make_dict_methods(
                "typing.Literal['book.info.store']", "BookInfoStore"))
        f.write(
            _make_dict_methods(
                "typing.Literal['page.history.store']",
                "Array[PageHistoryStoreElement]"))
        f.write(
            _make_dict_methods(
                "typing.Literal['reader.state.preferences']",
                "ReaderStatePreferences"))
        f.write(_make_dict_methods("typing.Literal['font.prefs']", "FontPrefs"))
        f.write(
            _make_dict_methods(
                "typing.Literal['annotation.cache.object']",
                "AnnotationCacheObject"))
        f.write(
            _make_dict_methods(
                "typing.Literal['annotation.personal.bookmark']",
                "AnnotationPersonalElement"))
        f.write(
            _make_dict_methods(
                "typing.Literal['annotation.personal.highlight']",
                "AnnotationPersonalElement"))
        f.write(
            _make_dict_methods(
                "typing.Literal['annotation.personal.note']",
                "AnnotationPersonalElement"))
        f.write(
            _make_dict_methods(
                "typing.Literal['annotation.personal.clip_article']",
                "AnnotationPersonalElement"))
        f.write(
            _make_dict_methods(
                "typing.Literal['whisperstore.migration.status']",
                "WhisperstoreMigrationStatus"))
        f.write(
            _make_dict_methods(
                "typing.Literal['timer.average.distribution.normal']",
                "TimerAverageCalculatorDistributionNormal"))
        f.write(
            _make_dict_methods(
                "typing.Literal['timer.average.calculator.outliers']",
                "TimerAverageCalculatorOutliers"))

        f.write(_make_dict_methods("typing.Any", "typing.Any"))
        f.write(_make_dict_methods('typing.Any', 'typing.Any', False))

        f.write("# @formatter: on\n")
        f.write("# NOLINTEND\n")

    return 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv[1:]))
