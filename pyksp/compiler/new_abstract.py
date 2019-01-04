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

    # def __new__(mcls, name: str,
    #             bases: Tuple[type, ...],
    #             namespace: Dict[str, Any]) -> Type['KSP']:
    #     cls = super().__new__(mcls, name, bases, namespace)
    #     print(cls == mcls, cls, mcls)
    #     return cls

    # def __call__(cls, *args: Tuple[Any, ...],
    #              **kwargs: Dict[str, Any]) -> 'KSP':
    #     setattr(cls, 'test_prop', 'KSP')
    #     obj = super().__call__(*args, **kwargs)
    #     return obj


class KSP(metaclass=KSPMeta):
    __script: Optional['ScriptBase'] = None
    __output: Optional['Output'] = None
    __outputs: List['Output'] = list()
    __listener: Optional['EventListener'] = None
    __is_compiled: bool = False
    __callback: Optional['CallbackBase'] = None
    docs: bool = False
    indents: int = 0
    __is_bool: bool = False

    @staticmethod
    def refresh() -> None:
        """Set KSP variables to defaults."""
        KSP.__script = None
        KSP.__output = None
        KSP.__listener = None
        KSP.__is_compiled = False
        KSP.__callback = None
        KSP.docs = False
        KSP.indents = 0
        KSP.__is_bool = False
        KSP.__outputs = list()

    class NoBaseError(Exception):
        def __init__(self) -> None:
            super().__init__('Script is not initialized')

    @staticmethod
    def new_out() -> 'Output':
        if KSP.__script is None:
            raise KSP.NoBaseError
        if KSP.__outputs:
            il = KSP.__outputs[-1].indent_level
        else:
            il = 0
        otpt = Output(il)
        KSP.__outputs.append(otpt)
        return otpt

    @staticmethod
    def pop_out() -> 'OutputGot':
        out = KSP.__outputs[-1].get()
        KSP.__outputs.pop()
        return out

    @staticmethod
    def merge_out() -> None:
        out = KSP.pop_out()
        KSP.__outputs[-1].put_lines(out)

    @staticmethod
    def event(event: 'ListenerEvent') -> None:
        if KSP.__listener is not None:
            KSP.__listener.put_event(event)

    @staticmethod
    def is_compiled() -> bool:
        """Check state (changes returns of KSP objects)."""
        return KSP.__is_compiled

    @staticmethod
    def set_compiled(val: bool) -> None:
        """Set state (changes returns of KSP objects)."""
        KSP.__is_compiled = val

    @staticmethod
    def set_callback(obj: 'CallbackBase') -> None:
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

        Return CallbackBase object or None"""
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
    def in_init() -> bool:
        """Check if compiler is in init callback."""
        return KSP.__callback is None


class ScriptBase(KSP):

    @abstractmethod
    def main(self) -> None:
        ...

    @abstractmethod
    def compile(self) -> None:
        ...


OutputGot = NewType('OutputGot', List[Union['AstNull', str]])


class Output(KSP):

    def __init__(self, indent_level: int) -> None:
        self._queue: List['AstRoot'] = list()
        self._blocks: List['OutputBlock'] = list()
        self._lines: List[Union['AstNull', str]] = list()
        self._block_in_queue: \
            Optional[Tuple['OutputBlock', 'OutputBlock', int]] = None
        self._start_indent = indent_level
        self.indent_level = indent_level
        self._blocked = False

    def block(self) -> None:
        assert self._blocked is False, 'blocked yet'
        self._blocked = True

    def release(self) -> None:
        assert self._blocked is True, 'has not been blocked'
        self._blocked = False

    def put_to_queue(self, ast: Union['AstRoot']) -> None:
        if self._blocked:
            return
        ast.queue_line = len(self._lines)
        self._queue.append(ast)
        self.put_line(AstNull())

    def put_immediatly(self, ast: 'AstRoot') -> None:
        if self._blocked:
            return
        if self._block_in_queue:
            block = self._block_in_queue[0]
            block_line = self._block_in_queue[2]
            self._lines[block_line] = block.close.expand()
            self._block_in_queue = None
            self._blocks.pop()
        line = ast.expand()
        for idx, ast in enumerate(self._queue):
            if ast.expanded is True:
                del self._queue[idx]
        self.put_line(line)

    def put_line(self, line: Union['AstNull', str]) -> None:
        if self._blocked:
            return
        if isinstance(line, AstNull):
            self._lines.append(line)
            return
        newline: str = ' ' * KSP.indents * self.indent_level + line
        self._lines.append(newline)

    def put_lines(self, lines: OutputGot) -> None:
        for line in lines:
            self.put_line(line)

    def open_block(self, block: 'OutputBlock') -> None:
        if self._blocked:
            return
        if self._block_in_queue:
            opened = self._block_in_queue[0]
            nextb = self._block_in_queue[1]
            assert block == nextb, f'block {nextb} is waited by {opened}'
            block_line = self._block_in_queue[2]
            self._block_in_queue = None
            self.indent_level -= 1
            self._blocks.pop()
        self.put_immediatly(block.open)
        self.indent_level += 1
        self._blocks.append(block)

    def close_block(self, block: 'OutputBlock') -> None:
        if self._blocked:
            return
        self.indent_level -= 1
        self.put_immediatly(block.close)
        assert self._blocks, 'all blocks are closed'
        assert self._blocks[-1] is block, \
            f'block {self._blocks[-1]} on the top of stack'
        assert self.indent_level >= self._start_indent,\
            f'indent level below stert. line: {block.close.expand()}'
        self._blocks.pop()

    def wait_for_block(self, opened: 'OutputBlock',
                       next_block: 'OutputBlock') -> None:
        if self._blocked:
            return
        self._block_in_queue = (opened, next_block, len(self._lines))
        return

    def get(self) -> OutputGot:
        return cast(OutputGot, self._lines)

    def __str__(self) -> str:
        out = f'Output from {self.__repr__()}'
        for line in self._lines:
            if isinstance(line, AstNull):
                continue
            out += '\n' + line
        return out


class OutputBlock:

    def __init__(self, open_str: str, close_str: str) -> None:
        self.open_str = open_str
        self.close_str = close_str
        self.open = AstString(open_str)
        self.close = AstString(close_str)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OutputBlock):
            return False
        if self.open_str == other.open_str and\
                self.close_str == other.close_str:
            return True
        else:
            return False


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
        cls = super().__new__(mcls, name, bases, namespace)

        old_expand = getattr(cls, 'expand')

        def expanded_wrapper(self: 'AstRoot') -> str:
            self._expanded = True
            return old_expand(self)

        setattr(cls, 'expand', expanded_wrapper)

        return cls


class AstRoot(AstBase, metaclass=AstRootMeta):
    _queue_line: int
    _expanded: bool

    class NullError(Exception):
        def __init__(self) -> None:
            super().__init__('line is null')

    @property
    def queue_line(self) -> int:
        return self._queue_line

    @queue_line.setter
    def queue_line(self, line: int) -> None:
        self._queue_line = line

    @property
    def expanded(self) -> int:
        return self._expanded


class AstString(AstRoot):
    def __init__(self, string: str) -> None:
        self.string = string

    def expand(self) -> str:
        return self.string

    def get_value(self) -> NoReturn:
        raise self.NullError


class AstNull(AstRoot):

    def expand(self) -> NoReturn:
        raise self.NullError

    def get_value(self) -> NoReturn:
        raise self.NullError


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
    def close(self, keep_type: bool=None) -> None:
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
        self._event_funcs: \
            Dict[Type['ListenerEvent'],
                 Callable[['ListenerEvent'], None]] = dict()

    def bind_to_event(self,
                      func: Callable[['ListenerEvent'], None],
                      event: Type['ListenerEvent']) -> None:
        self._event_funcs[event] = func

    def put_event(self, event: 'ListenerEvent') -> None:
        for event_type in self._event_funcs:
            if isinstance(event, event_type):
                self._event_funcs[event_type](event)
                return


class ListenerEvent:
    ...
