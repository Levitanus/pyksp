"""Implement base control structures: conditions and loops.

If(consition) <context manager>
Else([consition]) <context manager>
Select(expression) -> Case([constant]) <context manager>
While(condition) <context manager>
For(<look for docs>) <Iterator and context manager>
"""
import typing as ty

from . import abstract as ab
from . import base_types as bt


class IfElse(ab.KSP):
    """Base class for conditions."""
    stack: ty.ClassVar[ty.List['If']] = ...
    _is_true: ty.ClassVar[bool] = ...
    true_current: bool

    @property
    def is_true(self) -> bool:
        """Return true, if condition."""
        ...

    @is_true.setter
    def is_true(self, val: bool) -> None:  # pylint: disable=R0201
        ...

    def __enter__(self) -> None:
        """Handle is_true value of current context."""
        ...

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        """Handle is_true for future contexts."""
        ...


class If(IfElse):
    """Implement KSP if condition.

    usage:
    with If(condition: ty.Union[bt.AstBool, bool]):
        KSP code
    with Else([condition: ty.Union[bt.AstBool, bool]]):
        KSP code

    KSP objects will be assigned and processed only in true contexts.
    with context with false condition only code will be generated.
    Note, that code inside false context is still executed, so any
    Python expressions will be executed too. Just KSP realtime
    assignements are ignored."""
    _condition_bool: bool
    _condition_line: str
    _block: ab.OutputBlock
    _out: ab.Output
    _exited: bool

    def __init__(self, condition: ty.Union[bt.AstBool, bool]) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        ...


class Else(IfElse):
    """Implement KSP else/else if statements.

    for If-Else contexts docs see If doc.
    if no condition is passed, used as regular else.
    If initialized within conditions works as elif."""
    _condition: ty.Optional[ty.Union[bt.AstBool, bool]]
    _block: ab.OutputBlock
    _out: ab.Output
    _elif: bool

    def __init__(self,
                 condition: ty.Optional[ty.Union[bt.AstBool, bool]] = None
                 ) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        ...


class SelectCase(IfElse):
    """Base class for select-case (switch) KSP statements."""
    _vars: ty.List[bt.NTU[int]] = ...
    __case_opened: bool = ...

    @property
    def _case_opened(self) -> bool:
        ...

    @_case_opened.setter
    def _case_opened(self, val: bool) -> None:  # pylint: disable=R0201
        ...


class CaseException(Exception):
    """Raise if KSP code passed inside Select context."""

    def __init__(self) -> None:
        ...


def raise_on_put(event: ab.EventAddedToOutput) -> None:
    """Bound to every output added AstRoot event."""
    ...


class Select(SelectCase):
    """Implement KSP select condition.

    usage:
        with Select(<KSP int expression>):
            KSP code here raises error
            with case(int):
                KSP code"""
    out: ab.Output
    block: ab.OutputBlock
    listener: ab.EventListener

    def __init__(self, expression: bt.NTU[int]) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        ...


class Case(SelectCase):
    """Implement KSP select-case case block.

    see Select doc."""
    out: ab.Output
    block: ab.OutputBlock
    listener: ab.EventListener
    state: int

    def __init__(self, state: int) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(  # pylint: disable=W0235
            self, exc_type: ty.Type[Exception], exc_value: ty.Any,
            traceback: ty.Any) -> None:
        ...


class ForEnum:
    """class for static checking of for enum arg."""


enum = ForEnum()

ARGT = ty.Union[int, bt.ArrBase, ForEnum]


