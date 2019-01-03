"""Base compiler classes, whicn aother system is based on."""
from abc import ABCMeta
from abc import abstractmethod
import hashlib

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
# from typing import GenericMeta
# from typing import Generic

T = TypeVar('T')


class KspMeta(ABCMeta):
    pass


class SingletonMeta(KspMeta):
    """Singleton metaclass."""

    def __call__(cls: Type[T], *args: Any, **kw: Any) -> T:
        """Return instance of class."""
        if not hasattr(cls, 'instance'):
            setattr(cls,
                    'instance',
                    super().__call__(*args, **kw))
        return getattr(cls, 'instance')


class KSP(metaclass=KspMeta):
    """Base abstract class for all compiler classes."""

    __is_compiled: bool = False
    __is_bool: bool = False
    __in_init: bool = True
    __callback: Optional[object] = None
    indents = False
    docs = False

    @staticmethod
    def is_compiled() -> bool:
        """Check state (changes returns of KSP objects)."""
        return KSP.__is_compiled

    @staticmethod
    def set_compiled(val: bool) -> None:
        """Set state (changes returns of KSP objects)."""
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__is_compiled = val

    @staticmethod
    def set_callback(obj: object) -> None:
        """Set callback to be counted by built-ins."""
        if obj is None:
            KSP.__callback = obj
            return
        if KSP.__callback is not None:
            raise RuntimeError(
                f'callback {KSP.__callback} is opened yet')
        KSP.__callback = obj

    @staticmethod
    def callback() -> Optional[object]:
        """Retrieve current callback.

        Return Callback object or None"""
        return KSP.__callback

    @staticmethod
    def is_bool() -> bool:
        """Check state (for usage in if/else select/case blocks)."""
        return KSP.__is_bool

    @staticmethod
    def set_bool(val: bool) -> None:
        """Set bool state (for usage in if/else select/case blocks)."""
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__is_bool = val

    @staticmethod
    def in_init(val: Optional[bool]=None) -> Optional[bool]:
        """Set or check if compiler is in init callback.

        val is optional. Within kwarg "val" sets state to it
        without - checks"""
        if val is None:
            return KSP.__in_init
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        KSP.__in_init = val
        return None

    @staticmethod
    def refresh() -> None:
        """Set KSP variables to defaults."""
        KSP.__is_compiled = False
        KSP.__is_bool = False
        KSP.__in_init = True
        KSP.indents = False
        KSP.docs = False


class INameLocal(KSP):
    """Object name interface.

    Example:
    class Test2:

        def __init__(self, name='myname'):
            self.name = INameLocal(name)
    prefix and postfix used in childs for preserving order of strings
    """

    script_prefix = ''

    def __init__(self, name: str, prefix: str='',
                 postfix: str='') -> None:
        """Object name interface."""
        self._name = name
        self._prefix = prefix
        self._postfix = postfix

    def __call__(self) -> str:
        """Return name."""
        return self._prefix + IName.script_prefix +\
            self._name + self._postfix

    @staticmethod
    def refresh() -> None:
        """Refresh script prefix."""
        IName.script_prefix = ''


class IName(INameLocal):
    """Name can be compacted by default.

    For preserving use
    preserve=True
    prefix and postfix are always preserved and placed at sides.
    """

    __is_compact: bool = False
    __names: List[str] = list()
    __scope: List[str] = ['']

    @staticmethod
    def is_compact() -> bool:
        """Check if names are hashed."""
        return IName.__is_compact

    @staticmethod
    def set_compact(val: bool) -> None:
        """Hash names to 5-letter if val is True."""
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        IName.__is_compact = val

    def __init__(self, name: str, prefix: str='',
                 postfix: str='',
                 preserve: bool=False) -> None:
        """Name can be compacted by default."""
        name = IName.__scope[-1] + name
        self._preserve = preserve
        self._full = name
        if not preserve and self.is_compact() is True:
            name = self.get_compact_name(name)
        else:
            name = name
        if name in IName.__names:
            raise NameError(f'name "{name}" exists')
        IName.__names.append(name)
        super().__init__(name=name,
                         prefix=prefix, postfix=postfix)

    @staticmethod
    def get_compact_name(name: str) -> str:
        """Hashing function."""
        symbols = 'abcdefghijklmnopqrstuvwxyz012345'
        hash = hashlib.new('sha1')
        hash.update(name.encode('utf-8'))
        compact = ''.join((symbols[ch & 0x1F] for ch
                           in hash.digest()[:5]))
        return compact

    @staticmethod
    def scope(name: str='') -> Optional[str]:
        """Wrap all new declarations within the last put scope.

        if name is not passed, the last scope is removed from list"""
        if not name:
            return IName.__scope.pop()
        IName.__scope.append(name)
        return None

    @property
    def full(self) -> str:
        """Return full name even if it was compacted."""
        return self._full

    @staticmethod
    def refresh() -> None:
        """Set all class variables to defaults."""
        INameLocal.refresh()
        IName.__names = list()
        IName.__is_compact = False


