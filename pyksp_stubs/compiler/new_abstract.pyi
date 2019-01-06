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
from typing import Protocol
from typing import runtime

T = TypeVar('T')


class KSPBaseMeta(ABCMeta):
    """Abstract base metaclass for all KSP objects.

    for being under united ABCMeta parent
    """

    ...


class KSP(metaclass=KSPBaseMeta):
    """Base class for all compiler objects.

    Takes part of singletone object durin compilicng.
    Has to be refreshed by script at the start of compilation.
    """

    __script: Optional['ScriptBase'] = ...
    __output: Optional['Output'] = ...
    __outputs: List['Output'] = ...
    __listener: Optional['EventListener'] = ...
    __is_compiled: bool = ...
    __callback: Optional['CallbackBase'] = ...
    __is_bool: bool = ...
    __inits: List['HasInit'] = ...
    docs: bool = ...
    indents: int = ...
    compacted_names: bool = ...

    @staticmethod
    def refresh() -> None:
        """Set KSP variables to defaults."""
        ...

    class NoBaseError(Exception):
        """NoBaseError."""

        def __init__(self) -> None:
            """Raise if new output is requested not under script."""
            ...

    @staticmethod
    def append_init(init: 'HasInit') -> None:
        """Append object, able to generate init lines."""
        ...

    @staticmethod
    def get_inits() -> List['HasInit']:
        """Return all objects with inits."""
        ...

    @staticmethod
    def new_out() -> 'Output':
        """Return new Output object.

        normally, should be used by any class wants to produce
        block of lines"""
        ...

    @staticmethod
    def get_out() -> 'Output':
        """Return current Output object."""
        ...

    @staticmethod
    def pop_out() -> 'OutputGot':
        """Return lines from the current Output and delete it."""
        ...

    @staticmethod
    def merge_out() -> None:
        """Put lines from the current Output to the next and delete it."""
        ...

    @staticmethod
    def event(event: 'ListenerEventBase') -> None:
        """Produce event to the current EventListener object.

        or do nothing"""
        ...

    @staticmethod
    def set_listener(listener: 'EventListener') -> None:
        """Attach listener to KSP class."""
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
    """Abstract base class for script."""

    @abstractmethod
    def main(self) -> None:
        """Has to be overloaded by the main compilation function."""
        ...

    @abstractmethod
    def compile(self) -> None:
        """Compile the script."""
        ...


OutputGot = NewType('OutputGot', List[Union['AstNull', str]])


class Output(KSP):
    """Handles generation of code lines."""

    _queue: List['AstRoot'] = ...
    _blocks: List['OutputBlock'] = ...
    _lines: List[Union['AstNull', str]] = ...
    _block_in_queue: \
        Optional[Tuple['OutputBlock', 'OutputBlock', int]] = ...
    _start_indent: int = ...
    indent_level: int = ...
    _blocked: bool = ...

    def __init__(self, indent_level: int) -> None:
        """Initialize.

        indent level has to be 0 or been taken from the last used Output"""
        ...

    def block(self) -> None:
        """Block any addition to Output.

        Raises AssertionError if has been blocked earlier"""
        ...

    def release(self) -> None:
        """Allow to add things to code.

        Raises AssertionError if has not been blocked earlier"""
        ...

    def put_to_queue(self, ast: 'AstRoot') -> None:
        """Put AstRoot to queue.

        leaving empty line to be replaced by Ast, if it is not expanded"""
        ...

    def put_immediatly(self, ast: 'AstRoot') -> None:
        """Expand AstRoot immediately.

        Checks block queue and close it at nesessary.
        Checks queue for expanded during current Ast and removes them
        from queue."""
        ...

    def put_line(self, line: Union['AstNull', str]) -> None:
        """Put expanded line or AstNull to list with correct indent."""
        ...

    def put_lines(self, lines: OutputGot) -> None:
        """Put lines from another Output object to list."""
        ...

    def open_block(self, block: 'OutputBlock') -> None:
        """Open block, increase indent level.

        ignores closing of waiting block if any.

        Raises AssertionError if waiting block, and it is not
        the same block is recieved"""
        ...

    def close_block(self, block: 'OutputBlock') -> None:
        """Close block and decrease indent level."""
        ...

    def wait_for_block(self, opened: 'OutputBlock',
                       next_block: 'OutputBlock') -> None:
        """Put block to block_queue for closing with next event."""
        ...

    def get(self) -> OutputGot:
        """Expand all queued AstRoot and return lines.

        Ast's are expanded in the descending order"""
        ...

    def __str__(self) -> str:
        """Return header line and all lines in readable format."""
        ...


class OutputBlock:
    """Handle indented blocks of code.

    blocks are equal if their open and close strings are equal"""

    open_str: str
    close_str: str
    open: AstString
    close: AstString

    def __init__(self, open_str: str, close_str: str) -> None:
        """Initialize."""
        ...

    def __eq__(self, other: Any) -> bool:
        """Return True if both strings of blocks are equal."""
        ...


class AstBase(KSP, Generic[T]):
    """Abstract base class for all Ast objects."""

    @abstractmethod
    def expand(self) -> str:
        """Recursively expand ast and return summary string."""
        ...

    @abstractmethod
    def get_value(self) -> T:
        """Recursively get runtime value of ast."""
        ...