class ForClas(ab.KSP):  # pylint: disable=R0902
    """Implement KSP for loops."""
    loop_type: str
    start: int
    step: int
    stop: int
    args: ty.Sequence[ARGT]
    _exited: bool
    _block: ab.OutputBlock
    _out: ab.Output
    _count: int
    _ptr: int

    _idx = bt.Arr[int](name='__for_idx__', size=100)
    _depth = -1

    @staticmethod
    def _check_for_arrays(args: ty.Sequence[ARGT],
                          algo_name: str,
                          should_be_instance: bool = True) -> None:
        ...

    @classmethod
    def _initialize(cls) -> None:
        ...

    def __init__(self, *args: ARGT) -> None:
        ...

    def _parametrized_init(self, *args: ARGT) -> None:
        ...

    def _init_as_enum(self, args: ty.Sequence[ARGT]) -> None:
        ...

    def _init_as_zip(self, args: ty.Sequence[ARGT]) -> None:
        ...

    def _init_as_range(self, args: ty.Sequence[int]) -> None:
        ...

    def __enter__(self) -> 'ForClas':
        ...

    def __exit__(  # pylint: disable=W0235
            self, exc_type: ty.Type[Exception], exc_value: ty.Any,
            traceback: ty.Any) -> None:
        ...

    def __iter__(self) -> 'ForClas':
        ...

    def _exit(self) -> None:
        ...

    def __next__(self) -> ty.Union[ty.Iterable[bt.VarBase], bt.VarBase]:
        ...

    def _check_next(self) -> None:
        ...

    def _count_idx(self) -> None:
        ...

    def _get_block(self) -> ab.OutputBlock:
        ...

    def break_loop(self) -> None:
        """Finish this iteration and exit the loop.

        equals to idx = self.stop"""
        ...


class While(ab.KSP):
    """Wrap context in KSP while syntax.

    still, only while usage is any sort of complex callbacks,
    currently While context manager does nothing more than
    executes code in context one time and wraps it to KSP block:
    while(condition)
        KSP code
    end while"""
    _out: ab.Output
    _block: ab.OutputBlock

    def __init__(self, condition: bt.AstBool) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(  # pylint: disable=W0235
            self, exc_type: ty.Type[Exception], exc_value: ty.Any,
            traceback: ty.Any) -> None:
        ...


_T1 = ty.TypeVar('_T1', int, str, float)
_T2 = ty.TypeVar('_T2', int, str, float)
_T3 = ty.TypeVar('_T3', int, str, float)
_T4 = ty.TypeVar('_T4', int, str, float)
_T5 = ty.TypeVar('_T5', int, str, float)
_T6 = ty.TypeVar('_T6', int, str, float)
_T7 = ty.TypeVar('_T7', int, str, float)
_ABA = bt.ArrBase[bt.VarBase[bt.KT, bt.KT], bt.KT, bt.KT]
_BA = bt.VarBase[bt.KT, bt.KT]
# a = _ABA[_T1]

_I = bt.VarInt
_F = bt.VarFloat
_S = bt.VarStr
_IA = bt.ArrInt
_FA = bt.ArrFloat
_SA = bt.ArrStr


@ty.overload
def For(_1: _IA) -> ty.Iterator[_I]:
    ...


@ty.overload
def For(_1: _SA) -> ty.Iterator[_S]:
    ...


