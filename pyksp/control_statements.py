import typing as ty

from . import abstract as ab
from . import base_types as bt


class IfElse(ab.KSP):
    stack: ty.ClassVar[ty.List['If']] = list()
    _is_true: ty.ClassVar[bool] = True
    true_current: bool

    @property
    def is_true(self) -> bool:
        return IfElse._is_true

    @is_true.setter
    def is_true(self, val: bool) -> None:  # pylint: disable=R0201
        IfElse._is_true = val

    def __enter__(self) -> None:
        self.true_current = self.is_true

    def __exit__(self, exc_type: ty.Type[Exception], exc_value: ty.Any,
                 traceback: ty.Any) -> None:
        self.is_true = self.true_current


class If(IfElse):
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
    def __init__(self) -> None:
        super().__init__('outside case-context')


def raise_on_put(event: ab.EventAddedToOutput) -> None:
    if issubclass(event.item_type, ab.AstRoot):
        raise CaseException


class Select(SelectCase):
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


ForEnum = ty.NewType('ForEnum', object)
enum = ForEnum(1)

ARGT = ty.Union[int, bt.Arr, ForEnum]


class For(ab.KSP):
    loop_type: str
    start: int
    step: int
    stop: int
    args: ty.Sequence[ARGT]
    _exited: bool
    _block: ab.OutputBlock
    _out: ab.Output
    _count: int

    _idx = bt.Arr[int](name='__for_loop_idx__', size=10)
    # reveal_type(_idx)
    _depth = int()
    _ptr: int

    @staticmethod
    def _check_for_arrays(args: ty.Sequence[ARGT],
                          algo_name: str,
                          should_be_instance: bool = True) -> None:
        for i in range(1, len(args)):
            if not isinstance(i, bt.Arr) and should_be_instance:
                raise TypeError(f'{algo_name} works only with arrays')
            if isinstance(i, bt.Arr) and not should_be_instance:
                raise TypeError(f'{algo_name} not works with arrays')

    @classmethod
    def _initialize(cls) -> None:
        cls.append_init(cls._idx)

    def __init__(self, *args: ARGT) -> None:
        if not args:
            raise TypeError('has to be at least 1 arg')
        self.args = args
        self._exited = False
        self._ptr = self._depth
        if not self.for_init():
            self._initialize()
        if args[0] is enum:
            self._check_for_arrays(args, 'enum')
            self._init_as_enum(args)
            return
        if isinstance(args[0], bt.Arr):
            self._check_for_arrays(args, 'zip')
            self._init_as_zip(args)
            return
        if isinstance(args[0], int):
            self._check_for_arrays(args, 'range', False)
            self._init_as_range(args)
            return
        raise TypeError('can not infer loop type')

    def _init_as_enum(self, args: ty.Sequence[ARGT]) -> None:
        self.loop_type = 'enum'
        top = 1000000
        for arr in args[1:]:
            arr = ty.cast(bt.Arr, arr)
            if len(arr) < top:
                top = len(arr)
        self.start = 0
        self.stop = top
        self.step = 1

    def _init_as_zip(self, args: ty.Sequence[ARGT]) -> None:
        self.loop_type = 'zip'
        top = 1000000
        for arr in args:
            arr = ty.cast(bt.Arr, arr)
            if len(arr) < top:
                top = len(arr)
        self.start = 0
        self.stop = top
        self.step = 1

    def _init_as_range(self, args: ty.Sequence[ARGT]) -> None:
        self.loop_type = 'range'
        if len(args) > 3:
            raise TypeError('range supports up to 3 args: start, stop, step')
        args = ty.cast(ty.Sequence[int], args)
        if len(args) == 1:
            if args[0] < 1:
                raise TypeError('can be only positive int')
            self.start = 0
            self.stop = args[0]
            self.step = 1
        if len(args) == 2:
            self.start = args[0]
            self.stop = args[1]
            if self.start < self.stop:
                self.step = -1
            else:
                self.step = 1
        if len(args) == 2:
            self.start = args[0]
            self.stop = args[1]
            self.step = args[2]

    def __enter__(self) -> 'For':
        return self

    def __exit__(  # pylint: disable=W0235
            self, exc_type: ty.Type[Exception], exc_value: ty.Any,
            traceback: ty.Any) -> None:
        if not self._exited:
            self._exit()

    def _exit(self) -> None:
        self._exited = True
        self._out.release()
        self._out.close_block(self._block)

    def __iter__(self) -> 'For':
        self._out = self.new_out()
        self._block = self._get_block()
        self._out.open_block(self._block)
        self._out.block()
        self._count = 0
        return self

    def __next__(self) -> ty.Union[ty.Iterable[bt.VarParent], bt.VarParent]:
        if self._count != 0:
            self._idx[self._ptr] += self.step
        self._count += 1
        if self.loop_type == 'range':
            return self._idx[self._ptr]
        if self.loop_type == 'zip':
            self.args = ty.cast(ty.Sequence[bt.Arr], self.args)
            return [arr[self._idx[self._ptr]] for arr in self.args]

    def _get_block(self) -> ab.OutputBlock:
        add_str: bt.OperatorComparisson
        self._idx[self._ptr] <<= self.start
        if self.start < self.stop:
            add_str = self._idx[self._ptr] < self.stop
        else:
            add_str = self._idx[self._ptr] > self.stop
        return ab.OutputBlock('while', 'end while', add_str.expand())
