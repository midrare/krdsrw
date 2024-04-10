import abc
import argparse
import collections
import dataclasses
import inspect
import pathlib
import os
import re
import sys
import typing

from .basics import Basic
from .basics import Byte
from .basics import Char
from .basics import Bool
from .basics import Short
from .basics import Int
from .basics import Long
from .basics import Float
from .basics import Double
from .basics import Utf8Str
from .objects import DynamicMap
from .objects import Json
from .objects import IntMap
from .objects import ObjectMap
from .objects import Position
from .objects import LPR


@dataclasses.dataclass
class Function:
    name: str
    args: dict[
        str,
        None
        | type
        | typing.Literal["*"]
        | typing.Any
        | tuple[None | type | typing.Literal["*"] | typing.Any, ...]
        | list[None | type | typing.Literal["*"] | typing.Any],
    ] = dataclasses.field(default_factory=dict)
    ret: (
        None
        | type
        | typing.Literal["*"]
        | typing.Any
        | tuple[None | type | typing.Literal["*"] | typing.Any, ...]
        | list[None | type | typing.Literal["*"] | typing.Any]
    ) = dataclasses.field(default_factory=list)
    decorators: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ContainerAPI:
    pass


def _path_arg(
    exists: bool | None,
    type: str | None,
    alt: (
        None
        | typing.Literal["file", "dir"]
        | list[typing.Literal["file", "dir"]]
    ) = None,
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
                f'Path "{arg}" exists and is not a file.'
            )

        if type == "dir" and os.path.exists(arg) and not os.path.isdir(arg):
            raise argparse.ArgumentTypeError(
                f'Path "{arg}" exists and is not a directory.'
            )

        return arg

    return check


def _indent(code: str, indent: int) -> str:
    smallest = None
    for line in code.splitlines():
        m = re.match(r"^(\\h*)", line)
        if m and (smallest is None or len(m.group(1)) < len(smallest)):
            smallest = m.group(1)

    smallest = smallest or ""
    pre = " " * indent
    return f"\n".join(pre + s[len(smallest) :] for s in code.splitlines())


def _to_type(type_: type | typing.Literal["*"] | typing.Any) -> str:
    if type_ == "*":
        return "typing.Any"
    if inspect.isclass(type_):
        return type_.__name__
    if type_ is None:
        return "None"
    if isinstance(type_, str):
        return f"typing.Literal['{type_}']"
    if isinstance(type_, (bool, int, float, bytes)):
        return f"typing.Literal[{type_}]"

    return str(type_)


def _generate_function(sig: Function) -> str:
    result = []

    result.extend(sig.decorators)
    result.append(f"def {sig.name}(")

    for i, (key, values) in enumerate(sig.args.items()):
        if key in ["self", "cls"] and i <= 0:
            result.append(f"    {key}, \\")
            continue

        assert isinstance(values, (tuple, list))
        values_ = [_to_type(e) for e in values]
        result.append(f"    {key}{': \\' if values_ else ','}")
        for i, value in enumerate(values_):
            pipe = "| " if i > 0 else ""
            cont = " \\" if i < len(values_) - 1 else ","
            result.append(f"    {pipe}{value}{cont}")

    arrow = "-> " if sig.ret and sig.ret != [None] else ""
    result.append(f") {arrow}\\")
    if sig.ret and sig.ret != [None]:
        for i, ret in enumerate(sig.ret):
            pipe = "| " if i > 0 else ""
            result.append(f"    {pipe}{_to_type(ret)} \\")

    result.append(":")
    result.append("    ...\n")
    return "\n".join(result) + ("\n" if result else "")


def _flatten(o: typing.Any) -> list[typing.Any]:
    def recurse(o: typing.Any, master: list[typing.Any]):
        if isinstance(o, (tuple, list)):
            for e in o:
                recurse(e, master)
            return
        master.append(o)

    result = []
    recurse(o, result)
    return result


def _generate_map(cls_: type | str, fields: list[Index]) -> str:
    sigs = []
    for field in fields:
        if field.is_readable:
            sigs.append(
                Function(
                    "__getitem__",
                    {
                        "self": True,
                        "key": field.key,
                    },
                    field.value,
                )
            )
            sigs.append(
                Function(
                    "__contains__",
                    {
                        "self": True,
                        "key": field.key,
                    },
                    [bool],
                )
            )
            sigs.append(
                Function(
                    "get",
                    {
                        "self": True,
                        "key": field.key,
                        "default": [None, "*"],
                    },
                    field.value,
                )
            )

        if field.is_writable:
            sigs.append(
                Function(
                    "__setitem__",
                    {
                        "self": True,
                        "key": field.key,
                        "value": field.value,
                    },
                    [None],
                )
            )
            sigs.append(
                Function(
                    "setdefault",
                    {
                        "self": True,
                        "key": field.key,
                        "default": [None] + _flatten(field.value),
                    },
                    [None] + _flatten(field.value),
                )
            )

        if field.is_deletable:
            sigs.append(
                Function(
                    "__delitem__",
                    {
                        "self": True,
                        "key": field.key,
                    },
                    [None],
                )
            )
            sigs.append(
                Function(
                    "pop",
                    {
                        "self": True,
                        "key": field.key,
                        "default": [None] + _flatten(field.value),
                    },
                    [None] + _flatten(field.value),
                )
            )

    fn_to_sigs = collections.defaultdict(list)
    for sig in sigs:
        fn_to_sigs[sig.name].append(sig)

    for sigs in fn_to_sigs.values():
        if len(sigs) >= 2:
            for sig in sigs:
                sig.decorators.append("@typing.overload")

    code = f"class {cls_.__name__ if inspect.isclass(cls_) else cls_}:"
    for sigs in fn_to_sigs.values():
        for sig in sigs:
            code += "\n"
            code += _indent(_generate_function(sig), 4)

    return code


