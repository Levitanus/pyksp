import typing as ty
import functools as ft
import inspect as it
import re
from . import base_types as bt
from . import abstract as ab

# CPD-OFF


class LocMeta(ab.KSPBaseMeta):
    calls: int = ...

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        ...


class Loc(metaclass=LocMeta):
    pass


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

T = ty.TypeVar('T')
F = ty.TypeVar('F', bound=ty.Callable[..., ty.Any])


def vrs(f: F) -> F:
    ...


class OutMeta(ab.KSPBaseMeta):
    calls: int = 0

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        ...


class Out(metaclass=OutMeta):
    pass


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


class InMeta(ab.KSPBaseMeta):
    calls: int = 0

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        ...


class In(metaclass=InMeta):
    pass


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


class SubArray(bt.ArrBase[bt.KVT, bt.KLT, bt.KT]):
    array: bt.ArrBase[bt.KVT, bt.KLT, bt.KT]
    _start_idx: int
    _stop_idx: int

    def __init__(self, array: bt.ArrBase[bt.KVT, bt.KLT, bt.KT],
                 start_idx: int, stop_idx: int) -> None:
        ...

    def name(self) -> ty.NoReturn:  # type: ignore
        ...

    @property
    def val(self) -> bt.KLT:
        ...

    @val.setter
    def val(self, val: bt.KLT) -> None:
        ...

    def __getitem__(self, idx: bt.NTU[int]) -> bt.KVT:
        ...

    def __setitem__(self, idx: bt.NTU[int], val: bt.KVT) -> None:
        ...

    def set_val_at_idx(self, idx: int, val: bt.KT) -> None:
        ...
