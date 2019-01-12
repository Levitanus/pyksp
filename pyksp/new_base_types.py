from typing import TypeVar
from typing import Type
from typing import List
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Any
from typing import NoReturn
from typing import Callable
from typing import ClassVar
from typing import Set
from typing import Sequence
from typing import cast
from typing import Union
from typing import NewType
from typing import Generic
from typing import overload
# from typing import Protocol
# from typing import runtime
from abc import ABCMeta
from abc import abstractmethod

if __name__ == '__main__':
    __name__ = 'pyksp.new_base_types'

from .new_abstract import KspObject
from .new_abstract import NameBase
from .new_abstract import NameVar
from .new_abstract import AstRoot
from .new_abstract import AstBase


KT = TypeVar('KT', int, float, str)
# AT = TypeVar('AT', bound='KspVar[KT]')

ATU = Union['KspVar[KT]', 'AstBase', KT]
# STU = Union['KspVar[str]', 'AstConcatStr', ]


class KspVar(KspObject, Generic[KT]):
    names_count: int = 0

    def __init__(self,
                 value: KT,
                 name: Optional[str]=None,
                 *, local: bool=False) -> None:
        if local:
            assert isinstance(name, str)
            sup_name = NameBase(name)
            has_init = False
        else:
            if not name:
                name = f'Var{KspVar.names_count}'
                KspVar.names_count += 1
            sup_name = NameVar(name)
            has_init = True
        super().__init__(sup_name, has_init=has_init)
        self._value: KT = value
        if isinstance(value, int):
            self.name.prefix = '$'
        elif isinstance(value, str):
            self.name.prefix = '@'
        elif isinstance(value, float):
            self.name.prefix = '~'
        else:
            raise TypeError(f"Can't infer type of value {value}")
        self._ref_type: Type[KT] = type(value)

    def __ilshift__(self, other: 'KspVar[KT]') -> 'KspVar[KT]':
        assert isinstance(other, KspVar), \
            f'has to be of type {(KspVar, self._ref_type)}'
        assert isinstance(other._value, self._ref_type)
        name = other.name.name
        prefix = other.name.prefix
        postfix = other.name.postfix
        ret_obj = self.copy(name=name, prefix=prefix, postfix=postfix)

        otpt = self.get_out()
        otpt.put_immediatly(AstAssign(other, self))

        return ret_obj

    def copy(self, name: str, prefix: str, postfix: str) -> 'KspVar[KT]':
        obj = KspVar(self._value, name=name)
        obj.name.prefix = prefix
        obj.name.postfix = postfix
        return obj


class AstAssign(AstRoot):

    def __init__(self, to_arg: 'KspVar', from_arg: ATU) -> None:
        self.to_arg: 'KspVar' = to_arg
        self.from_arg: ATU = from_arg

    def expand(self) -> str:
        to = self.to_arg.name()
        if isinstance(self.from_arg, (int, float)):
            from_str = f'{self.from_arg}'
        elif isinstance(self.from_arg, str):
            from_str = f'"{self.from_arg}"'
        elif isinstance(self.from_arg, KspVar):
            from_str = self.from_arg.name()
        elif isinstance(self.from_arg, AstBase):
            from_str = self.from_arg.expand()
        else:
            raise TypeError(f"Can't infer type of value {self.from_arg}")
        return f'{to} := {from_str}'

    def get_value(self) -> NoReturn:
        raise NotImplementedError


a = KspVar('3')
b = KspVar(4, name='b', local=True)
c = KspVar(4.0)
print(b.name())