class AstRootMeta(KSPBaseMeta):
    """AstRoot metaclass.

    wraps expand() method for setting expanded property to True
    at invocation"""

    def __new__(mcls, name: str,
                bases: Tuple[type, ...],
                namespace: Dict[str, Any]) -> Type['AstRoot']:
        """Wrap expand() method for setting expanded to True."""
        ...


class AstRoot(AstBase, metaclass=AstRootMeta):  # type: ignore
    """Base class for AstRoot (e.g. potential starting of line)."""

    _queue_line: int
    _expanded: bool

    class NullError(Exception):
        """Raise if line is empty."""

        def __init__(self) -> None:
            """Initialize."""
            ...

    @property
    def queue_line(self) -> int:
        """Return line of pasting to queue."""
        ...

    @queue_line.setter
    def queue_line(self, line: int) -> None:
        """Set line of pasting to queue."""
        ...

    @property
    def expanded(self) -> bool:
        """Return true, if expand() has been invocated."""
        ...


class AstString(AstRoot):
    """Basic string is put to Output."""

    def __init__(self, string: str) -> None:
        """Initialize."""
        self.string = string

    def expand(self) -> str:
        """Return stored string."""
        return self.string

    def get_value(self) -> NoReturn:
        """Raise NullError."""
        raise self.NullError


class AstNull(AstRoot):
    """Placeholder for queued Ast's."""

    def expand(self) -> NoReturn:
        """Raise NullError."""
        raise self.NullError

    def get_value(self) -> NoReturn:
        """Raise NullError."""
        raise self.NullError


class NameBase(KSP):
    """Simple name handler."""

    _name: str
    _prefix: str
    _postfix: str

    def __init__(self,
                 name: str,
                 prefix: str='',
                 postfix: str='') -> None:
        """Make separate parts, van be modifyed independently."""
        ...

    @property
    def name(self) -> str:
        """Return the main part of name."""
        ...

    @name.setter
    def name(self, name: str) -> None:
        """Name setter."""
        ...

    @property
    def prefix(self) -> str:
        """Return prefix."""
        ...

    @prefix.setter
    def prefix(self, prefix: str) -> None:
        """Prefix setter."""
        ...

    @property
    def postfix(self) -> str:
        """Postfix getter."""
        ...

    @postfix.setter
    def postfix(self, postfix: str) -> None:
        """Postfix setter."""
        ...

    def __call__(self) -> str:
        """Return concatenated prefix, name and postfix."""
        ...


class NameVar(NameBase):
    """Variable name, can be hashed."""

    __scope: List[str] = ['']
    __names_full: List[str] = list()
    __names_comp: List[str] = list()
    _full: str

    def __init__(self,
                 name: str,
                 prefix: str='',
                 postfix: str='',
                 preserve: bool=False) -> None:
        """Compacted if flag is set on KSP.

        Full othercase or if preserve is True."""
        ...

    @property
    def full(self) -> str:
        """Return full name even if it was compacted."""
        ...

    @staticmethod
    def _hash_name(name: str) -> str:
        """Hashing function."""
        ...

    @staticmethod
    def scope(name: str='') -> Optional[str]:
        """Wrap all new declarations within the last put scope.

        if name is not passed, the last scope is removed from list"""
        ...

    @property
    def full(self) -> str:
        """Return full name even if it was compacted."""
        ...

    @staticmethod
    def refresh() -> None:
        """Set all class variables to defaults."""
        ...


@runtime
class HasInit(Protocol):
    """Has method generate_init."""

    def generate_init(self) -> List[str]:
        """Return init lines in lint."""
        ...


class KspObject(KSP):
    """Base class for all objects may appear in code."""

    name: NameVar

    def __init__(self,
                 name: NameBase) -> None:
        """Excluding Ast's."""
        ...

    @staticmethod
    def generate_inits() -> List[str]:
        """Return all init lines of declared instances."""
        ...


class CallbackBase(KSP):
    """Abstract base class for Callbacks."""

    __callbacks: List['CallbackBase']
    __current: 'CallbackBase'
    __id: int

    @abstractmethod
    def add_function(self, function: Callable[[], None]) -> None:
        """Add function to calling queue."""
        ...

    @abstractmethod
    def open(self) -> None:
        """Open callback block and set NI variables to it's values."""
        ...

    @abstractmethod
    def close(self, keep_type: bool=None) -> None:
        """Close callback block and make it init again."""
        ...

    @abstractmethod
    def generate_body(self) -> List[OutputGot]:
        """Return Output lines of invocated functions."""
        ...

    @staticmethod
    @abstractmethod
    def get_all_bodies() -> List[OutputGot]:
        """Collect all bodies of all instantiated callbacks."""
        ...

    @staticmethod
    @abstractmethod
    def refresh() -> None:
        """Set class variables to defaults."""
        ...


class EventListener(KSP):
    """Handle events and invocates functions at them."""

    _event_funcs: \
        Dict[Type['ListenerEventBase'],
             Callable[['ListenerEventBase'], None]]

    def __init__(self) -> None:
        """Initialize."""
        ...

    def bind_to_event(self,
                      func: Callable[['ListenerEventBase'], None],
                      event: Type['ListenerEventBase']) -> None:
        """Bind function to event type.

        function will be invocated at every event of the type."""
        ...

    def put_event(self, event: 'ListenerEventBase') -> None:
        """Invocate event function if any."""
        ...


class ListenerEventBase:
    """Placeholder."""

    ...
