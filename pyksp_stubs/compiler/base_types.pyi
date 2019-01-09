from abc import abstractmethod
from abc import ABCMeta
from warnings import warn

from .abstract import KspObject
from .abstract import KSP
from .abstract import Output

from typing import List
from typing import Any
from typing import Union
from typing import Callable
from typing import Tuple
from typing import Sequence
from typing import Iterable
from typing import NoReturn
from typing import Iterator
from typing import Optional
from typing import TypeVar
from typing import overload
from typing import Type
from typing import cast
from typing import Generic
from typing import NewType
from typing_extensions import Protocol

from __future__ import annotations


T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)


class AstBase(KSP, Generic[T]):
    '''Base abstract class for all Ast objects.
    Requires overriding of methods expand() and get_value()

    expand(self) has to return string representation of method
    get_value(self) has to behave like real representation of method
    '''

    @abstractmethod
    def expand(self) -> str:
        pass

    @abstractmethod
    def get_value(self) -> T:
        pass


ITU = Union[int, 'KspIntVar']
RTU = Union[float, 'KspRealVar']
STU = Union[float, 'KspRealVar']

S = TypeVar('S')
GT = TypeVar('GT', Union['KspIntVar', int],
             Union['KspRealVar', float], Union['KspStrVar', str],
             'NumericSupport')
ST = TypeVar('ST', str, float)

OP = TypeVar('OP', ITU, RTU, 'NumericSupport')

ValidAstInput = Union['KspVar', str, float]
# ValidAstInputGen = Union[GT, ST]


class AstAssign(AstBase):
    '''special top-level Ast class for making assigements.
    Has not method get_value()
    '''

    def __init__(self, to_arg: 'KspVar', from_arg: ValidAstInput) -> None:
        ...

    def expand(self) -> str:
        '''expand AstObject to string representation "a := b"'''
        ...

    def get_value(self) -> NoReturn:
        raise NotImplementedError('AstAssign can not return value')


class AstAddString(AstBase):
    '''special operator method for strings concatenation
    args has to be instances of (callable, str, AstBase, KspVar)
    '''
    _args: List[ValidAstInput]

    def __init__(self, arg1: ValidAstInput, arg2: ValidAstInput) -> None:
        ...

    def expand(self) -> str:
        '''returns "a & b"'''
        ...

    def get_value(self) -> str:
        '''returns self.expand()'''
        ...

    def __add__(self, other: ValidAstInput) -> 'AstAddString':
        '''returns AstAddString(self, other)'''
        ...

    def __radd__(self, other: ValidAstInput) -> 'AstAddString':
        '''returns AstAddString(other, self)'''
        ...

    def __iadd__(self, other: ValidAstInput) -> NoReturn:
        raise NotImplementedError(
            'method __iadd__ is not implemented')


