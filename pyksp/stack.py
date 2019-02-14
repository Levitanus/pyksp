import typing as ty

from . import abstract as ab
from . import base_types as bt
from . import control_statements as cs
from . import service_types as st


class StackArray(ty.Generic[bt.KAT]):
    array: bt.KAT
    ptr: bt.ArrInt
    idx: bt.VarInt
    _ref: ty.Type[bt.KAT]
    _size: int
    _depth: int
    _name: str

    def __init__(
        self,
        name: str,
        ref: ty.Type[bt.KAT],
        size: int = 32768,
        depth: int = 100
    ) -> None:
        self._ref = ref
        self._size = size
        self._depth = depth
        self._name = name
        self._check_init()

    def _check_init(self) -> None:
        try:
            self.array = self._ref(  # type: ignore
                name=f'_{self._name}_arr_', size=self._size)
            self.ptr = bt.ArrInt(
                name=f'_{self._name}_ptr_',
                size=self._depth
            )
            self.idx = bt.VarInt(-1, name=f'_{self._name}_idx_')
        except NameError:
            return

    def push(self, size: int) -> None:
        self._check_init()
        self.idx.inc()
        self.ptr[self.idx + 1] <<= self.ptr[self.idx] + size

    def pop(self) -> None:
        self.idx.dec()

    @property
    def index(self) -> bt.VarInt:
        return self.ptr[self.idx + 1]


vars_u = ty.Union[int,
                  str,
                  float,
                  bt.Magic,
                  ty.Type[ty.Union[st.LocArrInt,
                                   st.LocArrStr,
                                   st.LocArrFloat,
                                   st.LocInt,
                                   st.LocStr,
                                   st.LocFloat]]]


class Stack(ab.KSP):
    arrays: ty.Dict[ty.Type[ty.Union[int, str, float]], StackArray]
    frames: ty.List[ty.Dict[type, int]]

    def __init__(self, name: str) -> None:
        self.arrays = dict()
        self.frames = list()
        for n, t in (('int', int), ('str', str), ('float', float)):
            self.arrays[t] = StackArray(f'{name}_{n}', bt.Arr[t])

    def push(self, *vars_: vars_u) -> ty.Tuple[bt.Magic, ...]:
        sizes: ty.Dict[type, int] = {int: 0, str: 0, float: 0}
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]] = {
                                    int: (self.arrays[int].index,
                                          0),
                                    str: (self.arrays[str].index,
                                          0),
                                    float:
                                        (self.arrays[float].index,
                                         0)
                                }
        out_vars: ty.List[bt.Magic] = list()
        for var in vars_:
            out_vars.append(self._push_var(var, sizes, idxes))
        frame = {
            int: idxes[int][1],
            str: idxes[str][1],
            float: idxes[float][1]
        }
        self.frames.append(frame)
        for ref in idxes:
            shift = idxes[ref][1]
            if shift:
                self.arrays[ref].push(shift)
        return tuple(out_vars)

    def _push_var(
        self,
        var: vars_u,
        sizes: ty.Dict[type,
                       int],
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]]
    ) -> bt.Magic:
        if isinstance(var, (int, str, float)):
            ref = type(var)
        else:
            ref = var._ref_type
        idx, shift = idxes[ref]
        if isinstance(var, st.LocMeta):
            return self._push_loc(ref, var, idx, shift, idxes)
        if isinstance(var, bt.ArrBase):
            return self._push_arr(  # type: ignore
                ref, var, idx, shift, idxes
            )
        ret4 = self.arrays[ref].array[idx + shift]
        ret4 <<= var
        shift += 1
        idxes[ref] = (idx, shift)
        return ret4

    def _push_loc(
        self,
        ref: ty.Type[ty.Union[int,
                              str,
                              float]],
        var: st.LocMeta,
        idx: bt.ProcessInt,
        shift: int,
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]]
    ) -> ty.Union[bt.VarBase,
                  st.SubArray]:
        if hasattr(var, 'size'):
            ret = st.SubArray(
                self.arrays[ref].array,
                idx + shift,
                idx + shift + var.size  # type: ignore
            )
            shift += var.size  # type: ignore
            idxes[ref] = (idx, shift)
            return ret
        ret2 = self.arrays[ref].array[idx + shift]
        shift += 1
        idxes[ref] = (idx, shift)
        return ret2

    def _push_arr(
        self,
        ref: ty.Type[bt.KT],
        var: bt.ArrBase,
        idx: bt.ProcessInt,
        shift: int,
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]]
    ) -> st.SubArray:
        ret3 = st.SubArray(
            self.arrays[ref].array,
            idx + shift,
            idx + shift + len(var)
        )
        for var_item, arr_item in cs.For(var, ret3):
            arr_item <<= var_item
        shift += len(var)
        idxes[ref] = (idx, shift)
        return ret3

    def pop(self) -> ty.Dict[type, int]:
        frame = self.frames.pop()
        for ref in frame:
            if frame[ref]:
                self.arrays[ref].pop()
        return frame
