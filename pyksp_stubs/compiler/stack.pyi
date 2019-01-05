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

from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal

from abstract import KSP
from base_types import KspArray
from base_types import KspVar
from base_types import KspIntVar
from base_types import KspRealVar
from base_types import KspStrVar

from conditions_loops import For


GT = TypeVar('GT', int, str, float, kInt, kReal, kStr)
IT = TypeVar('IT', int, kInt, KspIntVar)
RT = TypeVar('RT', float, kReal, KspRealVar)
ST = TypeVar('ST', str, kStr, KspStrVar)
ITU = Union[int, kInt, KspIntVar]
RTU = Union[float, kReal, KspRealVar]
STU = Union[str, kStr, KspStrVar]

StackFrameArrayValidValue = \
    TypeVar('StackFrameArrayValidValue', kInt, kStr, kReal)


class kLoc(KSP, Generic[GT]):
    '''Special class for being argument annotation of functions
    or variable to put in stack.
    if size > 1 stack will return StackFrameArray object
    with size of 1 will return item of stack array

    Use it if You want to have true local variable inside a function
    '''
    __size: int
    __type: Union[kInt, kStr, kReal]

    def __init__(self,
                 ref_type: GT,
                 size: int=...) -> None:
        ...

    @overload
    def __get_type(self, ref_type: ITU) -> Type[kInt]:
        ...

    @overload
    def __get_type(self, ref_type: STU) -> Type[kStr]:
        ...

    @overload
    def __get_type(self, ref_type: RTU) -> Type[kReal]:
        ...

    @property
    def _size(self) -> int:
        '''return size of kLoc'''
        ...

    @property
    def ref_type(self) -> Union[kInt, kStr, kReal]:
        '''returns kInt, kStr or kReal depends on init'''
        ...


class StackFrameArray(KspArray, Generic[GT]):
    '''wraps KspArray for being some sort of slice object
    has methods __getitem__ and __setitem__, using start_idx
    as shift and returns or assignes wrapped array item
    methods __len__ and iter_runtime are implemented
    methods append and extend are not
    '''
    __array: KspArray[GT] = ...
    __start_idx: int = ...
    __length: int = ...

    def __init__(self,
                 arr: KspArray[GT],
                 start_idx: int,
                 end_idx: int) -> None:
        ...

    def _get_compiled(self) -> NoReturn:
        ...

    def _get_runtime(self) -> NoReturn:
        ...

    def __getitem__(self, idx: IT) -> KspVar[GT]:
        ...

    def __setitem__(self, idx: IT,
                    val: StackFrameArrayValidValue) -> None:
        ...

    def iter_runtime(self) -> Iterator[StackFrameArrayValidValue]:
        '''returns generator object within range of availble indicies'''
        ...

    def __len__(self) -> int:
        ...


class StackFrame(KSP, Generic[GT]):
    '''assigns variables to arr in order of passing.
    kLoc objects become items of an array, or StackFrameArray objects
    depends on their size.
    '''
    __vars: List[StackFrameArray[GT]]
    __size: int

    def __init__(self,
                 arr: KspArray[GT],
                 variables: Iterable[Union[kLoc[GT], KspVar[GT]]],
                 start_idx: ITU) -> None:
        ...

    @property
    def vars(self) -> List[StackFrameArray[GT]]:
        '''returns tuple of array items and StackFrameArray objects
        frame contains'''
        ...

    @property
    def size(self) -> int:
        '''returns int of total length of all items in the frame'''
        ...


# SAAT = TypeVar('SAAT', kArrInt, kArrStr, kArrReal)


class Stack(KSP, Generic[GT]):
    '''Can hold KSP variables and objecets of types (int, str, float)
    can hold only one type of objects
    '''

    depth: int = ...
    _arr: KspArray[GT] = ...
    _idx: kArrInt = ...
    _pointer: kInt = ...
    _frames: List[StackFrame[GT]] = list()
    _init_lines: List[str] = list()

    def __init__(self,
                 name: str,
                 ref_type: KspArray[GT],
                 size: int) -> None:
        ...

    def push(self,
             *variables: Union[kLoc[GT], KspVar[GT]])\
            -> List[StackFrameArray[GT]]:
        '''puts variables to stack and returns tuple of
        items of self array.
        '''
        ...

    def pop(self) -> StackFrame[GT]:
        '''deletes top frame of stack and returns it'''
        ...

    def is_empty(self) -> bool:
        '''returns True if empty'''
        ...


class MultiFrame:
    '''holds bolean attributes:
        is_int
        is_str
        is_real
    for track which stack has to be poped at pop method of MultiStack
    '''
    vars: List[StackFrameArray] = ...
    is_int: int = ...
    is_str: int = ...
    is_real: int = ...

    def __init__(self,
                 variables: List[StackFrameArray],
                 int_count: int,
                 str_count: int,
                 real_count: int) -> None:
        ...


ITLU = Union[kLoc[int], int, kInt, KspIntVar]
RTLU = Union[kLoc[float], float, kReal, KspRealVar]
STLU = Union[kLoc[str], str, kStr, KspStrVar]
MSVT = Union[kLoc[str], str, kStr, KspStrVar, kLoc[int], int,
             kInt, KspIntVar, kLoc[float], float, kReal, KspRealVar]


class MultiStack(KSP):
    '''the same as Stack, but can keep values of all KSP valid types'''

    _int: Stack[kInt]
    _str: Stack[kStr]
    _real: Stack[kReal]
    _frames: List[MultiFrame]
    _init_lines: List[str]

    def __init__(self, name: str, size: int) -> None:
        ...

    def push(self,
             *variables: MSVT)\
            -> List[StackFrameArray]:
        '''pushes variables and returns their connected stacks arrays
        items in order of pasting'''
        ...

    @overload
    @staticmethod
    def _get_var_type(var: ITLU) -> Type[int]:
        ...

    @overload
    @staticmethod
    def _get_var_type(var: STLU) -> Type[str]:
        ...

    @overload
    @staticmethod
    def _get_var_type(var: RTLU) -> Type[float]:
        ...

    def pop(self) -> List[StackFrameArray]:
        '''pop stacks, that have vars in the current frame and
        returns all frame variables'''
        ...

    def is_empty(self) -> bool:
        '''returns True if empty'''
        ...
