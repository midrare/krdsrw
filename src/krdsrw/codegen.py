import argparse
import collections
import copy
import dataclasses
import inspect
import os
import re
import sys
import typing

from .objects import Field
from .objects import Store
from .objects import _store_key_to_field


_VOID: object = object()


class _Name(str):
    pass


@dataclasses.dataclass
class _Function:
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
class _Class:
    name: str
    parents: list[typing.Self | type] = dataclasses.field(
        default_factory=list
    )
    methods: list[_Function] = dataclasses.field(default_factory=list)


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


def _indent_code(code: str, indent: int) -> str:
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
        return _Name("typing.Any")
    if inspect.isclass(type_):
        return type_.__name__
    if type_ is None:
        return "None"
    if isinstance(type_, _Name):
        return type_
    if isinstance(type_, str):
        return f"typing.Literal['{type_}']"
    if isinstance(type_, (bool, int, float, bytes)):
        return f"typing.Literal[{type_}]"

    return str(type_)


def _generate_function_code(func: _Function) -> str:
    result = []

    result.extend(func.decorators)
    result.append(f"def {func.name}(")

    for i, (key_name, key_values) in enumerate(func.args.items()):
        if not isinstance(key_values, (tuple, list)):
            key_values = [key_values]

        assert isinstance(key_values, (tuple, list))
        key_values = list(key_values)
        if None in key_values:
            key_values.remove(None)
            key_values.append(None)

        line = f"    {key_name}"
        values_ = [_to_type(e) for e in key_values if e is not _VOID]
        is_first = True
        for i2, value in enumerate(values_):
            pipe = ": " if is_first else " | "
            line += f"{pipe}{value}"
            is_first = False

        line += ","
        result.append(line)

    if not func.ret or func.ret == [None]:
        result.append("):")
    else:
        line = f") ->"

        ret_types = copy.copy(func.ret)
        if not isinstance(ret_types, (tuple, list)):
            ret_types = [ret_types]

        if None in ret_types:
            ret_types.remove(None)
            ret_types.append(None)
        ret_types = _flatten(ret_types)

        is_first = True
        for i, ret in enumerate(ret_types):
            if ret is _VOID:
                continue

            line += " | " if not is_first else " "
            line += _to_type(ret)
            is_first = False

        line += ":"
        result.append(line)

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


def _generate_class_code(cls_: _Class, indent: int = 4) -> str:
    parents = cls_.parents or []
    if not isinstance(parents, list):
        parents = [parents]

    fn_to_sigs = collections.defaultdict(list)
    for sig in cls_.methods:
        fn_to_sigs[sig.name].append(sig)

    for sigs in fn_to_sigs.values():
        if len(sigs) >= 2:
            for sig in sigs:
                sig.decorators.append("@typing.overload")

            base_fn = copy.deepcopy(sigs[0])
            base_fn.args.clear()
            base_fn.args.update(
                {
                    "self": _VOID,
                    "*args": _VOID,
                    "**kwargs": _VOID,
                }
            )
            base_fn.ret.clear()
            base_fn.ret.append(["*"])
            base_fn.decorators.clear()

            sigs.append(base_fn)

    parents_ = ""
    if parents:
        parents_ = f"({', '.join(t.__name__ for t in parents)})"

    code = f"class {cls_.name}{parents_}:"
    for sigs in fn_to_sigs.values():
        for sig in sigs:
            code += "\n"
            code += _indent_code(_generate_function_code(sig), indent)

    return code


def _generate_cls_name_from_key_path(key_path: list[str]) -> None | _Name:
    split = []

    for e in key_path or []:
        split.extend(re.split(r"[_\\.]+|(?<=[a-z])(?=[A-Z])", e))

    caps = (s.lower().capitalize() for s in split)
    if not caps:
        return None

    return _Name("_" + "".join(caps))


def _generate_cls_name(
    field: Field,
    path: None | list[str] = None,
) -> type | _Name:
    if field.proto.name:
        return _Name(field.proto.name)

    if (
        not issubclass(field.proto.cls_, (bool, int, float, str, bytes))
        and field.proto.schema
    ):
        return _Name(_generate_cls_name_from_key_path(path))

    return field.proto.cls_


