"""Stack and StackArray classes."""
import typing as ty

from . import abstract as ab
from . import base_types as bt
from . import control_statements as cs
from . import service_types as st


class StackArray(ty.Generic[bt.KAT]):
    """Handle arrays with their pointers and initializators."""
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
        """Initialize.

        name is unique arrays name
        ref is type of array, being handled (ArrInt, ArrStr, ArrFloat)
        size is main arr size (32768 by default)
        depth is ptr array size (100 by default)
        """
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
        """Shift ptr by size."""
        self._check_init()
        self.idx.inc()
        self.ptr[self.idx + 1] <<= self.ptr[self.idx] + size

    def pop(self) -> None:
        """Decrease index by the last frame size."""
        self.idx.dec()

    @property
    def index(self) -> bt.VarInt:
        """Return current frame ptr."""
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
    """Implement parametrized stack (mostly, for handling functions).

    name used for unique indentification of all stack objects.
    within push(*vars_) method all input int, str, float and KSP objects
    can be passed to the stack arrays and returned as their items.
    pop method decreases ptrs of arrays used in frame and returns
    Dict[Type[Union[int,str,float]], int] of used sizes.
    """
    arrays: ty.Dict[ty.Type[ty.Union[int, str, float]], StackArray]
    frames: ty.List[ty.Dict[type, int]]

    def __init__(self, name: str) -> None:
        """Initialize."""
        self.arrays = dict()
        self.frames = list()
        for n, t in (('int', int), ('str', str), ('float', float)):
            self.arrays[t] = StackArray(f'{name}_{n}', bt.Arr[t])

    def push(self, *vars_: vars_u) -> ty.Tuple[bt.Magic, ...]:
        """Pass vars to stack arrays and return their items."""
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
        out_vars: ty.List[bt.Magic] = [
            self._push_var(var,
                           idxes) for var in vars_
        ]
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
            return self._push_loc(ref, var, idxes)
        if isinstance(var, bt.ArrBase):
            return self._push_arr(  # type: ignore
                ref,
                var,
                idxes
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
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]]
    ) -> ty.Union[bt.VarBase,
                  st.SubArray]:
        idx, shift = idxes[ref]
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
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]]
    ) -> st.SubArray:
        idx, shift = idxes[ref]
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
        """Shift down ptr of arrays, used in frame.

        Returns dict with size of areas, used in this frame."""
        frame = self.frames.pop()
        for ref in frame:
            if frame[ref]:
                self.arrays[ref].pop()
        return frame
