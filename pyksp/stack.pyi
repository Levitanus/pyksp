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
        ...

    def _check_init(self) -> None:
        ...

    def push(self, size: int) -> None:
        """Shift ptr by size."""
        ...

    def pop(self) -> None:
        """Decrease index by the last frame size."""
        ...

    @property
    def index(self) -> bt.VarInt:
        """Return current frame ptr."""
        ...


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
        ...

    def push(self, *vars_: vars_u) -> ty.Tuple[bt.Magic, ...]:
        """Pass vars to stack arrays and return their items."""
        ...

    def _push_var(
        self,
        var: vars_u,
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]]
    ) -> bt.Magic:
        ...

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
        ...

    def _push_arr(
        self,
        ref: ty.Type[bt.KT],
        var: bt.ArrBase,
        idxes: ty.Dict[type,
                       ty.Tuple[bt.ProcessInt,
                                int]]
    ) -> st.SubArray:
        ...

    def pop(self) -> ty.Dict[type, int]:
        """Shift down ptr of arrays, used in frame.

        Returns dict with size of areas, used in this frame."""
        ...
