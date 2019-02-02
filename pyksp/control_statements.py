"""Implement base control structures: conditions and loops.

If(consition) <context manager>
Else([consition]) <context manager>
Select(expression) -> Case([constant]) <context manager>
While(condition) <context manager>
For(<look for docs>) <Iterator and context manager>
"""
import typing as ty

from . import abstract as ab
from . import base_types as bt


class IfElse(ab.KSP):
    """Base class for conditions."""
    stack: ty.ClassVar[ty.List['If']] = list()
    _is_true: ty.ClassVar[bool] = True
    true_current: bool

    @property
    def is_true(self) -> bool:
        """Return true, if condition."""
        return IfElse._is_true

    @is_true.setter
    def is_true(self, val: bool) -> None:  # pylint: disable=R0201
        IfElse._is_true = val

    def __enter__(self) -> None:
        """Handle is_true value of current context."""
        self.true_current = self.is_true

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        """Handle is_true for future contexts."""
        self.is_true = self.true_current


class If(IfElse):
    """Implement KSP if condition.

    usage:
    with If(condition: ty.Union[bt.AstBool, bool]):
        KSP code
    with Else([condition: ty.Union[bt.AstBool, bool]]):
        KSP code

    KSP objects will be assigned and processed only in true contexts.
    with context with false condition only code will be generated.
    Note, that code inside false context is still executed, so any
    Python expressions will be executed too. Just KSP realtime
    assignements are ignored."""

    def __init__(self, condition: ty.Union[bt.AstBool, bool]) -> None:
        condition = ty.cast(bt.AstBool, condition)
        self._condition_bool = bool(condition)
        self._condition_line = condition.expand_bool()
        self._block = ab.OutputBlock(f'if', 'end if', self._condition_line)
        self._out: ab.Output
        self._exited: bool = False

    def __enter__(self) -> None:
        super().__enter__()
        self._out = self.get_out()
        self._out.put_immediatly(ab.AstNull())
        try:
            if self.stack[-1]._exited:
                self.stack.pop()
        except IndexError:
            pass
        if not self._condition_bool:
            self.is_true = False
        if not self.is_true:
            self.set_compiled(True)
        self._out.open_block(self._block)
        self.stack.append(self)

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        super().__exit__(exc_type, exc_value, traceback)
        self._exited = True
        if self.stack[-1] is not self:
            self.stack.pop()
            self._out.put_immediatly(ab.AstNull())
        if len(self.stack) < 2:
            self.is_true = True
        self.set_compiled(False)
        self._out.wait_for_block(self._block, ab.OutputBlock('else', 'end if'))


class Else(IfElse):
    """Implement KSP else/else if statements.

    for If-Else contexts docs see If doc.
    if no condition is passed, used as regular else.
    If initialized within conditions works as elif."""

    def __init__(self,
                 condition: ty.Optional[ty.Union[bt.AstBool, bool]] = None
                 ) -> None:
        if not self.stack:
            raise RuntimeError('If(<condition>) block missed')
        if self.stack[-1]._exited is False:
            raise RuntimeError('probably, wrong identation')
        self._block = ab.OutputBlock('else', 'end if')
        self._out: ab.Output
        self._condition = condition
        if condition is None:
            self._elif = None
            return
        self.stack[-1]._exited = False
        self._elif = If(condition)

    def __enter__(self) -> None:
        super().__enter__()
        if self.stack[-1]._condition_bool or not self.is_true:
            self.set_compiled(True)
        if self.stack[-1]._exited and not self._elif:
            self.stack.pop()
        self._out = self.get_out()
        self._out.open_block(self._block)
        if self._elif:
            self._elif.__enter__()

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        super().__exit__(exc_type, exc_value, traceback)
        if self._elif:
            self._elif.__exit__(exc_type, exc_value, traceback)
            self.stack.pop()
            self.stack[-1]._exited = True
        if not self.stack:
            self.is_true = True
        self._out.put_immediatly(ab.AstNull())
        self.set_compiled(False)
        self._out.close_block(self._block)


