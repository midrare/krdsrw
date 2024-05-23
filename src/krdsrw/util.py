import typing


def flatten(o: typing.Any, skip_null: bool = True) -> list[typing.Any]:
    def recurse(oo: typing.Any, master: list[typing.Any]):
        if isinstance(oo, (tuple, list)):
            for e in oo:
                recurse(e, master)
            return
        if skip_null and oo is None:
            return
        master.append(oo)

    result = []
    recurse(o, result)
    return result


def explode(
    o: typing.Any | list[typing.Any], size: int = 0
) -> list[typing.Any]:
    result = []
    if isinstance(o, (tuple, list)):
        result.extend(o)
    else:
        result.append(o)
    result += [None for _ in range(size - len(result))]
    return result