class NumericSupport(Generic[OP]):

    def __neg__(self) ->Union[OP, AstNeg[OP]]:
        ...

    def __invert__(self) ->Union[OP, AstNot[OP]]:
        ...

    def __add__(self, other: OP) ->Union[OP, AstAdd[OP]]:
        ...

    def __radd__(self, other: OP) ->Union[OP, AstAdd[OP]]:
        ...

    def __iadd__(self: T, other: OP) ->Union[OP, NoReturn, T]:
        ...

    def __sub__(self, other: OP) ->Union[OP, AstSub[OP]]:
        ...

    def __rsub__(self, other: OP) ->Union[OP, AstSub[OP]]:
        ...

    def __isub__(self: T, other: OP) ->Union[OP, NoReturn, T]:
        ...

    @overload
    def __mul__(self, other: Union[NumericSupport[ITU], ITU]) \
            -> Union[ITU, AstMul[ITU]]:
        ...

    @overload
    def __mul__(self, other: Union[NumericSupport[RTU], RTU]) \
            -> Union[RTU, AstMul[RTU]]:
        ...

    @overload
    def __rmul__(self, other: Union[NumericSupport[ITU], ITU]) \
            -> Union[ITU, AstMul[ITU]]:
        ...

    @overload
    def __rmul__(self, other: Union[NumericSupport[RTU], RTU]) \
            -> Union[RTU, AstMul[RTU]]:
        ...

    @overload
    def __imul__(self: T, other: Union[NumericSupport[ITU], ITU])\
            ->Union[Union[ITU, AstMul[ITU]], NoReturn, T]:
        ...

    @overload
    def __imul__(self: T, other: Union[NumericSupport[RTU], RTU])\
            ->Union[Union[RTU, AstMul[RTU]], NoReturn, T]:
        ...

    @overload
    def __truediv__(self, other: Union[NumericSupport[ITU], ITU]) \
            -> Union[ITU, AstDiv[ITU]]:
        ...

    @overload
    def __truediv__(self, other: Union[NumericSupport[RTU], RTU]) \
            -> Union[RTU, AstDiv[RTU]]:
        ...

    @overload
    def __rtruediv__(self, other: Union[NumericSupport[ITU], ITU]) \
            -> Union[ITU, AstDiv[ITU]]:
        ...

    @overload
    def __rtruediv__(self, other: Union[NumericSupport[RTU], RTU]) \
            -> Union[RTU, AstDiv[RTU]]:
        ...

    def __itruediv__(self: T, other: OP) ->Union[OP, NoReturn, T]:
        ...

    def __floordiv__(self, other: OP) ->Union[OP, NoReturn]:
        ...

    def __rfloordiv__(self, other: OP) ->Union[OP, NoReturn]:
        ...

    def __ifloordiv__(self: T, other: OP) ->Union[OP, NoReturn, T]:
        ...

    def __mod__(self, other: OP) ->Union[OP, AstMod[OP]]:
        ...

    def __rmod__(self, other: OP) ->Union[OP, AstMod[OP]]:
        ...

    def __imod__(self: T, other: OP) ->Union[OP, NoReturn, T]:
        ...

    def __pow__(self, other: OP) ->Union[OP, AstPow[OP]]:
        ...

    def __rpow__(self, other: OP) ->Union[OP, AstPow[OP]]:
        ...

    def __ipow__(self: T, other: OP) ->Union[OP, NoReturn, T]:
        ...

    def __eq__(self, other: OP) ->Union[OP, AstEq[OP]]:
        ...

    def __ne__(self, other: OP) ->Union[OP, AstNe[OP]]:
        ...

    def __lt__(self, other: OP) ->Union[OP, AstLt[OP]]:
        ...

    def __gt__(self, other: OP) ->Union[OP, AstGt[OP]]:
        ...

    def __le__(self, other: OP) ->Union[OP, AstLe[OP]]:
        ...

    def __ge__(self, other: OP) ->Union[OP, AstGe[OP]]:
        ...

    def abs(self) -> AstAbs[OP]:
        ...

    def __and__(self, other: OP) -> Union[AstLogAnd[OP],
                                          AstBinAnd[OP], OP]:
        ...

    def __rand__(self, other: OP)-> Union[AstLogAnd[OP],
                                          AstBinAnd[OP], OP]:
        ...

    def __or__(self, other: OP) -> Union[AstLogOr[OP], AstBinOr[OP], OP]:
        ...

    def __ror__(self, other: OP)-> Union[AstLogOr[OP],
                                         AstBinOr[OP], OP]:
        ...


class AstOperator(AstBase, NumericSupport[OP],
                  Generic[OP], metaclass=ABCMeta):
    '''Base abstract class for all operators.'''
    _args: List[OP]
    priority: int

    def __init__(self, *args: OP) -> None:
        ...

    def unpack_args(self, *args: Sequence[OP]) -> ST:
        '''gets values of KspVar objects and expands AstBase objects
        keeps str, int and float objects untouched
        returns tuple of args or only arg, if it was alone
        '''
        ...

    def unary(self, string: str, val: OP) -> str:
        '''returns f"{string}{val}"'''
        ...

    def standart(self, string: str,
                 val1: OP,
                 val2: OP) -> str:
        '''returns f"{val1} {string} {val2}"'''
        ...

    def bracket_unary(self, string: str,
                      val: OP) -> str:
        '''returns f"{string}({val})"'''
        ...

    def bracket_double(self, string: str,
                       val1: OP,
                       val2: OP) -> str:
        '''returns f"{string}({val1}, {val2})"'''
        ...

    def get_value_proxy(self, func: Callable[[OP], ST]) -> ST:
        '''use via super
        accepts func (lambda?) and passes init args to it.
        args are expanded via:
        _get_runtime() for KspVar objects
        get_value() for AstBase objects'''
        ...