@ty.overload
def For(_1: _FA) -> ty.Iterator[_F]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA) -> ty.Iterator[ty.Tuple[_I, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA) -> ty.Iterator[ty.Tuple[_S, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA) -> ty.Iterator[ty.Tuple[_F, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA) -> ty.Iterator[ty.Tuple[_I, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA) -> ty.Iterator[ty.Tuple[_S, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA) -> ty.Iterator[ty.Tuple[_F, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA) -> ty.Iterator[ty.Tuple[_I, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA) -> ty.Iterator[ty.Tuple[_S, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA) -> ty.Iterator[ty.Tuple[_F, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _IA) -> ty.Iterator[ty.Tuple[_I, _I, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _IA) -> ty.Iterator[ty.Tuple[_S, _I, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _IA) -> ty.Iterator[ty.Tuple[_F, _I, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _IA) -> ty.Iterator[ty.Tuple[_I, _S, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _IA) -> ty.Iterator[ty.Tuple[_S, _S, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _IA) -> ty.Iterator[ty.Tuple[_F, _S, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _IA) -> ty.Iterator[ty.Tuple[_I, _F, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _IA) -> ty.Iterator[ty.Tuple[_S, _F, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _IA) -> ty.Iterator[ty.Tuple[_F, _F, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _SA) -> ty.Iterator[ty.Tuple[_I, _I, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _SA) -> ty.Iterator[ty.Tuple[_S, _I, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _SA) -> ty.Iterator[ty.Tuple[_F, _I, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _SA) -> ty.Iterator[ty.Tuple[_I, _S, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _SA) -> ty.Iterator[ty.Tuple[_S, _S, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _SA) -> ty.Iterator[ty.Tuple[_F, _S, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _SA) -> ty.Iterator[ty.Tuple[_I, _F, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _SA) -> ty.Iterator[ty.Tuple[_S, _F, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _SA) -> ty.Iterator[ty.Tuple[_F, _F, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _FA) -> ty.Iterator[ty.Tuple[_I, _I, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _FA) -> ty.Iterator[ty.Tuple[_S, _I, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _FA) -> ty.Iterator[ty.Tuple[_F, _I, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _FA) -> ty.Iterator[ty.Tuple[_I, _S, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _FA) -> ty.Iterator[ty.Tuple[_S, _S, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _FA) -> ty.Iterator[ty.Tuple[_F, _S, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _FA) -> ty.Iterator[ty.Tuple[_I, _F, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _FA) -> ty.Iterator[ty.Tuple[_S, _F, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _FA) -> ty.Iterator[ty.Tuple[_F, _F, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _I, _I, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _I, _I, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _I, _I, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _S, _I, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _S, _I, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _S, _I, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _F, _I, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _F, _I, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _F, _I, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _I, _S, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _I, _S, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _I, _S, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _S, _S, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _S, _S, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _S, _S, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _F, _S, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _F, _S, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _F, _S, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _I, _F, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _I, _F, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _I, _F, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _S, _F, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _S, _F, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _S, _F, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_I, _F, _F, _I]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_S, _F, _F, _I]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[_F, _F, _F, _I]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _I, _I, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _I, _I, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _I, _I, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _S, _I, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _S, _I, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _S, _I, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _F, _I, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _F, _I, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _F, _I, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _I, _S, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _I, _S, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _I, _S, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _S, _S, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _S, _S, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _S, _S, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _F, _S, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _F, _S, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _F, _S, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _I, _F, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _I, _F, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _I, _F, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _S, _F, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _S, _F, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _S, _F, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_I, _F, _F, _S]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_S, _F, _F, _S]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[_F, _F, _F, _S]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _I, _I, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _I, _I, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _I, _I, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _S, _I, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _S, _I, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _S, _I, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _F, _I, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _F, _I, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _F, _I, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _I, _S, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _I, _S, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _I, _S, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _S, _S, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _S, _S, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _S, _S, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _F, _S, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _F, _S, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _F, _S, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _IA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _I, _F, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _IA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _I, _F, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _IA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _I, _F, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _SA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _S, _F, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _SA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _S, _F, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _SA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _S, _F, _F]]:
    ...


@ty.overload
def For(_1: _IA, _2: _FA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_I, _F, _F, _F]]:
    ...


@ty.overload
def For(_1: _SA, _2: _FA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_S, _F, _F, _F]]:
    ...


@ty.overload
def For(_1: _FA, _2: _FA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[_F, _F, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA,
        _3: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA,
        _3: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA,
        _3: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA,
        _3: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA,
        _3: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA,
        _3: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA,
        _3: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA,
        _3: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA,
        _3: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA,
        _4: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA,
        _4: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA,
        _4: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _IA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _I, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _SA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _S, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _FA,
        _5: _IA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _F, _I]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _IA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _I, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _SA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _S, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _FA,
        _5: _SA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _F, _S]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _IA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _I, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _SA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _S, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _IA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _I, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _IA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _I, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _IA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _I, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _SA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _S, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _SA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _S, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _SA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _S, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _IA, _3: _FA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _I, _F, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _SA, _3: _FA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _S, _F, _F, _F]]:
    ...


@ty.overload
def For(_1: ForEnum, _2: _FA, _3: _FA, _4: _FA,
        _5: _FA) -> ty.Iterator[ty.Tuple[bt.VarInt, _F, _F, _F, _F]]:
    ...


@ty.overload
def For(_1: int) -> ty.Iterator[bt.VarInt]:
    ...


@ty.overload
def For(_1: int, _2: int) -> ty.Iterator[bt.VarInt]:
    ...


@ty.overload
def For(_1: int, _2: int, _3: int) -> ty.Iterator[bt.VarInt]:
    ...
