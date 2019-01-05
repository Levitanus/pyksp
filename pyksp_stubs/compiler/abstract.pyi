from abc import ABCMeta
from abc import abstractmethod
import hashlib

from typing import List
from typing import Any
from typing import Union
from typing import Callable
from typing import Tuple
from typing import NoReturn
from typing import Optional


class SingletonMeta(ABCMeta):
    '''Singleton metaclass'''
    def __init__(cls, *args: Any, **kw: Any) -> None:
        cls.instance = None

    def __call__(cls, *args: Any, **kw: Any) -> 'SingletonMeta':
        if cls.instance is None:
            cls.instance = \
                super(SingletonMeta, cls).__call__(*args, **kw)
        return cls.instance  # type: ignore


class KspBoolProp:
    '''class property, initialized at False and accepts only bool'''

    def __init__(self) -> None:
        ...

    def __get__(self, obj: object, cls: type) -> bool:
        ...

    def __set__(self, obj: object, val: bool) -> None:
        ...

    def __delete__(self) -> NoReturn:
        ...


class KSP(metaclass=ABCMeta):
    '''Base abstract class for all compiler classes'''
    __is_compiled: bool = ...
    __is_bool: bool = ...
    __in_init: bool = ...
    __callback: Optional[object] = ...
    indents: bool = ...
    docs: bool = ...

    @staticmethod
    def is_compiled() -> bool:
        '''check state (changes returns of KSP objects)'''
        ...

    @staticmethod
    def set_callback(obj: Any) -> None:
        '''set callback to be counted by built-ins'''
        ...

    @staticmethod
    def callback() -> Any:
        '''retrieve current callback'''
        ...

    @staticmethod
    def set_compiled(val: bool) -> None:
        '''set state (changes returns of KSP objects)'''
        ...

    @staticmethod
    def is_bool() -> bool:
        '''check state (for usage in if/else select/case blocks)'''
        ...

    @staticmethod
    def set_bool(val: bool) -> None:
        '''set bool state (for usage in if/else select/case blocks)'''
        ...

    @staticmethod
    def in_init(val: Optional[bool]=None) -> Optional[bool]:
        '''val is optional. Within kwarg "val" sets state to it
        without - checks'''
        ...

    @staticmethod
    def refresh() -> None:
        '''sets KSP variables to default'''
        ...


class INameLocal(KSP):
    '''Object name interface.'''

    script_prefix: str = ...

    def __init__(self, name: str,
                 prefix: str='',
                 postfix: str='') -> None:
        ...

    def __call__(self) -> str:
        ...

    @staticmethod
    def refresh() -> None:
        ...


class IName(INameLocal):
    '''name can be compacted by default. For preserving use
    preserve=True
    prefix and postfix are always preserved and placed at sides.
    '''

    __is_compact: bool = ...
    __names: List[str] = ...
    __scope: List[str] = ...

    @staticmethod
    def is_compact() -> bool:
        '''check if names are hashed'''
        ...

    @staticmethod
    def set_compact(val: bool) -> None:
        '''at True hashes names to 5-letter'''
        ...

    def __init__(self, name: str, prefix: str=..., postfix: str=...,
                 preserve: bool=...) -> None:
        ...

    @staticmethod
    def get_compact_name(name: str) -> str:
        '''hashing func'''
        ...

    @staticmethod
    def scope(name: str=...) -> None:
        ...

    @property
    def full(self) -> str:
        ...

    @staticmethod
    def refresh() -> None:
        ...


class KspObject(KSP):
    '''Base abstract class for all objects can be
    translated to code'''

    comments: KspBoolProp = ...
    _instances: List['KspObject'] = ...

    @property
    def has_init(self) -> bool:
        '''True if has to return init block'''
        ...

    @property
    def is_local(self) -> bool:
        '''True if has not return init and executable block'''
        ...

    @property
    def has_executable(self) -> bool:
        '''True if has to return executable block'''
        ...

    @staticmethod
    def instances() -> List['KspObject']:
        ...

    @abstractmethod
    def __init__(self, name: str,
                 name_prefix: str=...,
                 name_postfix: str=...,
                 preserve_name: bool=...,
                 has_init: bool=...,
                 is_local: bool=...,
                 has_executable: bool=...) -> None:
        ...

    @abstractmethod
    def _generate_init(self) -> List[str]:
        pass

    @abstractmethod
    def _generate_executable(self) -> List[str]:
        pass

    @staticmethod
    def generate_all_inits() -> List[str]:
        '''return init lines for every instance marked to
        generate init block'''
        ...

    @staticmethod
    def generate_all_executables() -> List[str]:
        '''return init lines for every instance marked to
        generate executable block'''
        ...

    @staticmethod
    def refresh() -> None:
        '''clear all instances'''
        ...


class Output(metaclass=SingletonMeta):
    '''Singleton interface for managing pure code'''

    __default: List[str]
    callable_on_put: Optional[Callable[..., Any]]
    __output: List[str]
    __indent: int

    class IsSetError(Exception):
        def __init__(self, extra: str=...) -> None:
            ...

    class IndentError(Exception):
        def __init__(self, extra: str=...) -> None:
            ...

    blocked = KspBoolProp()

    def indent(self) -> None:
        """increase indentation level to be used within compilation"""
        ...

    def unindent(self) -> None:
        """increase indentation level to be used within compilation"""
        ...

    def __init__(self) -> None:
        ...

    def set(self, obj: List[str]) -> None:
        '''set list for code from internal to external
        (callback body, for example)
        raises self.IsSetError if already set
        (e.g. can output only to top level)'''
        ...

    def release(self) -> None:
        '''set output to internal list'''
        ...

    def get(self) -> List[str]:
        '''get all items of current list'''
        ...

    def put(self, data: str) -> None:
        '''put item in list and perform actions based on flags:
        exception_on_put - raises exception, if not None
        callable_on_put - executes callable once at put
        and set it to None
        '''
        ...

    def pop(self) -> str:
        '''pop the last index from list'''
        ...

    def refresh(self) -> None:
        '''erase all data from internal list and set defaults'''
        ...
