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
