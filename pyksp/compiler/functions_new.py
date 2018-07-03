import re

from inspect import signature
from inspect import Parameter as ipar
from inspect import Signature

from warnings import warn

from abstract import KspObject
from interfaces import IOutput
from stack import Stack

from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal

from dev_tools import native_from_input
from dev_tools import native_from_input_obj
from dev_tools import SingletonMeta


not_native_type_msg = \
    '''Annotation of arg {arg} is of type {curr_type}.
For using function without inline parameter set to True (KSP call)
has to be one of: {types_list}. Otherway it raises exception on call'''


class FuncArg:

    def __init__(self, name, par):
        self._name = name
        self._par = par
        self.ref_type = self._pars_annotation(par.annotation)
        self.default = par.default

    def _pars_annotation(self, anno):
        if anno is ipar.empty:
            raise AttributeError('''arguments of KSP functions has to
                be strongly typed with ":" symbol and class''')
        available = (int, kInt, kArrInt, str, kStr, kArrStr,
                     float, kReal, kArrReal)
        if anno not in available:
            warn(not_native_type_msg.format(
                arg=self._name,
                curr_type=anno,
                types_list=available),
                FuncArg.warn, 4)
            return anno
        ref = native_from_input(anno)
        if anno is not ref:
            ref = (anno, ref)
        return ref

    class warn(Warning):
        pass


class FuncArgs:

    def __init__(self, func):
        self._args = dict()

        self._sig = signature(func)
        for name, par in self._sig.parameters.items():
            arg = FuncArg(name, par)
            self._args[name] = arg

    def check_args(self, *args, **kwargs):
        pasted = self._sig.bind(*args, **kwargs).arguments
        for arg, val in pasted.items():
            ref = self._args[arg].ref_type
            if not isinstance(val, ref):
                raise TypeError(
                    f'arg {arg} is {type(val)} ' +
                    f'has to be {ref}')

    def return_full(self, *args, **kwargs):
        self.check_args(*args, **kwargs)
        pasted = self._sig.bind(*args, **kwargs).arguments
        newargs = dict()
        for arg, val in self._args.items():
            if arg in pasted:
                newargs[arg] = pasted[arg]
                continue
            newargs[arg] = val.default
        return newargs


class FuncStack:

    def __init__(self, name, size, max_recursion):
        self.stack_int = Stack(f'{name}_int',
                               size, kInt, max_recursion)
        self.stack_str = Stack(f'{name}_str',
                               size, kStr, max_recursion)
        self.stack_real = Stack(f'{name}_real',
                                size, kReal, max_recursion)

    def push(self, **kwargs):
        int_vars = dict()
        str_vars = dict()
        real_vars = dict()
        for arg, val in kwargs.items():
            ref = native_from_input_obj(val)
            if ref is kInt or ref is kArrInt:
                int_vars[arg] = val
            if ref is kStr or ref is kArrStr:
                str_vars[arg] = val
            if ref is kReal or ref is kArrReal:
                real_vars[arg] = val
        int_frame, str_frame, real_frame =\
            self._push_sep_dicts(int_vars, str_vars, real_vars)
        out_vars = list()
        for arg, val in kwargs.items():
            if arg in int_vars:
                out_vars.append(int_frame[arg])
            if arg in str_vars:
                out_vars.append(str_frame[arg])
            if arg in real_vars:
                out_vars.append(real_frame[arg])
        return out_vars

    def _push_sep_dicts(self, int_vars, str_vars, real_vars):
        int_frame, str_frame, real_frame = None, None, None
        if len(int_vars) > 0:
            self.stack_int.push(**int_vars)
            int_frame = self.stack_int.peek()
        if len(str_vars) > 0:
            self.stack_str.push(**str_vars)
            str_frame = self.stack_str.peek()
        if len(real_vars) > 0:
            self.stack_real.push(**real_vars)
            real_frame = self.stack_real.peek()
        return int_frame, str_frame, real_frame
