import re

from inspect import signature
from inspect import Parameter as ipar
from inspect import Signature
from inspect import _empty

from warnings import warn

from abstract import KspObject
from interfaces import IOutput
# from interfaces import IName

from stack import Stack
from stack import kLocal

from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal
from native_types import KspNative

from dev_tools import native_from_input
from dev_tools import native_from_input_obj
from dev_tools import ref_type_from_input_class
from dev_tools import SingletonMeta
# from dev_tools import expand_if_callable


not_native_type_msg = \
    '''Annotation of arg {arg} is of type {curr_type}.
For using function without inline parameter set to True (KSP call)
has to be one of: {types_list}.
Otherway it raises exception on call'''


class FuncArg:

    def __init__(self, name, par):
        self._name = name

        self._par = par
        if isinstance(par.default, kLocal):
            self.ref_type = kLocal
        else:
            self.ref_type = self._pars_annotation(par.annotation)
        self.default = par.default

    def _pars_annotation(self, anno):
        if anno is ipar.empty:
            raise AttributeError(
                '''arguments of KSP functions has to
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
                if ref is kLocal:
                    raise AttributeError(
                        f'arg {arg} is local and can not be assigned')
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


class FuncStackCall:

    def __init__(self):
        self.int = 0
        self.str = 0
        self.real = 0


class FuncStack:

    def __init__(self, name, size, max_recursion):
        self.stack_int = Stack(f'{name}_int',
                               size, kInt, max_recursion)
        self.stack_str = Stack(f'{name}_str',
                               size, kStr, max_recursion)
        self.stack_real = Stack(f'{name}_real',
                                size, kReal, max_recursion)
        self.calls = list()

    def push(self, **kwargs):
        int_vars = dict()
        str_vars = dict()
        real_vars = dict()
        for arg, val in kwargs.items():
            if isinstance(val, KspNative):
                ref = native_from_input_obj(val)
            elif isinstance(val, kLocal):
                ref = native_from_input(val.ref_type)
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
        self.calls.append(FuncStackCall())
        call = self.calls[-1]
        if len(int_vars) > 0:
            call.int = len(int_vars)
            self.stack_int.push(**int_vars)
            int_frame = self.stack_int.peek()
        if len(str_vars) > 0:
            call.str = len(str_vars)
            self.stack_str.push(**str_vars)
            str_frame = self.stack_str.peek()
        if len(real_vars) > 0:
            call.real = len(real_vars)
            self.stack_real.push(**real_vars)
            real_frame = self.stack_real.peek()
        return int_frame, str_frame, real_frame

    def pop(self):
        call = self.calls.pop()
        if call.int > 0:
            self.stack_int.pop()
        if call.str > 0:
            self.stack_str.pop()
        if call.real > 0:
            self.stack_real.pop()

    def IsEmpty(self):
        return len(self.calls) == 0


def _func_name(func):
    re_name = re.compile(
        r'(?:<function )([a-zA-Z_][\.a-zA-Z0-9_]*\b)')
    name = repr(func)
    name = re.sub('.<locals>', '', name)
    m = re.match(re_name, name)
    if m:
        name = m.group(1)
    name = func.__module__ + name
    name = re.sub(r'\.', '__', name)
    return name


class FuncReturn:

    def __init__(self, func):
        sig = signature(func)
        if sig.return_annotation is _empty:
            self.return_type = None
        else:
            self.return_type = \
                ref_type_from_input_class(
                    sig.return_annotation)

    def _raise(self, val):
        raise AttributeError(
            f'return value is "{val}" ({type(val)}). ' +
            f'Has to be instance of {self.return_type}')

    def check(self, val):
        if self.return_type is None:
            if val is None:
                return True
            raise AttributeError(
                f'return value is "{val}". Has to be None')
        if isinstance(val, self.return_type):
            return True
        raise AttributeError(
            f'return value is "{val}" ({type(val)}). ' +
            f'Has to be instance of {self.return_type}')


class CallStack:

    _stack = list

    @staticmethod
    def append(seq):
        Stack._stack.append(seq)

    @staticmethod
    def put(func):
        for item in Stack._stack:
            item.add(func)

    @staticmethod
    def pop():
        Stack._stack.pop()


class Func(KspObject):

    stack_size = 1000000
    stack_depth = 100
    _stack = None
    _instances = list()

    def __init__(self, func):
        name = _func_name(func)
        super().__init__(name)
        if Func._stack is None:
            Func._stack = FuncStack('func',
                                    Func.stack_size,
                                    Func.stack_depth)
        self.stack = Func._stack
        self.func = func
        self.args = FuncArgs(func)
        self.return_type = FuncReturn(func)
        self.call_stack = set()
        Func._instances.append(self)

    def __call__(self, inline=False, **kwargs):
        if not inline:
            return self._called(**kwargs)

    def _called(self, **kwargs):
        CallStack.put(self)
        CallStack.append(self.call_stack)

        CallStack.pop()
