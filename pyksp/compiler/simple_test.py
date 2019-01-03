from abstract import KspObject
from abstract import KSP
from abstract import Output
# from abstract import KspGeneric
# from abstract import KspMeta

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
# from typing import TYPE_CHECKING
from typing_extensions import Protocol
from typing_extensions import runtime

from abc import ABCMeta


T = TypeVar('T')
# TA = TypeVar('TA')
T_co = TypeVar('T_co', covariant=True)
ST = TypeVar('ST', bound=str)
IT = TypeVar('IT', bound=int)
FT = TypeVar('FT', bound=float)
NT = Union[T, int, float]
VT = Union[T, int, float, str]
ValidTypesT = (int, str, float)


@runtime
class ValidKspVar(Protocol[T]):
    _value: T

    def _set_compiled(self, value: 'ValidKspVar[T]') -> None:
        ...

    def get_compiled(self) -> str:
        ...

    def get_runtime(self) -> T:
        ...

    def set_runtime(self, value: T) -> None:
        ...


@runtime
class ValidAstObject(Protocol[T_co]):

    def expand(self) -> str:
        ...

    def get_value(self) -> T_co:
        ...


class Var(Generic[T]):

    def __init__(self, value: T, name: str='testname') -> None:
        self._value: T = value
        self._name = name

    def _set_compiled(self, value: ValidKspVar[T]) -> None:
        ...

    def get_compiled(self) -> str:
        return self._name

    def set_runtime(self, value: Union[T,
                                       ValidKspVar[T],
                                       ValidAstObject[T]]) -> None:
        if isinstance(value, ValidKspVar):
            value = value.get_runtime()
        if isinstance(value, ValidAstObject):
            value = value.get_value()
        self._value = value
        return

    def get_runtime(self) -> T:
        return self._value


x = 3
y = 2.5
x = y

a = Var(5)
b = Var(7.5)
c = Var(2)
print(type(a))
print(type(b))

a.set_runtime(b)
# print(a.get_runtime())
a.set_runtime(x)
a.set_runtime(y)
b.set_runtime(x)
b.set_runtime(a)


class AstBase(Generic[T]):
    ...


class AstAssign(AstBase, Generic[T]):
    '''special top-level Ast class for making assigements.
    Has not method get_value()
    '''

    def __init__(self, to_arg: ValidKspVar[T],
                 from_arg: Union[ValidKspVar[T],
                                 ValidAstObject[T], T]) -> None:
        self._to_arg = to_arg.get_compiled()
        if isinstance(from_arg, AstAssign):
            raise TypeError('AstAssign is root, can not be added')
        if isinstance(from_arg, ValidAstObject):
            self._from_arg = from_arg.expand()
        elif isinstance(from_arg, ValidKspVar):
            self._from_arg = from_arg.get_compiled()
        else:
            self._from_arg = str(from_arg)
        # raise TypeError('can assign only instances of: ' +
        #                 f'{(KspVar, str, int, float, AstBase)}')

    def expand(self) -> str:
        '''expand AstObject to string representation "a := b"'''
        return f'{self._to_arg} := {self._from_arg}'

    def get_value(self) -> NoReturn:
        raise NotImplementedError('AstAssign can not return value')


class AstAssignInt(AstAssign[IT]):

    def __init__(self, to_arg: ValidKspVar[IT],
                 from_arg: Union[ValidKspVar[IT],
                                 ValidAstObject[IT], IT]) -> None:
        super().__init__(to_arg, from_arg)


class AstAssignStr(AstAssign[ST]):

    def __init__(self, to_arg: ValidKspVar[ST],
                 from_arg: Union[ValidKspVar[ST],
                                 ValidAstObject[ST], ST]) -> None:
        super().__init__(to_arg, from_arg)


class AstAssignFloat(AstAssign[FT]):

    def __init__(self, to_arg: ValidKspVar[FT],
                 from_arg: Union[ValidKspVar[FT],
                                 ValidAstObject[FT], FT]) -> None:
        if isinstance(from_arg, int):
            from_arg = float(from_arg)      # type: ignore
        super().__init__(to_arg, from_arg)  # type: ignore


assgn_a = AstAssignInt(a, 1)
print(assgn_a.expand())
assgn_b = AstAssignFloat(b, 2)
print(assgn_b.expand())
assgn_c = AstAssignFloat(a, 2.2)
print(assgn_c.expand())

test_a: AstAssign[int] = assgn_a
test_a = assgn_b

test_b: AstAssign[float] = assgn_b
test_b = assgn_a
