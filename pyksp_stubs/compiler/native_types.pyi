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

from base_types import IT
from base_types import RT
from base_types import ST
from base_types import ITU
from base_types import RTU
from base_types import ValidAstInput as STU

from base_types import KspIntVar
from base_types import KspStrVar
from base_types import KspRealVar
from base_types import KspArray


from base_types import AstOperator
from base_types import AstAddString

from abstract import Output
from abstract import SingletonMeta


class kInt(KspIntVar):
    '''See module doc'''
    warning_types: Union[KspStrVar, KspRealVar, str, float] = ...
    names_count: int = ...
    __init_val: int

    def __init__(self,
                 value: ITU=...,
                 name: str=...,
                 preserve: bool=...,
                 is_local: bool=...,
                 persist: bool=...) -> None:
        ...

    def _generate_init(self) -> List[str]:
        ...

    def _get_compiled(self) -> str:
        ...

    def _get_runtime(self) -> int:
        ...

    def _set_runtime(self, other: int) -> None:
        ...

    def inc(self) -> None:
        ...

    def dec(self) -> None:
        ...


class kReal(KspRealVar):
    '''See module doc'''
    warning_types: Union[KspStrVar, KspIntVar, str, int] = ...
    names_count: int = ...
    __init_val: float

    def __init__(self,
                 value: RTU=...,
                 name: str=...,
                 preserve: bool=...,
                 is_local: bool=...,
                 persist: bool=...) -> None:
        ...

    def _generate_init(self) -> List[str]:
        ...

    def _get_compiled(self) -> str:
        ...

    def _get_runtime(self) -> float:
        ...

    def _set_runtime(self, other: float) -> None:
        ...


class kStr(KspStrVar):
    '''See module doc'''
    warning_types: Union[KspIntVar, KspRealVar, int, float] = ...
    names_count: int = ...
    __init_val: str

    def __init__(self,
                 value: STU=...,
                 name: str=...,
                 preserve: bool=...,
                 is_local: bool=...,
                 persist: bool=...) -> None:
        ...

    def _generate_init(self) -> List[str]:
        ...

    def _get_compiled(self) -> str:
        ...

    def _get_runtime(self) -> str:
        ...

    def _set_runtime(self, other: str) -> None:
        ...


class kArrInt(KspArray):
    '''See module doc'''
    names_count: int = ...

    def __init__(self,
                 sequence: Optional[List[Optional[IT]]]=...,
                 name: str=...,
                 size: int=...,
                 preserve: bool=...,
                 persist: bool=...,
                 is_local: bool=...) -> None:
        ...

    def _get_compiled(self) -> str:
        ...

    def _get_runtime(self) -> List[Optional[IT]]:
        ...

    def _generate_init(self) -> List[str]:
        ...


class kArrReal(KspArray):
    '''See module doc'''
    names_count: int = ...

    def __init__(self,
                 sequence: Optional[List[Optional[RT]]]=...,
                 name: str=...,
                 size: int=...,
                 preserve: bool=...,
                 persist: bool=...,
                 is_local: bool=...) -> None:
        ...

    def _get_compiled(self) -> str:
        ...

    def _get_runtime(self) -> List[Optional[RT]]:
        ...

    def _generate_init(self) -> List[str]:
        ...


class kArrStr(KspArray):
    '''See module doc'''
    names_count: int = ...

    def __init__(self,
                 sequence: Optional[List[Optional[ST]]]=...,
                 name: str=...,
                 size: int=...,
                 preserve: bool=...,
                 persist: bool=...,
                 is_local: bool=...) -> None:
        ...

    def _get_compiled(self) -> str:
        ...

    def _get_runtime(self) -> List[Optional[ST]]:
        ...

    def _generate_init(self) -> List[str]:
        ...


def refresh_names_count() -> None:
    ...


