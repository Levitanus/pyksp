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

ST = TypeVar('ST')


class KspMeta(ABCMeta):
    """Metaclass to be parent for all compiler metaclasses."""
    ...


class SingletonMeta(KspMeta):
    """Singleton metaclass."""

    def __call__(cls: Type[ST], *args: Any, **kw: Any) -> ST:
        """Return instance of class."""
        ...


class KSP(metaclass=KspMeta):
    """Base abstract class for all compiler classes."""

    __is_compiled: bool = ...
    __is_bool: bool = ...
    __in_init: bool = ...
    __callback: Optional[object] = ...
    indents = ...
    docs = ...

    @staticmethod
    def is_compiled() -> bool:
        """Check state (changes returns of KSP objects)."""
        ...

    @staticmethod
    def set_compiled(val: bool) -> None:
        """Set state (changes returns of KSP objects)."""
        ...

    @staticmethod
    def set_callback(obj: object) -> None:
        """Set callback to be counted by built-ins."""
        ...

    @staticmethod
    def callback() -> Optional[object]:
        """Retrieve current callback.

        Return Callback object or None"""
        ...

    @staticmethod
    def is_bool() -> bool:
        """Check state (for usage in if/else select/case blocks)."""
        ...

    @staticmethod
    def set_bool(val: bool) -> None:
        """Set bool state (for usage in if/else select/case blocks)."""
        ...

    @staticmethod
    def in_init(val: Optional[bool]=...) -> Optional[bool]:
        """Set or check if compiler is in init callback.

        val is optional. Within kwarg "val" sets state to it
        without - checks"""
        ...

    @staticmethod
    def refresh() -> None:
        """Set KSP variables to defaults."""
        ...


class INameLocal(KSP):
    """Object name interface.

    Example:
    class Test2:

        def __init__(self, name='myname'):
            self.name = INameLocal(name)
    prefix and postfix used in childs for preserving order of strings
    """

    script_prefix = ''

    def __init__(self, name: str, prefix: str=...,
                 postfix: str=...) -> None:
        """Object name interface."""
        ...

    def __call__(self) -> str:
        """Return name."""
        ...

    @staticmethod
    def refresh() -> None:
        """Refresh script prefix."""
        ...


class IName(INameLocal):
    """Name can be compacted by default.

    For preserving use
    preserve=True
    prefix and postfix are always preserved and placed at sides.
    """

    __is_compact: bool = ...
    __names: List[str] = ...
    __scope: List[str] = ...

    @staticmethod
    def is_compact() -> bool:
        """Check if names are hashed."""
        ...

    @staticmethod
    def set_compact(val: bool) -> None:
        """Hash names to 5-letter if val is True."""
        ...

    def __init__(self, name: str,
                 prefix: str=...,
                 postfix: str=...,
                 preserve: bool=...) -> None:
        """Name can be compacted by default."""
        ...

    @staticmethod
    def get_compact_name(name: str) -> str:
        """Hashing function."""
        ...

    @staticmethod
    def scope(name: str=...) -> Optional[str]:
        """Wrap all new declarations within the last put scope.

        if name is not passed, the last scope is removed from list"""
        ...

    @property
    def full(self) -> str:
        """Return full name even if it was compacted."""
        ...

    @property
    def compact(self) -> str:
        """Return compacted name."""
        ...

    @staticmethod
    def refresh() -> None:
        """Set all class variables to defaults."""
        ...


class KspObject(KSP):
    """Base abstract class for all objects can be translated to code."""

    comments: bool = ...
    _instances: List['KspObject'] = ...

    @property
    def has_init(self) -> bool:
        """Return True if has to return init block."""
        ...

    @property
    def is_local(self) -> bool:
        """Return True if has not return init and executable block."""
        ...

    @staticmethod
    def instances() -> List['KspObject']:
        """Return list with all instances of KspObject."""
        ...

    @abstractmethod
    def __init__(self, name: str,
                 name_prefix: str=...,
                 name_postfix: str=...,
                 preserve_name: bool=...,
                 has_init: bool=...,
                 is_local: bool=...) -> None:
        """KSP object."""
        ...

    @abstractmethod
    def _generate_init(self) -> List[str]:
        ...

    @staticmethod
    def generate_all_inits() -> List[str]:
        """Return init lines for every instance.

        If instance marked as not having init it's _generate_init()
        method is not being executed"""
        ...

    @staticmethod
    def refresh() -> None:
        """Clear all instances."""
        ...


class Output(metaclass=SingletonMeta):
    """Singleton interface for managing pure code."""

    class IsSetError(Exception):
        """Raises if Output set() is called while it is set already."""

        def __init__(self, extra: str=...) -> None:
            """IsSetError."""
            ...

    class IndentError(Exception):
        """Raises if indentation level goes below 0."""

        def __init__(self, extra: str=...) -> None:
            """IndentError."""
            ...

    def indent(self) -> None:
        """Increase indentation level to be used within compilation."""
        ...

    def unindent(self) -> None:
        """Increase indentation level to be used within compilation.

        Raises Output.IndentError if indent level is below 0"""
        ...

    def __init__(self) -> None:
        """Singleton interface for managing pure code."""
        ...

    def set(self, obj: List[str]) -> None:
        """Set list for code from internal to external.

        (callback body, for example)
        raises self.IsSetError if already set
        (e.g. can output only to top level)"""
        ...

    def release(self) -> None:
        """Set output to internal list."""
        ...

    def get(self) -> List[str]:
        """Get all items of current list."""
        ...

    def put(self, data: str) -> None:
        """P.ut item in list and perform actions.

        Actions based on folowing flags:
        exception_on_put - raises exception, if not None
        callable_on_put - executes callable once at put
        and set it to None
        """
        ...

    def pop(self) -> str:
        """Pop the last item from list without indentation."""
        ...

    def refresh(self) -> None:
        """Erase all data from internal list and set defaults."""
        ...
