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
from typing_extensions import Protocol


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


S = TypeVar('S')
GT = TypeVar('GT', Union['KspIntVar', int],
             Union['KspRealVar', float], Union['KspStrVar', str])
ST = TypeVar('ST', str, float)
NT = TypeVar('NT', Union['KspIntVar', int],
             Union['KspRealVar', float])
IT = TypeVar('IT', bound=Union['KspIntVar', int])
RT = TypeVar('RT', bound=Union['KspRealVar', float])

ITU = Union[int, 'KspIntVar']
RTU = Union[float, 'KspRealVar']
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


class AstOperator(AstBase, Generic[NT], metaclass=ABCMeta):
    '''Base abstract class for all operators.'''
    _args: List[NT]
    priority: int

    def __init__(self, *args: NT) -> None:
        ...

    def unpack_args(self, *args: Sequence[NT]) -> ST:
        '''gets values of KspVar objects and expands AstBase objects
        keeps str, int and float objects untouched
        returns tuple of args or only arg, if it was alone
        '''
        ...

    def unary(self, string: str, val: NT) -> str:
        '''returns f"{string}{val}"'''
        ...

    def standart(self, string: str,
                 val1: NT,
                 val2: NT) -> str:
        '''returns f"{val1} {string} {val2}"'''
        ...

    def bracket_unary(self, string: str,
                      val: NT) -> str:
        '''returns f"{string}({val})"'''
        ...

    def bracket_double(self, string: str,
                       val1: NT,
                       val2: NT) -> str:
        '''returns f"{string}({val1}, {val2})"'''
        ...

    def get_value_proxy(self, func: Callable[[NT], ST]) -> ST:
        '''use via super
        accepts func (lambda?) and passes init args to it.
        args are expanded via:
        _get_runtime() for KspVar objects
        get_value() for AstBase objects'''
        ...

    def __neg__(self) -> AstNeg[NT]:
        ...

    def __invert__(self) -> AstNot[NT]:
        ...

    def __add__(self, other: NT) -> AstAdd[NT]:
        ...

    def __radd__(self, other: NT) -> AstAdd[NT]:  # type: ignore
        ...

    def __iadd__(self, other: NT) -> NoReturn:
        ...

    def __sub__(self, other: NT) -> AstSub[NT]:
        ...

    def __rsub__(self, other: NT) -> AstSub[NT]:  # type: ignore
        ...

    def __isub__(self, other: NT) -> NoReturn:
        ...

    def __mul__(self, other: NT) -> AstMul[NT]:
        ...

    def __rmul__(self, other: NT) -> AstMul[NT]:  # type: ignore
        ...

    def __imul__(self, other: NT) -> NoReturn:
        ...

    def __truediv__(self, other: NT) -> AstDiv[NT]:
        ...

    def __rtruediv__(self, other: NT) -> AstDiv[NT]:  # type: ignore
        ...

    def __itruediv__(self, other: NT) -> NoReturn:
        ...

    def __floordiv__(self, other: NT) -> NoReturn:
        ...

    def __rfloordiv__(self, other: NT) -> NoReturn:  # type: ignore
        ...

    def __ifloordiv__(self, other: NT) -> NoReturn:
        ...

    def __mod__(self, other: NT) -> AstMod[NT]:
        ...

    def __rmod__(self, other: NT) -> AstMod[NT]:  # type: ignore
        ...

    def __imod__(self, other: NT) -> NoReturn:
        ...

    def __pow__(self, other: NT) -> AstPow[NT]:
        ...

    def __rpow__(self, other: NT) -> AstPow[NT]:  # type: ignore
        ...

    def __ipow__(self, other: NT) -> NoReturn:
        ...

    def __and__(self, other: NT) -> Union[AstLogAnd[NT], AstBinAnd[NT]]:
        ...

    def __rand__(self, other: NT)-> Union[AstLogAnd[NT],   # type: ignore
                                          AstBinAnd[NT]]:  # type: ignore
        ...

    def __or__(self, other: NT) -> Union[AstLogOr[NT], AstBinOr[NT]]:
        ...

    def __ror__(self, other: NT)-> Union[AstLogOr[NT],   # type: ignore
                                         AstBinOr[NT]]:  # type: ignore
        ...

    def __eq__(self, other: NT) -> AstEq[NT]:  # type: ignore
        ...

    def __ne__(self, other: NT) -> AstNe[NT]:  # type: ignore
        ...

    def __lt__(self, other: NT) -> AstLt[NT]:  # type: ignore
        ...

    def __gt__(self, other: NT) -> AstGt[NT]:  # type: ignore
        ...

    def __le__(self, other: NT) -> AstLe[NT]:  # type: ignore
        ...

    def __ge__(self, other: NT) -> AstGe[NT]:  # type: ignore
        ...

    def abs(self) -> AstAbs[NT]:
        ...


