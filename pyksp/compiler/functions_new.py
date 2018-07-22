import re
import functools
# from collections import OrderedDict

from inspect import signature
from inspect import Parameter as ipar
# from inspect import Signature
# from inspect import _empty

from warnings import warn

from abstract import KspObject
from abstract import KSP
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
# from dev_tools import ref_type_from_input_class
# from dev_tools import SingletonMeta
# from dev_tools import expand_if_callable

from pyksp_ast import AstGetItem


not_native_type_msg = \
    '''Annotation of arg {arg} is of type {curr_type}.
For using function without inline parameter set to True (KSP call)
has to be one of: {types_list}.
Otherway it raises exception on call'''


class FuncArg:

    def __init__(self, name, par):
        self._name = name

        if name == 'self':
            return
        self._par = par
        self.default = par.default
        self.is_out = False
        #     self.ref_type =
        if isinstance(par.annotation, kOut):
            self.ref_type = par.annotation.ref_type
            self.is_out = True
            return
        if isinstance(par.default, kLocal):
            self.ref_type = kLocal
        else:
            self.ref_type = self._pars_annotation(par.annotation)

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
        self.has_self = False

        self._sig = signature(func)
        for name, par in self._sig.parameters.items():
            if name == 'self':
                self.has_self = True
            arg = FuncArg(name, par)
            self._args[name] = arg

    def check_args(self, *args, **kwargs):
        pasted = self._sig.bind(*args, **kwargs).arguments
        for arg, val in pasted.items():
            if arg == 'self':
                continue
            ref = self._args[arg].ref_type
            if not isinstance(val, ref):
                if ref is kLocal:
                    raise AttributeError(
                        f'arg {arg} is local and can not be assigned')
                raise TypeError(
                    f'arg {arg} is {type(val)} ' +
                    f'has to be {ref}')

    def return_full(self, *args, check=True, **kwargs):
        if check:
            self.check_args(*args, **kwargs)
        pasted = self._sig.bind(*args, **kwargs).arguments
        newargs = dict()

        try:
            obj = pasted['self']
        except KeyError:
            obj = None
        for arg, val in self._args.items():
            if arg == 'self':
                continue
            if arg in pasted:
                newargs[arg] = pasted[arg]
                continue
            newargs[arg] = val.default
        return obj, newargs

    def get_outs(self, args, pushed):
        # if 'self' in pushed:
        #     del pushed['self']
        pasted = self._sig.bind(self, *pushed).arguments
        # print('get_outs. pasted =', pasted)

        for key in pasted:
            if key == 'self':
                continue
            arg = self._args[key]
            val = args[key]
            var = pasted[key]
            if arg.is_out:

                val(var())


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
            if isinstance(val, (KspNative, int, str, float)):
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


class CallStack:

    _stack = list()

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


class kOut:

    def __init__(self, val, size=1):
        self.size = size
        ref = val
        self.var = kLocal(ref, size)
        # self.name = name
        self.ref_type = self.var.ref_type
        self.ref_type = native_from_input(self.ref_type)
        if self.size > 1:
            if self.duck_type is kInt:
                self.duck_type = kArrInt
            if self.duck_type is kStr:
                self.duck_type = kArrStr
            if self.duck_type is kReal:
                self.duck_type = kArrReal

    def check(self, val):
        if not self._duck_type(val):
            raise TypeError(
                f'out arg "{self.name}" is <{val}> ({type(val)}). ' +
                'has to be instance of ' +
                f'{self.duck_type}')
        return True

    def _duck_type(self, val):
        if isinstance(val, self.duck_type):
            return True
        if self.size == 1 and isinstance(val, AstGetItem):
            if self.duck_type is kInt:
                if isinstance(val.args[0], kArrInt):
                    return True
            if self.duck_type is kStr:
                if isinstance(val.args[0], kArrStr):
                    return True
            if self.duck_type is kReal:
                if isinstance(val.args[0], kArrReal):
                    return True


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
        # self.ret = FuncReturn(func)
        self.call_stack = set()
        self.used_in_call = False
        Func._instances.append(self)

    def __call__(self, *args, inline=False, **kwargs):
        if inline is False:
            return self._called(*args, **kwargs)
        return self._inlined(*args, **kwargs)

    def _inlined(self, *args, **kwargs):
        obj, args = self.args.return_full(*args, **kwargs)
        print(obj, args, sep='|: ')
        # pushed_vars = self.stack.push(**args)
        # IOutput.put(f'call {self.name()}')
        if obj:
            out = self.func(obj, **args)
        else:
            out = self.func(*args)
        # args = self.args.get_outs(args, pushed_vars)

        # self.stack.pop()
        return out

    def _called(self, *args, **kwargs):
        out = None
        self.used_in_call = True
        obj, args = self.args.return_full(*args, **kwargs)
        pushed_vars = self.stack.push(**args)
        IOutput.put(f'call {self.name()}')
        if KSP.is_under_test():
            if obj:
                out = self.func(obj, *pushed_vars)
            else:
                out = self.func(*pushed_vars)
        args = self.args.get_outs(args, pushed_vars)

        self.stack.pop()
        return out

    def __get__(self, instance, instancetype):
        """Implement the descriptor protocol to make decorating
        instance method possible.
        """

        # Return a partial function with the first argument
        # is the instance of the class decorated.
        if instance is None:
            return self
        # print(self, instance, instancetype)
        return functools.partial(self.__call__, instance)
