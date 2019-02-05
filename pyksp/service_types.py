from . import base_types as bt
from . import abstract as ab
import typing as ty
import functools as ft
import inspect as it
import re


class LocMeta(ab.KSPBaseMeta):
    calls: int = 0

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        LocMeta.calls += 1
        if isinstance(arg, tuple):
            if issubclass(arg[0], int):
                return type('LocArrInt' + str(LocMeta.calls), (LocArrInt, ),
                            {'size': arg[1]})
            if issubclass(arg[0], str):
                return type('LocArrStr' + str(LocMeta.calls), (LocArrStr, ),
                            {'size': arg[1]})
            if issubclass(arg[0], float):
                return type('LocArrFloat' + str(LocMeta.calls),
                            (LocArrFloat, ), {'size': arg[1]})
        arg = ty.cast(type, arg)
        if issubclass(arg, int):
            return LocInt
        if issubclass(arg, str):
            return LocStr
        if issubclass(arg, float):
            return LocFloat
        raise TypeError('can not infer type of Local')


class Loc(metaclass=LocMeta):
    pass


# CPD-OFF
if ty.TYPE_CHECKING:

    class LocArrInt(bt.ArrInt):
        pass

    class LocArrStr(bt.ArrStr):
        pass

    class LocArrFloat(bt.ArrFloat):
        pass

    class LocInt(bt.VarInt):
        pass

    class LocStr(bt.VarStr):
        pass

    class LocFloat(bt.VarFloat):
        pass

    # CPD-ON
else:

    class LocArrInt(Loc, bt.ArrInt):
        pass

    class LocArrStr(Loc, bt.ArrStr):
        pass

    class LocArrFloat(Loc, bt.ArrFloat):
        pass

    class LocInt(Loc, bt.VarInt):
        pass

    class LocStr(Loc, bt.VarStr):
        pass

    class LocFloat(Loc, bt.VarFloat):
        pass


F = ty.TypeVar('F', bound=ty.Callable[..., None])


def vrs(f: F) -> F:
    name = f.__qualname__
    name = re.sub(r'\.', '_', name)
    ab.NameVar.scope(name)
    sig = it.signature(f)
    new_kwargs: ty.Dict[str, Loc] = dict()
    for par in sig.parameters:
        anno = sig.parameters[par].annotation
        # print(par, anno)
        if issubclass(anno, Loc):
            # print('instance')
            a_kwgs = dict(name=par)
            if hasattr(anno, 'size'):
                a_kwgs['size'] = anno.size
            try:
                new_kwargs[par] = anno(**a_kwgs)
            except NameError:
                new_kwargs[par] = anno(**a_kwgs, local=True)
    ab.NameVar.scope()

    @ft.wraps(f)
    def wrapper(*args: ty.Any, **kwargs: ty.Any) -> None:
        b_args = sig.bind(*args, **kwargs, **new_kwargs)
        return f(*b_args.args, **b_args.kwargs)

    return wrapper  # type: ignore