class SelectCase(IfElse):
    """Base class for select-case (switch) KSP statements."""
    _vars: ty.List[bt.NTU[int]] = list()
    __case_opened: bool = True

    @property
    def _case_opened(self) -> bool:
        return SelectCase.__case_opened

    @_case_opened.setter
    def _case_opened(self, val: bool) -> None:  # pylint: disable=R0201
        if not isinstance(val, bool):
            raise TypeError('has to be bool')
        SelectCase.__case_opened = val


class CaseException(Exception):
    """Raise if KSP code passed inside Select context."""

    def __init__(self) -> None:
        super().__init__('outside case-context')


def raise_on_put(event: ab.EventAddedToOutput) -> None:
    """Bound to every output added AstRoot event."""
    if issubclass(event.item_type, ab.AstRoot):
        raise CaseException


class Select(SelectCase):
    """Implement KSP select condition.

    usage:
        with Select(<KSP int expression>):
            KSP code here raises error
            with case(int):
                KSP code"""
    out: ab.Output
    block: ab.OutputBlock
    listener: ab.EventListener

    def __init__(self, expression: bt.NTU[int]) -> None:
        e_rt = bt.get_value(expression)
        if not isinstance(e_rt, int):
            raise TypeError(
                'Has to be valid KSP int expression. pasted %s' % expression)
        self._vars.append(expression)
        self.block = ab.OutputBlock('select', 'end select',
                                    bt.get_compiled(expression))

    def __enter__(self) -> None:
        self.out = self.get_out()
        self.listener = self.get_listener()
        self.out.put_immediatly(ab.AstNull())
        self.out.open_block(self.block)
        self.listener.bind_to_event(raise_on_put, ab.EventAddedToOutput)
        self._case_opened = False

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        self.listener.unbind(raise_on_put, ab.EventAddedToOutput)
        self.out.put_immediatly(ab.AstNull())
        self.out.close_block(self.block)
        self._vars.pop()
        self._case_opened = True


class Case(SelectCase):
    """Implement KSP select-case case block.

    see Select doc."""
    out: ab.Output
    block: ab.OutputBlock
    listener: ab.EventListener

    def __init__(self, state: int) -> None:
        if not isinstance(state, int):
            raise TypeError(f'accepts only generic ints, pasted {state}')
        self.state = state
        self.block = ab.OutputBlock('case', '', bt.get_compiled(state))

    def __enter__(self) -> None:
        super().__enter__()
        if self._case_opened:
            raise RuntimeError('nested case')
        self._case_opened = True
        self.listener = self.get_listener()
        self.listener.unbind(raise_on_put, ab.EventAddedToOutput)
        self.out = self.get_out()
        self.out.put_immediatly(ab.AstNull())
        self.out.open_block(self.block)
        if not bool(self._vars[-1] == self.state):
            self.is_true = False
        if not self.is_true:
            self.set_compiled(True)

    def __exit__(  # pylint: disable=W0235
            self, exc_type: ty.Type[Exception], exc_value: ty.Any,
            traceback: ty.Any) -> None:
        super().__exit__(exc_type, exc_value, traceback)
        self.set_compiled(False)
        self.out.put_immediatly(ab.AstNull())
        self.out.close_block(self.block)
        self.listener.bind_to_event(raise_on_put, ab.EventAddedToOutput)
        self._case_opened = False


class ForEnum:
    """class for static checking of for enum arg."""


enum = ForEnum()

ARGT = ty.Union[int, bt.ArrBase, ForEnum]


