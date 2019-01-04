"""Base compiler classes, whicn aother system is based on."""
from abc import ABCMeta
from abc import abstractmethod
import hashlib

from types import MethodType

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
# from typing import GenericMeta
from typing import Generic

T = TypeVar('T')


class KSPMeta(ABCMeta):
    pass


class KSP(metaclass=KSPMeta):
    __script: Optional['ScriptBase'] = ...
    __output: Optional['Output'] = ...
    __outputs: List['Output'] = ...
    __listener: Optional['EventListener'] = ...
    __is_compiled: bool = ...
    __callback: Optional['CallbackBase'] = ...
    docs: bool = ...
    indents: int = ...
    __is_bool: bool = ...

    @staticmethod
    def refresh() -> None:
        """Set KSP variables to defaults."""
        ...

    class NoBaseError(Exception):
        def __init__(self) -> None:
            super().__init__('Script is not initialized')

    @staticmethod
    def new_out() -> 'Output':
        ...

    @staticmethod
    def pop_out() -> 'OutputGot':
        ...

    @staticmethod
    def merge_out() -> None:
        ...

    @staticmethod
    def event(event: 'ListenerEvent') -> None:
        ...

    @staticmethod
    def is_compiled() -> bool:
        """Check state (changes returns of KSP objects)."""
        ...

    @staticmethod
    def set_compiled(val: bool) -> None:
        """Set state (changes returns of KSP objects)."""
        ...

    @staticmethod
    def set_callback(obj: 'CallbackBase') -> None:
        """Set callback to be counted by built-ins."""
        ...

    @staticmethod
    def callback() -> Optional[object]:
        """Retrieve current callback.

        Return CallbackBase object or None"""
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
    def in_init() -> bool:
        """Check if compiler is in init callback."""
        ...


class ScriptBase(KSP):

    @abstractmethod
    def main(self) -> None:
        ...

    @abstractmethod
    def compile(self) -> None:
        ...


OutputGot = NewType('OutputGot', List[Union['AstNull', str]])


class Output(KSP):
    _queue: List['AstRoot']
    _blocks: List['OutputBlock']
    _lines: List[Union['AstNull', str]]
    _block_in_queue: Optional[Tuple['OutputBlock', 'OutputBlock', int]]
    _start_indent: int
    indent_level: int
    _blocked: bool

    def __init__(self, indent_level: int) -> None:
        ...

    def block(self) -> None:
        ...

    def release(self) -> None:
        ...

    def put_to_queue(self, ast: Union['AstRoot']) -> None:
        ...

    def put_immediatly(self, ast: 'AstRoot') -> None:
        ...

    def put_line(self, line: Union['AstNull', str]) -> None:
        ...

    def put_lines(self, lines: OutputGot) -> None:
        ...

    def open_block(self, block: 'OutputBlock') -> None:
        ...

    def close_block(self, block: 'OutputBlock') -> None:
        ...

    def wait_for_block(self, opened: 'OutputBlock',
                       next_block: 'OutputBlock') -> None:
        ...

    def get(self) -> OutputGot:
        ...

    def __str__(self) -> str:
        ...


class OutputBlock:
    open_str: str
    close_str: str
    open: 'AstString'
    close: 'AstString'

    def __init__(self, open_str: str, close_str: str) -> None:
        ...

    def __eq__(self, other: Any) -> bool:
        ...


class AstBase(KSP, Generic[T]):

    @abstractmethod
    def expand(self) -> str:
        ...

    @abstractmethod
    def get_value(self) -> T:
        ...


class AstRootMeta(KSPMeta):

    def __new__(mcls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any]) -> Type['AstRoot']:
        ...


class AstRoot(AstBase, metaclass=AstRootMeta):  # type: ignore
    _queue_line: int
    _expanded: bool

    class NullError(Exception):
        def __init__(self) -> None:
            ...

    @property
    def queue_line(self) -> int:
        ...

    @queue_line.setter
    def queue_line(self, line: int) -> None:
        ...

    @property
    def expanded(self) -> int:
        ...


class AstString(AstRoot):
    def __init__(self, string: str) -> None:
        ...

    def expand(self) -> str:
        ...

    def get_value(self) -> NoReturn:
        ...


class AstNull(AstRoot):

    def expand(self) -> NoReturn:
        ...

    def get_value(self) -> NoReturn:
        ...


class KspObjectMeta(KSPMeta):
    pass


class KspObject(KSP):
    pass


class CallbackBase(KSP):
    __callbacks: List['CallbackBase']
    __current: 'CallbackBase'
    __id: int

    @abstractmethod
    def add_function(self, function: Callable[[], None]) -> None:
        ...

    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self, keep_type: bool=...) -> None:
        ...

    @abstractmethod
    def generate_body(self) -> List[OutputGot]:
        ...

    @staticmethod
    @abstractmethod
    def get_all_bodies() -> List[OutputGot]:
        ...

    @staticmethod
    @abstractmethod
    def refresh() -> None:
        ...


class EventListener(KSP):

    def __init__(self) -> None:
        ...

    def bind_to_event(self,
                      func: Callable[['ListenerEvent'], None],
                      event: Type['ListenerEvent']) -> None:
        ...

    def put_event(self, event: 'ListenerEvent') -> None:
        ...


class ListenerEvent:
    ...
