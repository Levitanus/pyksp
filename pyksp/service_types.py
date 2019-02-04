from . import base_types as bt
import typing as ty


class LocMeta(type):
    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        ...


class Loc(metaclass=LocMeta):
    ...


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