def _generate_array_methods(
    index: Field,
    path: list[str],
) -> list[_Function]:
    value = _generate_cls_name(index, path)

    # noinspection PyListCreation
    result = []

    # result.append(
    #     _Function(
    #         "__getitem__",
    #         {"self": _VOID, "key": [key]},
    #         [value],
    #     )
    # )
    #
    # result.append(
    #     _Function(
    #         "__contains__",
    #         {"self": _VOID, "o": [key]},
    #         [bool],
    #     )
    # )

    result.append(
        _Function(
            "__setitem__",
            {
                "self": _VOID,
                "i": [typing.SupportsIndex],
                "o": [int, float, str, value],
            },
            [None],
        )
    )

    result.append(
        _Function(
            "__setitem__",
            {
                "self": _VOID,
                "i": [slice],
                "o": [
                    _Name(f"typing.Iterable[int| float| str| {str(value)}]")
                ],
            },
            [None],
        )
    )

    result.append(
        _Function(
            "__add__",
            {
                "self": _VOID,
                "other": [
                    _Name(f"typing.Sequence[int | float | str | value]")
                ],
            },
            ["self"],
        )
    )

    return result


def _generate_map_methods(
    field: Field,
    path: list[str],
) -> list[_Function]:
    if field is NotImplemented:
        return []

    key = path[-1]
    value = _generate_cls_name(field, path)

    # noinspection PyListCreation
    result = []

    result.append(
        _Function(
            "__getitem__",
            {"self": _VOID, "key": [key]},
            [value],
        )
    )
    result.append(
        _Function(
            "__contains__",
            {"self": _VOID, "key": [key]},
            [bool],
        )
    )
    result.append(
        _Function(
            "get",
            {"self": _VOID, "key": [key], "default": [None, "*"]},
            [value],
        )
    )

    result.append(
        _Function(
            "__setitem__",
            {"self": _VOID, "key": [key], "value": [value]},
            [None],
        )
    )
    result.append(
        _Function(
            "setdefault",
            {
                "self": _VOID,
                "key": [key],
                "default": [None, value],
            },
            [None, value],
        )
    )

    if not field.required:
        result.append(
            _Function(
                "__delitem__",
                {"self": _VOID, "key": [key]},
                [None],
            )
        )
        result.append(
            _Function(
                "pop",
                {
                    "self": _VOID,
                    "key": [key],
                    "default": [None, "*"],
                },
                [None, value],
            )
        )

    return result


def _generate_array_class(
    index: Field,
    name: None | str = None,
    path: None | list[str] = None,
) -> _Class:
    if not name:
        name = _generate_cls_name_from_key_path(path)
    assert name, "could not determine class name"
    result = _Class(name)
    result.methods.extend(_generate_array_methods(index, path))
    return result


def _generate_map_class(
    fields: dict[str, Field],
    name: None | str = None,
    path: None | list[str] = None,
) -> _Class:
    if not name:
        name = _generate_cls_name_from_key_path(path)
    assert name, "could not determine class name"
    result = _Class(name)

    for key, field in fields.items():
        kp = (path or []) + [key]
        result.methods.extend(_generate_map_methods(field, kp))

    return result


def _generate_map_classes(
    fields: dict[str, Field],
    name: None | str = None,
    _path: None | list[str] = None,
) -> list[_Class]:
    if not name:
        name = _generate_cls_name_from_key_path(_path)

    assert name, "could not determine class name"
    result = [_generate_map_class(_store_key_to_field, name)]

    for key, field in fields.items():
        kp = (_path or []) + [key]

        if issubclass(field.proto.cls_, dict) and field.proto.schema:
            result.append(
                _generate_map_class(
                    field.proto.schema, name=field.proto.name, path=kp
                )
            )
        elif issubclass(field.proto.cls_, list):
            result.append(
                _generate_array_class(
                    field.proto.schema, name=field.proto.name, path=kp
                )
            )

    return result


def _get_imports(fields: list[Field]) -> set[type]:
    result = set()

    for field in fields:
        if field.proto.cls_ is None:
            continue
        if inspect.isclass(field.proto.cls_):
            result.add(field.proto.cls_)

    return result


def _generate_imports(fields: list[Field]) -> str:
    result = []

    for im in _get_imports(fields):
        absname = ".".join([im.__module__, im.__qualname__])
        modname = re.sub(r"(^src\.|\.[^\\.]+$)", "", absname)
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
        f.write("# autopep8: off\n")
        f.write("# @formatter: off\n")
        f.write("# fmt: off\n")
        f.write("# yapf: disable\n")
        f.write("\n")
        f.write("from __future__ import annotations\n")
        f.write("import typing\n")
        f.write("\n")
        f.write("from .basics import *  # type: ignore  # pyright: ignore\n")
        f.write("from .objects import *  # type: ignore  # pyright: ignore\n")
        f.write("\n\n")

        clss = _generate_map_classes(_store_key_to_field, "Store2")
        for cls_ in clss:
            code = _generate_class_code(cls_)
            f.write(code)
            f.write("\n\n")

        f.write("\n\n")
        f.write("# yapf: enable\n")
        f.write("# fmt: on\n")
        f.write("# @formatter: on\n")
        f.write("# autopep8: on\n")
        f.write("# NOLINTEND\n")

    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
