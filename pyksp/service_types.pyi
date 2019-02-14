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
    """Spetial class can be used as callable argument annotation.

    when used in function or method decorated with vrs,
        new KSP variable will be created and passed to the
        every function call.
    when used in function or method decorated with func,
        stack area will be allocated and returned as KSP var
    Loc[type] produces variables
    Loc[type, size: int] produces array of specified size
    """


# CPD-OFF
class LocArrInt(bt.ArrInt):
    _ref_type = int


class LocArrStr(bt.ArrStr):
    _ref_type = str


class LocArrFloat(bt.ArrFloat):
    _ref_type = float


class LocInt(bt.VarInt):
    _ref_type = int


class LocStr(bt.VarStr):
    _ref_type = str


class LocFloat(bt.VarFloat):
    _ref_type = float


# CPD-ON

T = ty.TypeVar('T')
F = ty.TypeVar('F', bound=ty.Callable[..., ty.Any])


def vrs(f: F) -> F:
    ...


class OutMeta(ab.KSPBaseMeta):
    calls: int = ...

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        ...


class Out(metaclass=OutMeta):
    """Spetial class can be used as func argument annotation.

    can be used only in function or method decorated with func,
        stack area will be allocated and returned as KSP var,
        then returned to variable, passed as argument.
        If no var passed, no error is raised.
    Out[type] produces variables
    Out[type, size: int] produces array of specified size
    """


# CPD-OFF
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
class InMeta(ab.KSPBaseMeta):
    calls: int = ...

    def __getitem__(cls, arg: ty.Union[type, ty.Tuple[type, int]]) -> type:
        ...


class In(metaclass=InMeta):
    """Spetial class can be used as func argument annotation.

    can be used only in function or method decorated with func,
        arg will recieve the KSP var of specified type
        stack area will be allocated and could be used as KKSP variable
    In[type] produces variables
    In[type, size: int] produces array of specified size
    """


# CPD-OFF
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
    _start_idx: bt.ProcessInt
    _stop_idx: bt.ProcessInt
    _ref_type: ty.Type[bt.KT]
    _size: int

    def __init__(
        self, array: bt.ArrBase[bt.KVT, bt.KLT, bt.KT],
        start_idx: bt.ProcessInt, stop_idx: bt.ProcessInt
    ) -> None:
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

    def __len__(self) -> int:
        ...
