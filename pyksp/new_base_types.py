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
from .new_abstract import AstString
from .new_abstract import AstBase
from .new_abstract import HasInit

from .new_abstract import KSP

T = TypeVar('T')
KT = TypeVar('KT', int, float, str)
KVT = TypeVar('KVT', bound='KspVar')
NT = TypeVar('NT', int, float)
# AT = TypeVar('AT', bound='KspVar[KT]')

ATU = Union['KspVar[KT]', 'AstBase[KT]', KT]
# STU = Union['KspVar[str]', 'AstConcatStr', ]


def get_value(value: ATU[KT]) -> KT:
    if isinstance(value, (int, str, float)):
        return value
    if isinstance(value, KspVar):
        return value._value
    if isinstance(value, AstBase):
        return value.get_value()
    raise TypeError(f"Can't infer type of {value}")


def get_compiled(value: ATU[KT]) -> str:
    if isinstance(value, (int, float)):
        return f'{value}'
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, KspVar):
        return value.name()
    if isinstance(value, AstBase):
        return value.expand()
    raise TypeError(f"Can't infer type of {value}")


class KspVar(KspObject, HasInit, Generic[KT]):
    names_count: int = 0

    class Persist:
        """Class for mark persistence of variable.

        can be:
        KspVar.not_persistent
        KspVar.persistent
        KspVar.inst_persistent"""

        def __init__(self, line: str='') -> None:
            self.line = line

    not_persistent: ClassVar[Persist] = Persist()
    persistent: ClassVar[Persist] = Persist('make_persistent')
    inst_persistent: ClassVar[Persist] = Persist('make_instr_persistent')
    read_persistent: ClassVar[Persist] = Persist('make_persistent')

    def __init__(self,
                 value: KT,
                 name: str='',
                 persist: Persist=not_persistent,
                 preserve_name: bool=False,
                 *, local: bool=False) -> None:
        if local:
            assert name
            sup_name = NameBase(name)
            has_init = False
        else:
            if not name:
                name = f'Var{KspVar.names_count}'
                KspVar.names_count += 1
            sup_name = NameVar(name, preserve=preserve_name)
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
        self._init_val: KT = value
        self._persist: KspVar.Persist = persist

    @abstractmethod
    def get_decl_line(self) -> List[str]:
        ...

    def generate_init(self) -> List[str]:
        out = self.get_decl_line()
        if self._persist is not self.not_persistent:
            out.append(f'{self._persist.line}({self.name()})')
        if self._persist is self.read_persistent:
            out.append(f'read_persistent_var({self.name()})')

        return out

    @property
    def val(self) -> KT:
        return self._value

    def read(self) -> None:
        self._persist = self.persistent
        out = self.get_out()
        out.put_immediatly(AstString(f'read_persistent_var({self.name()})'))

    @abstractmethod
    def __ilshift__(self: KVT, other: ATU) -> KVT:
        ...

    def copy(self: KVT, name: str, prefix: str, postfix: str) -> KVT:
        obj = self.__class__(self._value, name=name, local=True)
        obj.name.prefix = prefix
        obj.name.postfix = postfix
        return obj


class Str(KspVar[str]):

    def __ilshift__(self, other: ATU) -> 'Str':
        value = get_value(other)
        if not isinstance(value, str):
            value = f'{value}'
        name = self.name.name
        prefix = self.name.prefix
        postfix = self.name.postfix
        if isinstance(other, Str):
            ret_obj = other.copy(name, prefix, postfix)
            ret_obj._value = value
        else:
            ret_obj = Str(value, name, local=True)
            ret_obj.name.prefix = prefix
            ret_obj.name.postfix = postfix

        otpt = self.get_out()
        otpt.put_immediatly(AstAssign(self, other))

        return ret_obj

    def get_decl_line(self) -> List[str]:
        out = [f'declare {self.name()}']
        if self._init_val:
            out.append(f'{self.name()} := {self._init_val}')
        return out


class Num(KspVar[NT]):

    def __ilshift__(self, other: ATU[NT]) -> 'Num[NT]':
        if isinstance(other, int) and issubclass(self._ref_type, float):
            other = float(other)  # type: ignore
        value = get_value(other)
        assert isinstance(value, self._ref_type), \
            f'assigned to a value of wrong type: {value}'
        name = self.name.name
        prefix = self.name.prefix
        postfix = self.name.postfix
        if isinstance(other, Num):
            ret_obj = other.copy(name, prefix, postfix)
            ret_obj._value = value
        else:
            ret_obj = Num(value, name, local=True)
            ret_obj.name.prefix = prefix
            ret_obj.name.postfix = postfix

        otpt = self.get_out()
        otpt.put_immediatly(AstAssign(self, other))

        return ret_obj

    def get_decl_line(self) -> List[str]:
        value = ''
        if self._init_val:
            value = f' := {self._init_val}'
        out = [f'declare {self.name()}{value}']
        return out


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
        raise self.NullError


out = KSP.new_out()
a = Str('3')
b = Num(4, name='b', local=True)
c = Num(5)
print(b.name())
b <<= c
print(b, b.val, b.name())
b <<= 15
a <<= 3

d = Num(4.1, 'd')
# reveal_type(d)
d <<= 3
print(d.val)
# reveal_type(d)
# b <<= 3.1
# d <<= b
d <<= d

print(out.get())