class AstNeg(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> ST:
        ...


class AstNot(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstAdd(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstSub(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstMul(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstDiv(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstMod(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstPow(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstLogAnd(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstBinAnd(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstLogOr(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstBinOr(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstEq(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstNe(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstLt(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstGt(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstLe(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstGe(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
        ...


class AstAbs(AstOperator, Generic[NT]):

    def expand(self) -> str:
        ...

    def get_value(self) -> NT:
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

    def __ilshift__(self, other: GT) -> 'KspVar[GT]':
        '''under compilation calls self._set_compiled
        otherwise calls self._set_runtime

        returns self'''
        ...

    def __rlshift__(self, other: GT) -> Union[str, ST]:
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

    def __radd__(self, other: GT) -> Union[AstAddString,  # type: ignore
                                           str]:  # type: ignore
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


class KspNumeric(KspVar[NT], Generic[NT]):
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

        def __init__(self, val: NT) -> None:  # type: ignore
            ...

    def _generate_executable(self) -> NoReturn:
        ...

    def _warn_other(self, value: Any) -> None:
        ...

    def abs(self) -> Union[AstAbs[NT], ST]:
        ...

    @abstractmethod
    def __truediv__(self, other: NT) -> Union[AstDiv[NT], NT]:
        pass

    @abstractmethod
    def __rtruediv__(self,                                 # type: ignore
                     other: NT) -> Union[AstDiv[NT], NT]:  # type: ignore
        pass

    @abstractmethod
    def __itruediv__(self, other: NT) -> Union[AstDiv[NT], NT]:
        pass

    @abstractmethod
    def __floordiv__(self, other: NT) -> NoReturn:
        ...

    @abstractmethod
    def __rfloordiv__(self, other: NT) -> NoReturn:  # type: ignore
        ...

    @abstractmethod
    def __ifloordiv__(self, other: NT) -> NoReturn:
        ...

    def _expand_other(self, other: NT) -> Union[str, int, float]:
        '''returns other, expanded via val property if is
        instance of KspVar'''
        ...

    def __neg__(self) -> Union[AstNeg[NT], NT]:
        ...

    def __invert__(self) -> Union[AstNot[NT], NT]:
        ...

    def __add__(self, other: NT) -> Union[AstAdd[NT], NT]:
        ...

    def __radd__(self,                                 # type: ignore
                 other: NT) -> Union[AstAdd[NT], NT]:  # type: ignore
        ...

    def __iadd__(self, other: NT) -> 'KspNumeric[NT]':
        ...

    def __sub__(self, other: NT) -> Union[AstSub[NT], NT]:
        ...

    def __rsub__(self,                                 # type: ignore
                 other: NT) -> Union[AstSub[NT], NT]:  # type: ignore
        ...

    def __isub__(self, other: NT) -> 'KspNumeric[NT]':
        ...

    def __mul__(self, other: NT) -> Union[AstMul[NT], NT]:
        ...

    def __rmul__(self,                                 # type: ignore
                 other: NT) -> Union[AstMul[NT], NT]:  # type: ignore
        ...

    def __imul__(self, other: NT) -> 'KspNumeric[NT]':
        ...

    def __and__(self, other: NT) -> Union[
            Union[NT, AstBinAnd[NT]],
            Union[bool, AstLogAnd[NT]]]:
        ...

    def __rand__(self, other: NT) -> Union[  # type: ignore
            Union[NT, AstBinAnd[NT]],
            Union[bool, AstLogAnd[NT]]]:
        ...

    def __iand__(self, other: NT) -> NoReturn:
        ...

    def __or__(self, other: NT) -> Union[  # type: ignore
            Union[NT, AstBinOr[NT]],
            Union[bool, AstLogOr[NT]]]:
        ...

    def __ror__(self, other: NT) -> Union[  # type: ignore
            Union[NT, AstBinOr[NT]],
            Union[bool, AstLogOr[NT]]]:
        ...

    def __ior__(self, other: NT) -> NoReturn:
        raise NotImplementedError

    def __eq__(self, other: NT) -> Union[bool, AstEq[NT]]:  # type: ignore
        ...

    def __ne__(self, other: NT) -> Union[bool, AstNe[NT]]:  # type: ignore
        ...

    def __lt__(self, other: NT) -> Union[bool, AstLt[NT]]:  # type: ignore
        ...

    def __gt__(self, other: NT) -> Union[bool, AstGt[NT]]:  # type: ignore
        ...

    def __le__(self, other: NT) -> Union[bool, AstLe[NT]]:  # type: ignore
        ...

    def __ge__(self, other: NT) -> Union[bool, AstGe[NT]]:  # type: ignore
        ...


class KspIntVar(KspNumeric[ITU], metaclass=ABCMeta):

    def __truediv__(self, other: ITU) -> Union[AstDiv[ITU], ITU]:
        ...

    def __rtruediv__(self, other: ITU) -> Union[AstDiv[ITU], ITU]:
        ...

    def __itruediv__(self, other: ITU) -> Union[AstDiv[ITU], 'KspIntVar']:
        ...

    def __floordiv__(self, other: ITU) -> NoReturn:
        ...

    def __rfloordiv__(self, other: ITU) -> NoReturn:
        ...

    def __ifloordiv__(self, other: ITU) -> NoReturn:
        ...

    def __mod__(self, other: ITU) -> Union[AstMod[ITU], ITU]:
        ...

    def __rmod__(self, other: ITU) -> Union[AstMod[ITU], ITU]:
        ...


class KspRealVar(KspNumeric[RTU], metaclass=ABCMeta):
    def __truediv__(self, other: RTU) -> Union[AstDiv[RTU], RTU]:
        ...

    def __rtruediv__(self, other: RTU) -> Union[AstDiv[RTU], RTU]:
        ...

    def __itruediv__(self, other: RTU) -> Union[AstDiv[RTU],
                                                'KspRealVar']:
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

    def __ipow__(self, other: RTU) -> Union[AstPow[RTU],
                                            'KspRealVar']:
        ...

    def __and__(self, other: RTU) -> Union[RTU, AstBinAnd[RTU]]:
        ...

    def __rand__(self, other: RTU) -> Union[RTU, AstBinAnd[RTU]]:
        ...

    def __or__(self, other: RTU) -> Union[RTU, AstBinOr[RTU]]:
        ...

    def __ror__(self, other: RTU) -> Union[RTU, AstBinOr[RTU]]:
        ...


class KspArray(KspVar, Generic[GT], metaclass=ABCMeta):
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

    def __getitem__(self, idx: IT) -> KspVar[GT]:
        '''returns item_type (KspVar instance) local objects with
        value from squence and name of array index ("array[idx]")
        resource-unefficient. cashes object for later usage, but
        rewrites several methods for keeping index fresh
        For lite usage (just what puted in seq) use _getitem_fast(idx)
        '''
        ...

    def _getitem_full(self, idx: IT) -> KspVar[GT]:
        ...

    def _getitem_fast(self, idx: ITU) -> Optional[GT]:
        '''returns value from sequence (even None)
        at idx value (runtime representation)
        '''
        ...

    def __setitem__(self, idx: ITU, val: IT) -> None:
        '''calls self.set_at_idx(idx, val)'''
        ...

    def set_at_idx(self, idx: ITU, val: IT) -> None:
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