def _get_imports(fields: list[Index]) -> set[type]:
    result = set()

    for field in fields:
        for e in _flatten(field.key) + _flatten(field.value):
            if e is None:
                continue
            if inspect.isclass(e):
                result.add(e)

    return result


def _generate_imports(fields: list[Index]) -> str:
    result = []

    for im in _get_imports(fields):
        absname = ".".join([im.__module__, im.__qualname__])
        modname = re.sub(r"(^src\.|\.[^\.]+$)", "", absname)
        tail = re.sub(r"^.+\.", "", absname)
        # m = re.match(r'([^\\.\\s]+)\\s*$', im)
        # assert m is not None
        result.append(f"from {modname} import {tail}")

    return "\n".join(result) + "\n" if result else ""


def _main(argv: list[str]) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="generate container type hints"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="path to output file",
        type=_path_arg(exists=None, type="file"),
        required=True,
    )

    args = parser.parse_args(argv)
    with open(args.output, "w") as f:
        f.write("# THIS FILE IS AUTOMATICALLY GENERATED. DO NOT\n")
        f.write("# MODIFY THIS FILE. ALL CHANGES WILL BE UNDONE.\n")
        f.write("\n")
        f.write("# NOLINTBEGIN\n")
        f.write("# @formatter:off\n")
        f.write("# autopep8: off\n")
        f.write("# yapf: disable\n")
        f.write("import typing\n")
        f.write("\n")
        f.write("from .basics import *  # type: ignore  # pyright: ignore\n")
        f.write("from .objects import *  # type: ignore  # pyright: ignore\n")
        f.write("\n")

        fields = [
            Index("dictionary", Utf8Str),
            Index("sync_lpr", Bool),
            Index("dict.prefs.v2", DynamicMap),
            Index("EndActions", DynamicMap),
            Index("ReaderMetrics", DynamicMap),
            Index("StartActions", DynamicMap),
            Index("Translator", Utf8Str),
            Index("Wikipedia", Utf8Str),
            Index("buy.asin.response.data", Json),
            Index("next.in.series.info.data", Json),
            Index("price.info.data", Json),
            Index("erl", Position),
            Index("lpr", LPR),
            Index("fpr", PageReadPos),
            Index("updated_lpr", PageReadPos),
            # Field('apnx.key', APNXKey),
            # Field('fixed.layout.data', FixedLayoutData),
            # Field('sharing.limits', SharingLimits),
            # Field('language.store', LanguageStore),
            # Field('periodicals.view.state', PeriodicalsViewState),
            # Field('purchase.state.data', PurchaseStateData),
            # Field('timer.model', TimerModel),
            # Field('timer.data.store', TimerDataStore),
            # Field('timer.data.store.v2', TimerDataStoreV2),
            # Field('book.info.store', BookInfoStore),
            # Field('page.history.store', Array[PageHistoryStoreElement]),
            # Field('reader.state.preferences', ReaderStatePreferences),
            # Field('font.prefs', FontPrefs),
            # Field('annotation.cache.object', AnnotationCacheObject),
            # Field('annotation.personal.bookmark', AnnotationPersonalElement,),
            # Field('annotation.personal.highlight', AnnotationPersonalElement,),
            # Field('annotation.personal.note', AnnotationPersonalElement,),
            # Field('annotation.personal.clip_article', AnnotationPersonalElement,),
            # Field('whisperstore.migration.status', WhisperstoreMigrationStatus,),
            # Field('timer.average.distribution.normal', TimerAverageCalculatorDistributionNormal,),
            # Field('timer.average.calculator.outliers', TimerAverageCalculatorOutliers,),
        ]

        f.write(_generate_imports(fields))
        f.write("\n\n")
        f.write(_generate_map(ObjectMap, fields))
        f.write("\n")

        f.write("# autopep8: on\n")
        f.write("# yapf: enable\n")
        f.write("# @formatter: on\n")
        f.write("# NOLINTEND\n")

    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
