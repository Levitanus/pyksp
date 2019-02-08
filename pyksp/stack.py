import typing as ty

from . import abstract as ab
from . import base_types as bt
from . import control_statements as cs
from . import service_types as st


class FrameVar(ab.KSP, ty.Generic[bt.KVT, bt.VHT, bt.KT, bt.KVAT]):
    var: bt.KVAT
    array: bt.ArrBase[bt.KVT, bt.VHT, bt.KT]
    size: int

    def __init__(self,
                 array: bt.ArrBase[bt.KVT, bt.VHT, bt.KT],
                 var: bt.KVAT,
                 size: int = 1) -> None:
        self.var = var
        self.array = array
        self.size = size
        self.ref = var._ref_type

    def push(self, idx: bt.NTU[int]) -> bt.KVAT:
        if self.size == 1:
            self.array[idx] <<= self.var  # type: ignore
            return self.array[idx]  # type: ignore
        for i in cs.For(self.size):
            self.array[idx + i] <<= self.var[i]  # type: ignore
        return st.SubArray(  # type: ignore
            self.array, idx, idx + self.size - 1)


class StackArray(ty.Generic[bt.KAT]):
    array: bt.KAT
    ptr: bt.ArrInt
    idx: bt.VarInt
    _ref: ty.Type[bt.KAT]
    _size: int
    _depth: int
    _name: str

    def __init__(self,
                 name: str,
                 ref: ty.Type[bt.KAT],
                 size: int = 32768,
                 depth: int = 100) -> None:
        # self.array = ref(name=f'_{name}_arr_', size=size)  # type: ignore
        # self.ptr = bt.ArrInt(name=f'_{name}_ptr_', size=depth)
        # self.idx = bt.VarInt(-1, name=f'_{name}_idx_')
        self._ref = ref
        self._size = size
        self._depth = depth
        self._name = name

    def _check_init(self) -> None:
        try:
            self.array = self._ref(  # type: ignore
                name=f'_{self._name}_arr_', size=self._size)
            self.ptr = bt.ArrInt(name=f'_{self._name}_ptr_', size=self._depth)
            self.idx = bt.VarInt(-1, name=f'_{self._name}_idx_')
        except NameError:
            return

    def push(self, size: int) -> None:
        self._check_init()
        self.idx.inc()
        self.ptr[self.idx + 1] <<= self.ptr[self.idx] + size

    def pop(self) -> None:
        self.idx.dec()


class StackFrame:
    def __init__(self, *vars_: FrameVar) -> None:
        self.vars = vars_
        self.size = 0
        for var in vars_:
            self.size += var.size


class Stack:
    arrays: ty.Dict[ty.Type[ty.Union[int, str, float]], StackArray]
    frames: ty.List[StackFrame]

    def __init__(self, name: str) -> None:
        self.arrays = dict()
        for t in (int, str, float):
            self.arrays[t] = StackArray(f'{name}_{t}', bt.Arr[t])
        self.frames = list()

    # def push(self, **vars_:bt.KVAT) -> ty.List[bt.KVAT]:
    #     f_vars: ty.List[FrameVar] = list()
    #     for var in vars_.values():
    #         if isinstance(var, st.LocMeta)
    #     frame = StackFrame(vars_)
    #     self.frames.append(frame)
    #     if frame.int_vars:
    #         int_vars =
