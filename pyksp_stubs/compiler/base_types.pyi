from abstract import KspObject
from abstract import KSP
from abstract import Output
from abstract import KspGeneric

from typing import Union
from typing import TypeVar
from typing import Any
from typing import List
from typing import Callable
from typing import Tuple
from typing import Generic
from typing import Sequence
from typing import overload
from typing import NoReturn
from typing import cast
from typing_extensions import Protocol
from typing_extensions import runtime


T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
ST = TypeVar('ST', bound=str)
IT = TypeVar('IT', bound=int)
FT = TypeVar('FT', bound=float)

ValidKspVarU = Union['ValidKspVar[T]', T]


@runtime
class ValidKspVar(Protocol[T]):
    _value: T

    def _set_compiled(self,
                      value: ValidKspVarU[T]) -> None:
        ...

    def get_compiled(self) -> str:
        ...

    def get_runtime(self) -> T:
        ...

    def set_runtime(self, value: T) -> None:
        ...

    def __ilshift__(self,
                    other: ValidKspVarU[T])\
            -> ValidKspVarU[T]:
        ...

    def __rlshift__(self,
                    other: ValidKspVarU[T])\
            -> ValidKspVarU[T]:
        ...


@runtime
class ValidAstObject(Protocol[T_co]):

    def expand(self) -> str:
        ...

    def get_value(self) -> T_co:
        ...


ValidAstObjectStr = Union[ValidAstObject[ST],
                          ValidAstObject[FT],
                          ValidAstObject[FT]]


def get_runtime(value: Union[ValidKspVar[T],
                             ValidAstObject[T],
                             T]) -> T:
    ...


def get_compiled(value: Union[ValidKspVar[T],
                              ValidAstObject[T],
                              T]) -> str:
    ...


class AstBase(Generic[T]):
    ...


class AstAssign(Generic[T]):
    '''special top-level Ast class for making assigements.
    Has not method get_value()
    '''

    def __init__(self, to_arg: ValidKspVar[T],
                 from_arg: Union[ValidKspVar[T],
                                 ValidAstObject[T], T]) -> None:
        ...

    def expand(self) -> str:
        '''expand AstObject to string representation "a := b"'''
        ...

    def get_value(self) -> NoReturn:
        ...


class AstAddStr(AstBase, Generic[ST]):

    def __init__(self, arg1: ValidAstObjectStr,
                 arg2: ValidAstObjectStr) -> None:
        ...

    def expand(self) -> str:
        ...

    def get_value(self) -> str:
        ...

    def __add__(self, other: ValidAstObjectStr) -> 'AstAddStr':
        ...

    def __radd__(self, other: ValidAstObjectStr) -> 'AstAddStr':
        ...

    def __iadd__(self, other: ValidAstObjectStr) -> NoReturn:
        ...


ValidAstObjectU = Union[ValidAstObject[FT], FT]


