from .abstract import Output
from .abstract import KSP
from .abstract import IName

from .script import kScript
from .functions import kLocals
from .functions import kLoc

from .native_types import kInt
from .native_types import kStr
from .native_types import kReal
from .native_types import kArrInt
from .native_types import kArrStr
from .native_types import kArrReal

from .bi_ui_controls import kWidget
from .bi_ui_controls import KspNativeControl
from .bi_ui_controls import set_control_par
from .bi_ui_controls import get_control_par
from .bi_ui_controls import CONTROL_PAR_HIDE
from .bi_ui_controls import HIDE_WHOLE_CONTROL
from .bi_ui_controls import HIDE_PART_NOTHING
# from .bi_ui_controls import WidgetMeta

from .conditions_loops import For
from .conditions_loops import If
from .conditions_loops import Else

from typing import Union
from typing import List
from typing import Optional
from typing import Callable
from typing import cast
from typing import Any
from typing import TypeVar

from functools import wraps
from inspect import cleandoc
from abc import abstractmethod

from re import sub


def docstring(f):
    """Decorator for placing docastrings as comments to code
    docstring will be placed at the function invocation place
    if script docs attribute is set to True"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not KSP.docs:
            return f(*args, **kwargs)
        Output().put('{%s}' % f.__doc__)
        # if not KSP.indents:
        #     Output().put('{%s}' % f.__doc__)
        #     return
        # comm = cleandoc(f.__doc__).split('\n')
        # new = comm[0]
        # if len(comm) > 1:
        #     for line in comm[1:]:
        #         new += f'\n{" " * KSP.indents}{line}'
        # Output().put('{%s}' % new)
        return f(*args, **kwargs)

    return wrapper


def scope(f):
    """Decorator for making all Ksp declarations 'local'
    adds current scope to the declaration name"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # print(dir(f))
        scope = f'{f.__module__}_{f.__qualname__}_'
        scope = sub(r'(__init__)|[<>]', '', scope)
        scope = sub(r'\.', '_', scope)
        IName.scope(scope)
        ret_val = f(*args, **kwargs)
        IName.scope('')
        return ret_val

    return wrapper


def scope_with_locals(local: kLocals):

    def scope(f):
        """Decorator for making all Ksp declarations 'local'
        adds current scope to the declaration name"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            # print(dir(f))
            scope = f'{f.__module__}_{f.__qualname__}_'
            scope = sub(r'(__init__)|[<>]', '', scope)
            scope = sub(r'\.', '_', scope)
            IName.scope(scope)
            ret_val = f(*args, **kwargs)
            IName.scope('')
            return ret_val

        return wrapper
    local.init_vars()
    return scope


def comment(comment: str):
    """Place comment to the result code
    comment will be placed if script docs attribute is set to True"""
    if not KSP.docs:
        return
    comm: Union[str, List[str]]
    if not KSP.indents:
        Output().put('{%s}' % comment)
        return
    # Output().put('{%s}' % cleandoc(comment))
    comm = cleandoc(comment).split('\n')
    new = comm[0]
    if len(comm) > 1:
        for line in comm[1:]:
            new += f'\n{" " * KSP.indents}{line}'
    Output().put('{%s}' % new)


F = TypeVar('F', bound=Callable[..., None])


def quick_script(f: F) -> F:

    @wraps(f)
    def wrapper(*args: Any, out=kScript.clipboard, **kwargs: Any) -> None:
        script = kScript(out,
                         compact=False,
                         max_line_length=False,
                         indents=2,
                         docs=True,)
        setattr(script, 'main', lambda: f(*args, **kwargs))
        script.compile()

    return cast(F, wrapper)


# class Collection:

#     def __init__(self, ref_type: Union[Type[int], Type[str], Type[float]],
#                  **sizes: kLoc):
#         if ref_type is int:
#             self.array_type = kArrInt
#             self.value_type = (int, kInt)
#         elif ref_type is str:
#             self.array_type = kArrStr
#             self.value_type = (str, kStr)
#         elif ref_type is float:
#             self.array_type = kArrReal
#             self.value_type = (float, kReal)
#         else:
#             raise TypeError(f'wrong type of the first arg: {ref_type}')
#         self.
#         for key, val in zip(items, items.values()):
#             if val._size == 1:
#                 i


# a = kArg(int)
# print(a.size())


class UiPage(kWidget):
    local = kLocals()

    # @scope
    def __init__(self, name: str, parent: object=None,
                 x: int=None, y: int=None,
                 width: int=None, height: int=None) -> None:
        super().__init__(parent=parent,
                         x=x,
                         y=y,
                         width=width,
                         height=height)
        self.name = name
        self.child_ids: kArrInt
        self.child_hide_state: kArrInt
        self._initialized: bool = False
        self.local.init_vars()
        self._is_hidden: kInt = kInt()

    def get_childs(self, widget: kWidget) -> List[KspNativeControl]:
        out = list()
        for child in widget.childs:
            if isinstance(child, KspNativeControl):
                out.append(child)
            out.extend(self.get_childs(child))
        return out

    def initialize(self) -> None:
        childs = self.get_childs(self)
        self.child_ids = kArrInt(name=f'{self.name}_child_ids')
        for child in childs:
            self.child_ids.append(child.id)
        # print(childs)
        if len(self.child_ids) == 0:
            self.child_ids.append(-1)
        self.child_hide_state = kArrInt([-1] * len(self.child_ids),
                                        name=f'{self.name}_child_hides',
                                        size=len(self.child_ids))

        self._initialized = True

    # @abstractmethod
    def show(self) -> None:
        ...

    @local('hide')
    def show_childs(self,
                    hide: kInt=0
                    ) -> None:
        assert self._initialized, 'not initialized'
        with If(self._is_hidden > 0):
            with For(len(self.child_ids)) as seq:
                for child in seq:
                    with If(self.child_hide_state[child] == -1):
                        hide <<= HIDE_PART_NOTHING
                    with Else():
                        hide <<= self.child_hide_state[child]
                    set_control_par(self.child_ids[child],
                                    CONTROL_PAR_HIDE,
                                    hide)
            self._is_hidden <<= -1

    # @abstractmethod
    def hide(self) -> None:
        ...

    def hide_childs(self) -> None:
        assert self._initialized, 'not initialized'
        with If(self._is_hidden <= 0):
            with For(len(self.child_ids)) as seq:
                for child in seq:
                    self.child_hide_state[child] <<= \
                        get_control_par(self.child_ids[child],
                                        CONTROL_PAR_HIDE)
                    set_control_par(self.child_ids[child],
                                    CONTROL_PAR_HIDE,
                                    HIDE_WHOLE_CONTROL)
            self._is_hidden <<= 1
