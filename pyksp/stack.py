import typing as ty

from . import abstract as ab
from . import base_types as bt
from . import control_statements as cs
from . import service_types as st


class FrameVar(ab.KSP, ty.Generic[bt.KVT, bt.VHT, bt.KT, bt.KVAT]):
    var: bt.KVAT
    array: bt.ArrBase[bt.KVT, bt.VHT, bt.KT]
    size: int

    def __init__(self, array: bt.ArrBase[bt.KVT, bt.VHT, bt.KT], var: bt.KVAT,
                 size: int) -> None:
        self.var = var
        self.array = array
        self.size = size

    def push(self, idx: bt.NTU[int]) -> ty.Tuple[bt.KVAT, bt.NTU[int]]:
        if self.size == 1:
            self.array[idx] <<= self.var  # type: ignore
            return self.array[idx], idx + 1  # type: ignore
        for i in cs.For(self.size):
            self.array[idx + i] <<= self.var[i]  # type: ignore
        return st.SubArray(  # type: ignore
            self.array, idx, idx + self.size - 1), idx + self.size


# class StackFrame(ab.KSP, ty.Generic[bt.KVT, bt.VHT, bt.KT, bt.KVAT]):
#     def __init__(self, array: bt.ArrBase[bt.KVT, bt.VHT, bt.KT],
#                  ptr: bt.VarInt, **vars: bt.KVAT) -> None:
#         self.array = array
#         self.ptr =