class AstOperator(AstBase, Generic[FT]):
    _args: Sequence[FT]
    priority: int

    def __init__(self,
                 *args: Sequence[ValidAstObjectU[FT]]) -> None:
        ...

    @overload
    def unpack_arg(self, arg: ST) -> str:
        ...

    @overload
    def unpack_arg(self, arg: IT) -> int:
        ...

    @overload
    def unpack_arg(self, arg: FT) -> float:
        ...

    def unary(self, string: str,
              val: ValidAstObjectU[FT]) -> str:
        ...

    def bracket_unary(self, string: str,
                      val: ValidAstObjectU[FT]) -> str:
        ...

    def standart(self, string: str,
                 val1: ValidAstObjectU[FT],
                 val2: ValidAstObjectU[FT]) -> str:
        ...

    def bracket_double(self, string: str,
                       val1: ValidAstObjectU[FT],
                       val2: ValidAstObjectU[FT]) -> str:
        ...

    def __neg__(self) -> 'AstNeg[FT]':
        ...

    def __invert__(self) -> 'AstNot[FT]':
        ...

    def __add__(self, other: ValidAstObjectU[FT])\
            -> 'AstAdd[FT]':
        ...

    def __radd__(self, other: ValidAstObjectU[FT])\
            -> 'AstAdd[FT]':
        ...

    def __iadd__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __sub__(self, other: ValidAstObjectU[FT])\
            -> 'AstSub[FT]':
        ...

    def __rsub__(self, other: ValidAstObjectU[FT])\
            -> 'AstSub[FT]':
        ...

    def __isub__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __mul__(self, other: ValidAstObjectU[FT])\
            -> 'AstMul[FT]':
        ...

    def __rmul__(self, other: ValidAstObjectU[FT])\
            -> 'AstMul[FT]':
        ...

    def __imul__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __truediv__(self, other: ValidAstObjectU[FT])\
            -> 'AstDiv[FT]':
        ...

    def __rtruediv__(self, other: ValidAstObjectU[FT])\
            -> 'AstDiv[FT]':
        ...

    def __itruediv__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __floordiv__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __rfloordiv__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __ifloordiv__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __mod__(self, other: ValidAstObjectU[FT])\
            -> 'AstMod[FT]':
        ...

    def __rmod__(self, other: ValidAstObjectU[FT])\
            -> 'AstMod[FT]':
        ...

    def __imod__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __pow__(self, other: ValidAstObjectU[FT])\
            -> 'AstPow[FT]':
        ...

    def __rpow__(self, other: ValidAstObjectU[FT])\
            -> 'AstPow[FT]':
        ...

    def __ipow__(self, other: ValidAstObjectU[FT]) -> NoReturn:
        ...

    def __and__(self, other: ValidAstObjectU[FT]) \
        -> Union['AstLogAnd[FT]',
                 'AstBinAnd[FT]']:
        ...

    def __rand__(self, other: ValidAstObjectU[FT]) \
        -> Union['AstLogAnd[FT]',
                 'AstBinAnd[FT]']:
        ...

    def __or__(self, other: ValidAstObjectU[FT]) \
        -> Union['AstLogOr[FT]',
                 'AstBinOr[FT]']:
        ...

    def __ror__(self, other: ValidAstObjectU[FT]) \
        -> Union['AstLogOr[FT]',
                 'AstBinOr[FT]']:
        ...

    def __eq__(self,                                      # type: ignore
               other: ValidAstObjectU[FT])->'AstEq[FT]':  # type: ignore
        ...

    def __ne__(self,                                      # type: ignore
               other: ValidAstObjectU[FT])->'AstNe[FT]':  # type: ignore
        ...

    def __lt__(self, other: ValidAstObjectU[FT])\
            -> 'AstLt[FT]':
        ...

    def __gt__(self, other: ValidAstObjectU[FT])\
            -> 'AstGt[FT]':
        ...

    def __le__(self, other: ValidAstObjectU[FT])\
            -> 'AstLe[FT]':
        ...

    def __ge__(self, other: ValidAstObjectU[FT])\
            -> 'AstGe[FT]':
        ...

    def abs(self) -> 'AstAbs[FT]':
        ...


class AstNeg(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstNot(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstAdd(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstSub(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstMul(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstDiv(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstMod(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstPow(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstLogAnd(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstBinAnd(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstLogOr(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstBinOr(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstEq(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstNe(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstLt(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstGt(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstLe(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstGe(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class AstAbs(AstOperator, Generic[FT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> FT:
        ...


class KspVar(KspObject, Generic[T]):

    def __init__(self,
                 value: ValidKspVarU[T]=...,
                 name: str=...,
                 preserve_name: bool=...,
                 is_local: bool=...,
                 persist: bool=...) -> None:
        ...

    def read(self) -> None:
        ...

    def _set_compiled(self,
                      value: ValidKspVarU[T]) -> None:
        ...

    def get_compiled(self) -> str:
        ...

    def get_runtime(self) -> T:
        ...

    def set_runtime(self, value: T) -> None:
        ...

    def __ilshift__(self,
                    other: ValidKspVarU[T])\
            -> 'KspVar[T]':
        ...

    def __rlshift__(self,
                    other: ValidKspVarU[T])\
            -> 'KspVar[T]':
        ...

    @property
    def val(self) -> Union[T, str]:
        ...

    @property
    def _value(self) -> T:
        ...

    @_value.setter
    def _value(self, value: ValidKspVarU[T]) -> None:
        ...


class