def For(*args: ARGT
        ) -> ty.Iterator[ty.Union[ty.Iterable[bt.VarBase], bt.VarBase]]:
    """Return ForClass Iterator, implements various for loops in KSP.

    if int args are passed works as Python for i in range(args) loop.
    for i in For(3):
        will be executed 3 times with i being Var,
        keeps value from 0 to 2
    for i in For(2, 4):
        will be executed 2 times with i being Var,
        keeps value from 2 to 3
    for i in For(10, 5, -2):
        will be executed 3 times with i being Var,
        iterates over [10, 8, 6]

    if Arr args are passed works as normal Python for/zip loop.
    for i in For(Arr[int]([1,3,4])):
        will be executed 3 times with i being Arr item
    for i, f in For(Arr[int]([1,3,4]), Arr[float]([1.5,2.3])):
        will be executed 2 times with i being int Arr item,
        and f being float Arr item.

    if enum passed as the first arg works like Python
    for i in enumerate(list) of for i in enumerate(zip(list(lists))) loop.
    for idx, i in For(enum, Arr[int]([1,3,4])):
        will be executed 3 times with i being Arr item,
        and idx being Var[int] keeps vals in range 0 -> 2
    for idx, i, f in For(enum, Arr[int]([1,3,4]), Arr[float]([1.5,2.3])):
        will be executed 2 times with i being int Arr item,
        and f being float Arr item,
        and idx being Var[int] keeps vals in range 0 -> 1

    when used as context manager, can be stopped before going through
    all values.
    with For(2) as f:
        for i in f:
            with If(i == 0):
                f.brake_loop()
                # equals to i <<= 2
    """
    return ForClas(*args)


