import typing as ty
import functools as ft
import inspect as it
import re
from . import base_types as bt
from . import abstract as ab


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


T = ty.TypeVar('T')
F = ty.TypeVar('F', bound=ty.Callable[..., ty.Any])


def vrs(f: F) -> F:
    if not ty.TYPE_CHECKING:  # pylint: disable=R1705
        name = f'{f.__module__}_{f.__qualname__}'
        name = re.sub(r'\.', '_', name)
        sig = it.signature(f)
        new_kwargs: ty.Dict[str, Loc] = dict()

        @ft.wraps(f)
        def wrapper(*args: ty.Any, **kwargs: ty.Any) -> T:
            ab.NameVar.scope(name)
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
            b_args = sig.bind(*args, **kwargs, **new_kwargs)
            ab.NameVar.scope()
            return f(*b_args.args, **b_args.kwargs)

        return wrapper
    else:
        return f


class OutMeta(ab.KSPBaseMeta):
    calls: int = 0

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        OutMeta.calls += 1
        if isinstance(arg, tuple):
            if issubclass(arg[0], int):
                return type('OutArrInt' + str(OutMeta.calls), (OutArrInt, ),
                            {'size': arg[1]})
            if issubclass(arg[0], str):
                return type('OutArrStr' + str(OutMeta.calls), (OutArrStr, ),
                            {'size': arg[1]})
            if issubclass(arg[0], float):
                return type('OutArrFloat' + str(OutMeta.calls),
                            (OutArrFloat, ), {'size': arg[1]})
        arg = ty.cast(type, arg)
        if issubclass(arg, int):
            return OutInt
        if issubclass(arg, str):
            return OutStr
        if issubclass(arg, float):
            return OutFloat
        raise TypeError('can not infer type of Outal')


class Out(metaclass=OutMeta):
    pass


# CPD-OFF
if ty.TYPE_CHECKING:

    class OutArrInt(bt.ArrInt):
        pass

    class OutArrStr(bt.ArrStr):
        pass

    class OutArrFloat(bt.ArrFloat):
        pass

    class OutInt(bt.VarInt):
        pass

    class OutStr(bt.VarStr):
        pass

    class OutFloat(bt.VarFloat):
        pass

    # CPD-ON
else:

    class OutArrInt(Out, bt.ArrInt):
        pass

    class OutArrStr(Out, bt.ArrStr):
        pass

    class OutArrFloat(Out, bt.ArrFloat):
        pass

    class OutInt(Out, bt.VarInt):
        pass

    class OutStr(Out, bt.VarStr):
        pass

    class OutFloat(Out, bt.VarFloat):
        pass


class InMeta(ab.KSPBaseMeta):
    calls: int = 0

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        InMeta.calls += 1
        if isinstance(arg, tuple):
            if issubclass(arg[0], int):
                return type('InArrInt' + str(InMeta.calls), (InArrInt, ),
                            {'size': arg[1]})
            if issubclass(arg[0], str):
                return type('InArrStr' + str(InMeta.calls), (InArrStr, ),
                            {'size': arg[1]})
            if issubclass(arg[0], float):
                return type('InArrFloat' + str(InMeta.calls), (InArrFloat, ),
                            {'size': arg[1]})
        arg = ty.cast(type, arg)
        if issubclass(arg, int):
            return InInt
        if issubclass(arg, str):
            return InStr
        if issubclass(arg, float):
            return InFloat
        raise TypeError('can not infer type of In arg')


class In(metaclass=InMeta):
    pass


# CPD-OFF
if ty.TYPE_CHECKING:

    class InArrInt(bt.ArrInt):
        pass

    class InArrStr(bt.ArrStr):
        pass

    class InArrFloat(bt.ArrFloat):
        pass

    class InInt(bt.VarInt):
        pass

    class InStr(bt.VarStr):
        pass

    class InFloat(bt.VarFloat):
        pass

    # CPD-ON
else:

    class InArrInt(In, bt.ArrInt):
        pass

    class InArrStr(In, bt.ArrStr):
        pass

    class InArrFloat(In, bt.ArrFloat):
        pass

    class InInt(In, bt.VarInt):
        pass

    class InStr(In, bt.VarStr):
        pass

    class InFloat(In, bt.VarFloat):
        pass