class KspObject(KSP):
    """Base abstract class for all objects can be translated to code."""

    comments: bool = False
    _instances: List['KspObject'] = list()

    @property
    def has_init(self) -> bool:
        """Return True if has to return init block."""
        return self._has_init

    @property
    def is_local(self) -> bool:
        """Return True if has not return init and executable block."""
        return self._is_local

    @staticmethod
    def instances() -> List['KspObject']:
        """Return list with all instances of KspObject."""
        return KspObject._instances

    @abstractmethod
    def __init__(self, name: str,
                 name_prefix: str='',
                 name_postfix: str='',
                 preserve_name: bool=False,
                 has_init: bool=True,
                 is_local: bool=False) -> None:
        """KSP object."""
        self._is_local = is_local
        if is_local:
            if has_init:
                raise AttributeError('can not have init within local')
            if preserve_name:
                raise AttributeError(
                    'local name is already preserved')
            self.name = INameLocal(name, name_prefix, name_postfix)
        else:
            self.name = IName(name, name_prefix, name_postfix,
                              preserve_name)
        self._has_init = has_init
        KspObject._instances.append(self)

    @abstractmethod
    def _generate_init(self) -> List[str]:
        pass

    @staticmethod
    def generate_all_inits() -> List[str]:
        """Return init lines for every instance.

        If instance marked as not having init it's _generate_init()
        method is not being executed"""
        out: List[str] = list()
        for inst in KspObject.instances():
            if not inst._has_init:
                continue
            inst_init = inst._generate_init()
            if inst_init is None:
                continue
            if isinstance(inst_init, str):
                raise TypeError('can not add string')
            out.extend(inst_init)
        return out

    @staticmethod
    def refresh() -> None:
        """Clear all instances."""
        KspObject._instances = list()


class Output(metaclass=SingletonMeta):
    """Singleton interface for managing pure code.

    self.indent():
        increase indentation level to be used at compilation
    self.unindent():
        decrease indentation. Raises self.IndentError if
        indent level is below 0.
    note: indentation depends on KSP.indents integer value

    self.set(obj: list):
        set list for code from internal to external
        (callback body, for example)
        raises self.IsSetError if already set
        (e.g. can output only to top level)
    self.release():
        releases if is set to list.

    self.put(data):
        put item in list and perform actions based on flags:
        exception_on_put - raises exception, if not None
        callable_on_put - executes callable once at put
        and set it to None
    self.get():
        get all items of current list
    self.refresh():
        erase all data from internal list and set defaults

    self.blocked:
        bool property for blocking put method.
    """

    class IsSetError(Exception):
        """Raises if Output set() is called while it is set already."""

        def __init__(self, extra: str='') -> None:
            """IsSetError."""
            super().__init__('Output is set yet. ' + extra)

    class IndentError(Exception):
        """Raises if indentation level goes below 0."""

        def __init__(self, extra: str='') -> None:
            """IndentError."""
            super().__init__(extra)

    def indent(self) -> None:
        """Increase indentation level to be used within compilation."""
        self.__indent += 1

    def unindent(self) -> None:
        """Increase indentation level to be used within compilation.

        Raises Output.IndentError if indent level is below 0"""
        self.__indent -= 1
        if self.__indent < 0:
            raise self.IndentError('indent level below 0')

    def __init__(self) -> None:
        """Singleton interface for managing pure code."""
        self.__default: List[str] = list()
        self.blocked: bool = False
        self.callable_on_put: Optional[Callable] = None
        self.exception_on_put: Optional[Exception] = None
        self.__output: List[str] = self.__default
        self.__indent: int = int()

    def set(self, obj: List[str]) -> None:
        """Set list for code from internal to external.

        (callback body, for example)
        raises self.IsSetError if already set
        (e.g. can output only to top level)"""
        if self.__output is not self.__default:
            raise self.IsSetError
        self.__output = obj

    def release(self) -> None:
        """Set output to internal list."""
        self.__output = self.__default

    def get(self) -> List[str]:
        """Get all items of current list."""
        return self.__output

    def put(self, data: str) -> None:
        """P.ut item in list and perform actions.

        Actions based on folowing flags:
        exception_on_put - raises exception, if not None
        callable_on_put - executes callable once at put
        and set it to None
        """
        if self.exception_on_put:
            raise self.exception_on_put
        if self.callable_on_put:
            self.callable_on_put()
            self.callable_on_put = None
        if self.blocked:
            return
        if isinstance(data, list):
            self.__output.extend(data)
            return
        if KSP.indents is not False:
            data = self.__indent * KSP.indents * ' ' + data
        self.__output.append(data)

    def pop(self) -> str:
        """Pop the last item from list without indentation."""
        return self.__output.pop().strip()

    def refresh(self) -> None:
        """Erase all data from internal list and set defaults."""
        self.__default = list()
        self.__output = self.__default
        self.blocked = False
        self.exception_on_put = None
        self.callable_on_put = None
