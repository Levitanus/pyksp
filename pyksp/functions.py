import typing as ty
import functools as ft
import inspect as it
import re
from enum import Enum

from . import abstract as ab
from . import stack as stc
from . import service_types as st
from . import base_types as bt

CT = ty.TypeVar("CT", bound=ty.Callable[..., None])
TDU = ty.Dict[type, ty.Union[type, ty.Tuple[type, ...]]]
types_dict: TDU = {
    # local vars
    st.LocInt: type(None),
    st.LocStr: type(None),
    st.LocFloat: type(None),
    st.LocArrInt: type(None),
    st.LocArrStr: type(None),
    st.LocArrFloat: type(None),
    # pseudo-local args
    bt.VarInt: (int,
                bt.ProcessInt),
    bt.VarStr: (str,
                bt.ConcatsStrings),
    bt.VarFloat: (float,
                  bt.ProcessFloat),
    bt.ArrInt: bt.ArrInt,
    bt.ArrStr: bt.ArrStr,
    bt.ArrFloat: bt.ArrFloat,
    # local args
    st.InInt: (int,
               bt.ProcessInt),
    st.InStr: (str,
               bt.Magic),
    st.InFloat: (float,
                 bt.ProcessFloat),
    st.InArrInt: bt.ArrInt,
    st.InArrStr: bt.ArrStr,
    st.InArrFloat: bt.ArrFloat,
    #  output args
    st.OutInt: bt.VarInt,
    st.OutStr: bt.VarStr,
    st.OutFloat: bt.VarFloat,
    st.OutArrInt: bt.ArrInt,
    st.OutArrStr: bt.ArrStr,
    st.OutArrFloat: bt.ArrFloat,
}


class Dest(Enum):
    basic = -1
    stack = 1
    local_var = 2
    out_var = 3


SD = ty.Dict[ty.Type, Dest]
dest_dict: SD = {
    # local vars
    st.LocInt: Dest.stack,
    st.LocStr: Dest.stack,
    st.LocFloat: Dest.stack,
    st.LocArrInt: Dest.stack,
    st.LocArrStr: Dest.stack,
    st.LocArrFloat: Dest.stack,
    # pseudo-local args
    bt.VarInt: Dest.local_var,
    bt.VarStr: Dest.local_var,
    bt.VarFloat: Dest.local_var,
    bt.ArrInt: Dest.local_var,
    bt.ArrStr: Dest.local_var,
    bt.ArrFloat: Dest.local_var,
    # local args
    st.InInt: Dest.stack,
    st.InStr: Dest.stack,
    st.InFloat: Dest.stack,
    st.InArrInt: Dest.stack,
    st.InArrStr: Dest.stack,
    st.InArrFloat: Dest.stack,
    #  output args
    st.OutInt: Dest.out_var,
    st.OutStr: Dest.out_var,
    st.OutFloat: Dest.out_var,
    st.OutArrInt: Dest.out_var,
    st.OutArrStr: Dest.out_var,
    st.OutArrFloat: Dest.out_var,
}


class FuncArgs:
    def __init__(self, func: CT, func_name: ab.NameVar) -> None:
        print('FuncArgs init')
        self.func_name = func_name
        self.sig = it.signature(func)
        self.arg_types: ty.Dict[str,
                                ty.Union[type,
                                         ty.Tuple[type,
                                                  ...]]] = dict()
        self.arg_sizes: ty.Dict[str, int] = dict()
        self.arg_dests: ty.Dict[str, Dest] = dict()
        self.cashed: ty.Dict[str, ty.Any] = dict()
        self.local_types: ty.Dict[str, bt.VarBase] = dict()

        if self.sig.return_annotation is not None:
            raise TypeError(
                'return has to be annotated to None (def foo() -> None:)'
            )

        parameters = self.sig.parameters
        for arg, par in zip(parameters, parameters.values()):
            anno = par.annotation
            print(anno)
            if anno is it.Parameter.empty and arg is not 'cls':
                raise TypeError(
                    'only first argument with arg "cls" can be not annotated'
                )
            if anno in types_dict:
                self.arg_types[arg] = types_dict[anno]
                if hasattr(anno, 'size'):
                    self.arg_sizes[arg] = anno.size
                self.arg_dests[arg] = dest_dict[anno]
                if dest_dict[anno] is Dest.local_var:
                    self.local_types[arg] = anno
                continue
            self.arg_dests[arg] = Dest.basic
            self.arg_types[arg] = anno

    def bound(
        self,
        stack: stc.Stack,
        *args: ty.Any,
        **kwargs: ty.Any
    ) -> it.BoundArguments:
        bound = self.sig.bind(*args, **kwargs)
        stack_vars: ty.Dict[str, stc.vars_u] = dict()
        for arg, value in zip(bound.arguments, bound.arguments.values()):
            if self.arg_dests[arg] is Dest.basic:
                self._check_cashed_basic(arg, value)
                continue
            if self.arg_dests[arg] is Dest.local_var:
                self._handle_local_var(arg, value, bound.arguments)
                continue
            if self.arg_dests[arg] is Dest.stack:
                self._check_stack_var(arg, value)
                print(arg, 'is dest.stack', value)
                stack_vars[arg] = value
                continue
        stck_ret = stack.push(*stack_vars.values())
        for idx, arg in enumerate(stack_vars):
            bound.arguments[arg] = stck_ret[idx]
        return bound

    def _check_cashed_basic(self, arg: str, value: ty.Any) -> None:
        if arg not in self.cashed:
            self.cashed[arg] = value
            return
        if self.cashed[arg] is not value:
            raise TypeError(
                'arg {arg} has to contain only value {value}'.format(
                    arg=arg,
                    value=self.cashed[arg]
                )
            )

    def _handle_local_var(
        self,
        arg: str,
        value: ty.Any,
        args: ty.MutableMapping
    ) -> None:
        raise NotImplementedError

    def _check_stack_var(self, arg: str, value: ty.Any) -> None:
        if not isinstance(value, self.arg_types[arg]):
            raise TypeError(
                'value of arg "{arg}" has to instance of {type_}'.
                format(arg=arg,
                       type_=self.arg_types[arg])
            )


class Function(ab.KSP):
    stack = stc.Stack('func')

    def __init__(self, func: CT) -> None:
        print('Function init')
        print(type(func), func)
        if isinstance(func, classmethod):
            print('is class method')
        self.func = func
        self.name: ab.NameVar = self._get_name(func)
        self.args = FuncArgs(func, self.name)
        # self.__call__ = ft.wraps(self.func)(self.__call__)
        self.obj: ty.Optional[object] = None

    def _get_name(self, func: CT) -> ab.NameVar:
        name = func.__qualname__
        name = re.sub(r'\.', '_', name)
        return ab.NameVar(name)

    def __get__(self, obj: object, cls: type) -> CT:
        self.obj = cls
        return ty.cast(CT, self.__call__)

    def __call__(self, *args: ty.Any, **kwargs: ty.Any) -> None:
        if self.obj:
            bound_args = self.args.bound(
                self.stack,
                self.obj,
                *args,
                **kwargs
            )
        else:
            bound_args = self.args.bound(self.stack, *args, **kwargs)
        return self.func(*bound_args.args, **bound_args.kwargs)


def func(f: CT) -> CT:
    return ty.cast(CT, Function(f))
