from . import base_types as bt
from . import abstract as ab
import typing as ty


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
        if issubclass(arg, int):
            return LocInt
        if issubclass(arg, str):
            return LocStr
        if issubclass(arg, float):
            return LocFloat
        raise TypeError('can not infer type of Local')


class Loc(metaclass=LocMeta):
    pass


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