class ForClas(ab.KSP):  # pylint: disable=R0902
    """Implement KSP for loops."""
    loop_type: str
    start: int
    step: int
    stop: int
    args: ty.Sequence[ARGT]
    _exited: bool
    _block: ab.OutputBlock
    _out: ab.Output
    _count: int
    _ptr: int

    _idx = bt.Arr[int](name='__for_idx__', size=100)
    _depth = -1

    @staticmethod
    def _check_for_arrays(args: ty.Sequence[ARGT],
                          algo_name: str,
                          should_be_instance: bool = True) -> None:
        for i in range(1, len(args)):
            if not isinstance(args[i], bt.Arr) and should_be_instance:
                raise TypeError(
                    f'{algo_name} works only with arrays, pasted: {i}')
            if isinstance(args[i], bt.Arr) and not should_be_instance:
                raise TypeError(f'{algo_name} not works with arrays')

    @classmethod
    def _initialize(cls) -> None:
        cls.append_init(cls._idx)
        # cls.append_init(cls._ptr)

    def __init__(self, *args: ARGT) -> None:
        if not args:
            raise TypeError('has to be at least 1 arg')
        self.args = args
        self._exited = False

        if not self.for_init():
            self._initialize()
        self._parametrized_init(*args)

    def _parametrized_init(self, *args: ARGT) -> None:
        if args[0] is enum:
            self._check_for_arrays(args, 'enum')
            self._init_as_enum(args)
            return
        if isinstance(args[0], bt.Arr):
            self._check_for_arrays(args, 'zip')
            self._init_as_zip(args)
            return
        if isinstance(args[0], (int, bt.ProcessInt)):
            self._check_for_arrays(args, 'range', False)
            self.loop_type = 'range'
            if len(args) > 3:
                raise TypeError(
                    'range supports up to 3 args: start, stop, step')
            self._init_as_range(ty.cast(ty.Sequence[int], args))
            return
        raise TypeError('can not infer loop type')

    def _init_as_enum(self, args: ty.Sequence[ARGT]) -> None:
        self.loop_type = 'enum'
        top = 1000000
        if len(args) == 1:
            raise TypeError('enum has to be used with at least one Arr object')
        for arr in args[1:]:
            arr = ty.cast(bt.ArrBase, arr)
            if len(arr) < top:
                top = len(arr)
        self.start = 0
        self.stop = top
        self.step = 1

    def _init_as_zip(self, args: ty.Sequence[ARGT]) -> None:
        self.loop_type = 'zip'
        top = 1000000
        for arr in args:
            arr = ty.cast(bt.ArrBase, arr)
            if len(arr) < top:
                top = len(arr)
        self.start = 0
        self.stop = top
        self.step = 1

    def _init_as_range(self, args: ty.Sequence[int]) -> None:
        if len(args) == 1:
            if bt.get_value(args[0]) < 1:
                raise TypeError('can be only positive int')
            self.start = 0
            self.stop = args[0]
            self.step = 1
        if len(args) == 2:
            self.start = args[0]
            self.stop = args[1]
            if bt.get_value(self.start) > bt.get_value(self.stop):
                self.step = -1
            else:
                self.step = 1
        if len(args) == 3:
            self.start = args[0]
            self.stop = args[1]
            self.step = args[2]

    def __enter__(self) -> 'ForClas':
        return self

    def __exit__(  # pylint: disable=W0235
            self, exc_type: ty.Type[Exception], exc_value: ty.Any,
            traceback: ty.Any) -> None:
        if not self._exited:
            self._exit()

    def __iter__(self) -> 'ForClas':
        self._out = self.new_out()
        ForClas._depth += 1
        self._ptr = ForClas._depth
        self._block = self._get_block()
        self._out.open_block(self._block)
        self._count = 0
        return self

    def _exit(self) -> None:
        ForClas._depth -= 1
        self._exited = True
        self._out.release()
        self._out.close_block(self._block)
        self.merge_out()

    def __next__(self) -> ty.Union[ty.Iterable[bt.VarBase], bt.VarBase]:
        self._check_next()
        self._count += 1
        if self.loop_type == 'range':
            return self._idx[self._ptr]
        if self.loop_type == 'zip':
            if len(self.args) == 1:
                return self.args[0][self._idx[self._ptr]]  # type: ignore
            return [
                arr[self._idx[self._ptr]]
                for arr in ty.cast(ty.Sequence[bt.ArrBase], self.args)
            ]
        if self.loop_type == 'enum':
            out = [self._idx[self._ptr]]
            out.extend([
                arr[self._idx[self._ptr]]
                for arr in ty.cast(ty.Sequence[bt.ArrBase], self.args[1:])
            ])
            return out
        raise RuntimeError('undefined behaviour')

    def _check_next(self) -> None:
        limit = 500000
        if self._count > limit:
            raise RuntimeError('%s iterations. Endless loop.' % limit)
        if self._count != 0:
            self._count_idx()
            if self.is_compiled():
                self._exit()
                raise StopIteration
        if self.step > 0:
            cond = bt.get_value(self._idx[self._ptr]) >= bt.get_value(
                self.stop)
        else:
            cond = bt.get_value(self._idx[self._ptr]) <= bt.get_value(
                self.stop)
        if cond:
            self._exit()
            raise StopIteration

    def _count_idx(self) -> None:
        if bt.get_value(self.step) == 1:
            self._idx[self._ptr].inc()
        elif bt.get_value(self.step) == -1:
            self._idx[self._ptr].dec()
        else:
            self._idx[self._ptr] += self.step
        if self._count == 1:
            self._out.block()

    def _get_block(self) -> ab.OutputBlock:
        add_str: bt.OperatorComparisson
        self._idx[self._ptr] <<= self.start
        if self.start < self.stop:
            add_str = self._idx[self._ptr] < self.stop
        else:
            add_str = self._idx[self._ptr] > self.stop
        return ab.OutputBlock('while', 'end while', add_str.expand())

    def break_loop(self) -> None:
        """Finish this iteration and exit the loop.

        equals to idx = self.stop"""
        self._idx[self._ptr] <<= self.stop


class While(ab.KSP):
    """Wrap context in KSP while syntax.

    still, only while usage is any sort of complex callbacks,
    currently While context manager does nothing more than
    executes code in context one time and wraps it to KSP block:
    while(condition)
        KSP code
    end while"""
    _out: ab.Output

    def __init__(self, condition: bt.AstBool) -> None:
        if not isinstance(condition, bt.AstBool):
            raise TypeError('epected bool, pasted {c} ({r})'.format(
                c=bt.get_compiled(condition), r=bt.get_value(condition)))
        self._block = ab.OutputBlock('while', 'end while',
                                     condition.expand_bool())

    def __enter__(self) -> None:
        self._out = self.get_out()
        self._out.open_block(self._block)

    def __exit__(  # pylint: disable=W0235
            self, exc_type: ty.Type[Exception], exc_value: ty.Any,
            traceback: ty.Any) -> None:
        self._out.close_block(self._block)