class AstNeg(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> ST:
        ...


class AstNot(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstAdd(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstSub(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstMul(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstDiv(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstMod(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstPow(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstLogAnd(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstBinAnd(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstLogOr(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstBinOr(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstEq(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstNe(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstLt(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstGt(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstLe(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstGe(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class AstAbs(AstOperator, Generic[OP]):

    def expand(self) -> str:
        ...

    def get_value(self) -> OP:
        ...


class KspVar(KspObject, Generic[GT]):
    '''Abstract base class for every object can behave like variable:
    int, string or real(float) variables and arrays of KSP
    '''
    _ref_type: Union[Type[GT], Tuple[Type[GT], ...]]
    __value: GT
    _persistent: bool
    _read: bool

    def __init__(self, name: str,
                 value: Optional[GT]=...,
                 ref_type: Optional[Union[Type[GT],
                                          Tuple[Type[GT], ...]]]=...,
                 name_prefix: str=...,
                 name_postfix: str=...,
                 preserve_name: bool=...,
                 has_init: bool=...,
                 is_local: bool=...,
                 persist: bool=...) -> None:
        ...

    def _check_val_type(self, val: GT) -> ST:
        '''check if val is instance of ref_type.
        expands val if it is instance of KspVar

        returns val
        '''
        ...

    def read(self) -> None:
        '''calls KSP function read_persistent_var() and adds
        make_persistent() function call at declaration if not any
        '''
        ...

    @property
    def ref_type(self) -> Type[GT]:
        '''getter. returns tuple of types'''
        ...

    def _set_compiled(self, val: GT) -> None:
        '''Puts AstAssign to Output()
        calls self._set_runtime with "val" rutime val
        '''
        ...

    @overload
    def _get_rutime_other(self, other: Union['KspIntVar', int]) -> int:
        '''returns runtime representation of KspVar and AstBase
        or just passed value'''
        ...

    @overload
    def _get_rutime_other(self, other: Union['KspStrVar', str]) -> str:
        ...

    @overload
    def _get_rutime_other(self,
                          other: Union['KspRealVar', float]) -> float:
        ...

    @abstractmethod
    def _get_compiled(self) -> str:
        pass

    @abstractmethod
    def _set_runtime(self, val: GT) -> None:
        pass

    @abstractmethod
    def _get_runtime(self) -> GT:
        pass

    def __ilshift__(self: T, other: Union[OP, GT]) -> T:
        '''under compilation calls self._set_compiled
        otherwise calls self._set_runtime

        returns self'''
        ...

    def __rlshift__(self,
                    other: OP) -> Union[str, OP]:
        '''under compilation calls self._get_compiled
        otherwise calls self._get_runtime
        '''
        ...

    @property
    def val(self) -> Union[str, ST]:
        '''under compilation calls self._get_compiled
        otherwise calls self._get_runtime
        '''
        ...

    @property
    def _value(self) -> ST:
        '''returns value passed in __init__ as "value" parameter'''
        ...

    @_value.setter
    def _value(self, val: GT) -> None:
        '''sets the value could be taken from _value property'''
        ...


class KspStrVar(KspVar[Union['KspStrVar', str]], metaclass=ABCMeta):
    '''Keeps str objects or string representations of KspVar objects
    can be only assigned via <<= or concantenated via + and +=
    '''

    def _set_compiled(self, other: GT) -> None:
        ...

    def __add__(self, other: GT) -> Union[AstAddString, str]:
        ...

    def __radd__(self, other: GT) -> Union[AstAddString, str]:
        ...

    def __iadd__(self, other: GT) -> Union[AstAddString, str]:
        ...

    @abstractmethod
    def _set_runtime(self, other: Union['KspStrVar', str]) -> None:
        ...

    def _add_compiled(self, arg1: GT, arg2: GT) -> AstAddString:
        ...

    def _add_runtime(self, arg1: GT, arg2: GT) -> str:
        ...

    def __check_add_runtime_str(self, other: GT) -> str:
        ...

    def _generate_executable(self) -> NoReturn:
        ...


class KspNumeric(KspVar[OP], NumericSupport[OP], Generic[OP]):
    '''abstract base class for int and real KSP variables
    has to keep class variable "warning_types", consists tuple
    of classes for blocking magic methods.
    For example:
    warning_types = (KspIntVar, str, KspStrVar)

    '''

    warning_types: List[type] = ...
    _warning_types_exc_str: str = ...

    class TypeWarn(Warning):
        '''raised when type convertion is needed'''

        def __init__(self, val: str) -> None:
            ...

    # @abstractmethod
    # def __truediv__(self, other: OP) -> Union[AstDiv[OP], OP]:
    #     pass

    # @abstractmethod
    # def __rtruediv__(self,
    #                  other: OP) -> Union[AstDiv[OP], OP]:
    #     pass

    # @abstractmethod
    # def __itruediv__(self, other: OP) -> Union[AstDiv[OP], OP]:
    #     pass

    def _generate_executable(self) -> NoReturn:
        ...

    def _warn_other(self, value: Any) -> None:
        ...

    def _expand_other(self, other: OP) -> Union[str, int, float]:
        '''returns other, expanded via val property if is
        instance of KspVar'''
        ...


class KspIntVar(KspNumeric[ITU], metaclass=ABCMeta):

    @overload
    def __truediv__(self, other: Union[NumericSupport[ITU], ITU]) \
            -> Union[ITU, AstDiv[ITU]]:
        ...

    @overload
    def __truediv__(self, other: Union[NumericSupport[RTU], RTU]) \
            -> NoReturn:
        ...

    def __rtruediv__(self, other: Union[NumericSupport[ITU], ITU]) \
            -> Union[ITU, AstDiv[ITU]]:
        ...

    def __rtruediv__(self, other: Union[NumericSupport[RTU], RTU]) \
            -> NoReturn:
        ...

    @overload
    def __itruediv__(self: T, other: Union[NumericSupport[ITU], ITU]) \
            -> T:
        ...

    @overload
    def __itruediv__(self, other: Union[NumericSupport[RTU], RTU]) \
            -> NoReturn:
        ...

    def __floordiv__(self, other: Union[AstOperator[ITU], ITU])\
            -> NoReturn:
        ...

    def __rfloordiv__(self, other: Union[AstOperator[ITU], ITU])\
            -> NoReturn:
        ...

    def __ifloordiv__(self, other: Union[AstOperator[ITU], ITU])\
            -> NoReturn:
        ...

    def __mod__(self, other: Union[AstOperator[ITU], ITU])\
            -> Union[AstMod[ITU], ITU]:
        ...

    def __rmod__(self, other: Union[AstOperator[ITU], ITU])\
            -> Union[AstMod[ITU], ITU]:
        ...


class KspRealVar(KspNumeric[RTU], metaclass=ABCMeta):
    def __truediv__(self, other: RTU) -> Union[AstDiv[RTU], RTU]:
        ...

    def __rtruediv__(self, other: RTU) -> Union[AstDiv[RTU], RTU]:
        ...

    def __itruediv__(self: T, other: RTU) -> Union[AstDiv[RTU], T]:
        ...

    def __floordiv__(self, other: RTU) -> NoReturn:
        raise ArithmeticError('use built-in floor(x) instead')

    def __rfloordiv__(self, other: RTU) -> NoReturn:
        raise ArithmeticError('use built-in floor(x) instead')

    def __ifloordiv__(self, other: RTU) -> NoReturn:
        raise ArithmeticError('use built-in floor(x) instead')

    def __round__(self, other: RTU) -> NoReturn:
        raise ArithmeticError('use built-in round(x) instead')

    def __pow__(self, other: RTU) -> Union[AstPow[RTU], RTU]:
        ...

    def __rpow__(self, other: RTU) -> Union[AstPow[RTU], RTU]:
        ...

    def __ipow__(self, other: RTU) -> Union[AstPow[RTU], T]:
        ...

    def __and__(self, other: RTU) -> Union[RTU, AstBinAnd[RTU]]:
        ...

    def __rand__(self, other: RTU) -> Union[RTU, AstBinAnd[RTU]]:
        ...

    def __or__(self, other: RTU) -> Union[RTU, AstBinOr[RTU]]:
        ...

    def __ror__(self, other: RTU) -> Union[RTU, AstBinOr[RTU]]:
        ...


class KspArray(KspVar[GT], Generic[GT], metaclass=ABCMeta):
    '''abstract base class for making int str and real KSP arrays
    ref_type is values accepted for sequence input and items assignment
    item_type is single class reference for local object construction
    via __getitem__ and _runtime_iter.
    (local maked by kwarg "local=True", value handles via standart
    kwarg value)
    '''
    _item_type: Union[Type[GT],
                      Tuple[Type[GT], ...]]
    __pure_name: str
    __prefix: str
    __postfix: str
    __init_seq: Optional[List[Optional[GT]]]
    _seq: List[Optional[GT]]
    _init_size: int
    _size: int
    __default: Optional[GT]
    _cashed: List[Optional[Union[KspIntVar, KspStrVar, KspRealVar]]]

    def __init__(self,
                 name: str,
                 name_prefix: str=...,
                 name_postfix: str=...,
                 preserve_name: bool=...,
                 has_init: bool=...,
                 is_local: bool=...,
                 ref_type: Optional[Union[Type[GT],
                                          Tuple[Type[GT], ...]]]=...,
                 item_type: Optional[Union[Type[GT],
                                           Tuple[Type[GT], ...]]]=...,
                 size: Optional[int]=...,
                 seq: Optional[List[Optional[GT]]]=...,
                 persist: bool=...,
                 def_val: Optional[GT]=...) -> None:
        ...

    @property
    def default(self) -> Optional[GT]:
        return self.__default

    def _init_seq(self, seq: List[Optional[GT]]) -> List[Optional[GT]]:
        '''makes self._cashed and returns seq
        depends on init arguments'''
        ...

    def _generate_init(self) -> List[str]:
        '''returns declaration line and optional addition assignement
        lines for non-numeric item_types'''
        ...

    @property
    def item_type(self) -> Union[Type[GT],
                                 Tuple[Type[GT], ...]]:
        '''getter for item_type argument'''
        ...

    def append(self, val: GT) -> None:
        '''puts value to the last used key of array, if size permits'''
        ...

    def extend(self, seq: List[GT]) -> None:
        '''extends array if size permits'''
        ...

    def __getitem__(self, idx: ITU) -> KspVar[GT]:
        '''returns item_type (KspVar instance) local objects with
        value from squence and name of array index ("array[idx]")
        resource-unefficient. cashes object for later usage, but
        rewrites several methods for keeping index fresh
        For lite usage (just what puted in seq) use _getitem_fast(idx)
        '''
        ...

    def _getitem_full(self, idx: ITU) -> KspVar[GT]:
        ...

    def _getitem_fast(self, idx: ITU) -> Optional[GT]:
        '''returns value from sequence (even None)
        at idx value (runtime representation)
        '''
        ...

    def __setitem__(self, idx: ITU, val: ITU) -> None:
        '''calls self.set_at_idx(idx, val)'''
        ...

    def set_at_idx(self, idx: ITU, val: ITU) -> None:
        '''puts value to the cashed object at idx.
        Or makes one if not exists'''
        ...

    def _get_runtime_idx(self, idx: ITU) -> int:
        '''get runtime value from KspIntVar, or return int index'''
        ...

    def _check_idx(self, idx: ITU) -> Union[str, int]:
        '''returns index, got from int object, or val property of
        KspIntVar object

        raises TypeError on incorrect index type'''
        ...

    def _check_cashed_item(self, idx: int) -> bool:
        '''returns cashed object from index, or make one.'''
        ...

    def _item_get_compiled(self, arr: 'KspArray', idx: int) -> str:
        '''method for overriding cashed item method within new name'''
        ...

    def _item_get_runtime(self, arr: 'KspArray[GT]',
                          idx: int) -> Optional[GT]:
        '''method for overriding cashed item method within new value'''
        ...

    def _item_set_runtime(self, arr: 'KspArray[GT]',
                          idx: int, val: GT) -> None:
        '''method for overriding cashed item method within new value'''
        ...

    def _item_name(self, arr: 'KspArray', idx: Union[str, int]) -> str:
        '''method for overriding cashed item method within new name'''
        ...

    def _set_runtime(self, val: GT) -> NoReturn:
        ...

    def __iter__(self) -> NoReturn:
        ...

    def __len__(self) -> int:
        '''returns init size, if specifyed, or actual size of array.
        for KSP built-in function use built-in func'''
        ...

    def iter_runtime(self) -> Iterator[Union[Type[GT],
                                             Tuple[Type[GT], ...]]]:
        '''returns __getitem__ on each index'''
        ...

    def iter_runtime_fast(self) -> Iterator[Optional[GT]]:
        '''returns pure objects, stored in seq at each idx'''
        ...

    def _generate_executable(self) -> NoReturn:
        ...

    def _sort(self, direction: int) -> None:
        ...


@overload
def get_val(*args: Union[int,
                         KspIntVar,
                         AstOperator[Union[int, KspIntVar]]
                         ]) -> Union[str, int]:
    ...


@overload
def get_val(*args: Union[str,
                         KspStrVar,
                         AstAddString
                         ]) -> str:
    ...


@overload
def get_val(*args: Union[float,
                         KspRealVar,
                         AstOperator[Union[float, KspRealVar]]
                         ]) -> Union[str, float]:
    ...


def get_string_repr(*args: GT) -> str:
    ...


@overload
def get_runtime(*args: Union[int,
                             KspIntVar,
                             AstOperator[Union[int, KspIntVar]]
                             ]) -> int:
    ...


@overload
def get_runtime(*args: Union[str,
                             KspStrVar,
                             AstAddString
                             ]) -> str:
    ...


@overload
def get_runtime(*args: Union[float,
                             KspRealVar,
                             AstOperator[Union[float, KspRealVar]]
                             ]) -> float:
    ...