class kVar:
    '''returns KSP native var at construction or with assignement via
    <<= operator.
    arguments: (value=None, name=None, size=None,
                preserve=False, persist=False)
        if value, ready object is returned
        if not, object has to be initialized via <<= operator

    if init_value is:
        int, kInt -> kInt
        str, kStr -> kStr
        float, kReal -> kReal
        list -> kArr, depends on first item type
    '''
    names_count = 0

    def __new__(cls, value=None, name=None, size=None,
                preserve=False, persist=False):
        if not name:
            name = f'kVar{kVar.names_count}'
            kVar.names_count += 1
        if not value:
            obj = super(kVar, cls).__new__(cls)
            d = obj.__dict__
            d['name'] = name
            d['size'] = size
            d['preserve'] = preserve
            d['persist'] = persist
            return obj
        if isinstance(value, (int, KspIntVar)):
            return kInt(value=value, name=name,
                        preserve=preserve, persist=persist)
        if isinstance(value, (str, KspStrVar)):
            return kStr(value=value, name=name,
                        preserve=preserve, persist=persist)
        if isinstance(value, (float, KspRealVar)):
            return kReal(value=value, name=name,
                         preserve=preserve, persist=persist)
        if isinstance(value, list):
            if isinstance(value[0], (int, KspIntVar)):
                return kArrInt(value=value, name=name,
                               preserve=preserve, persist=persist,
                               size=size)
            if isinstance(value[0], (str, KspStrVar)):
                return kArrStr(value=value, name=name,
                               preserve=preserve, persist=persist,
                               size=size)
            if isinstance(value[0], (float, KspRealVar)):
                return kArrReal(value=value, name=name,
                                preserve=preserve, persist=persist,
                                size=size)
        raise TypeError('can be initialized only with:%s' %
                        (int, str, float, kInt, kStr, kReal, list))

    def __ilshift__(self, value):
        if isinstance(value, (int, KspIntVar)):
            if self.size:
                raise TypeError('for arrays initialization use list')
            return kInt(value=value, name=self.name,
                        preserve=self.preserve, persist=self.persist)
        if isinstance(value, (str, KspStrVar)):
            if self.size:
                raise TypeError('for arrays initialization use list')
            return kStr(value=value, name=self.name,
                        preserve=self.preserve, persist=self.persist)
        if isinstance(value, (float, KspRealVar)):
            if self.size:
                raise TypeError('for arrays initialization use list')
            return kReal(value=value, name=self.name,
                         preserve=self.preserve, persist=self.persist)
        if isinstance(value, list):
            if isinstance(value[0], (int, KspIntVar)):
                return kArrInt(sequence=value, name=self.name,
                               preserve=self.preserve,
                               persist=self.persist,
                               size=self.size)
            if isinstance(value[0], (str, KspStrVar)):
                return kArrStr(sequence=value, name=self.name,
                               preserve=self.preserve,
                               persist=self.persist,
                               size=self.size)
            if isinstance(value[0], (float, KspRealVar)):
                return kArrReal(sequence=value, name=self.name,
                                preserve=self.preserve,
                                persist=self.persist,
                                size=self.size)
        raise TypeError('can be initialized only with:%s' %
                        (int, str, float, kInt, kStr, kReal, list))

#


class kNone(kInt, metaclass=SingletonMeta):
    '''used as None value for KSP objects
    currently always returns -1, but still can be
    used as comparisson to kNone() :)
    '''

    def __init__(self):
        super().__init__(value=-1, name='None',
                         preserve=False, is_local=True)

    def _get_compiled(self):
        return self._value

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        raise NotImplementedError

    def _set_compiled(self, other):
        raise NotImplementedError

    def inc(self):
        raise NotImplementedError

    def dec(self):
        raise NotImplementedError


class kFalse(kInt):

    def __init__(self):
        super().__init__(value=0, name='None',
                         preserve=False, is_local=True)

    def _get_compiled(self):
        return self._value

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        raise NotImplementedError

    def _set_compiled(self, other):
        raise NotImplementedError

    def inc(self):
        raise NotImplementedError

    def dec(self):
        raise NotImplementedError


class kTrue(kInt):

    def __init__(self):
        super().__init__(value=1, name='None',
                         preserve=False, is_local=True)

    def _get_compiled(self):
        return self._value

    def _get_runtime(self):
        return self._value

    def _set_runtime(self, other):
        raise NotImplementedError

    def _set_compiled(self, other):
        raise NotImplementedError

    def inc(self):
        raise NotImplementedError

    def dec(self):
        raise NotImplementedError

    def __eq__(self, other):
        return 0 < other
