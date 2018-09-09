from inspect import signature
from inspect import Parameter as ipar
from collections import OrderedDict
import re

from functools import wraps

from stack import MultiStack
from stack import kLoc

from abstract import KSP
from abstract import Output
from abstract import SingletonMeta
from abstract import KspObject

from base_types import KspIntVar
from base_types import KspStrVar
from base_types import KspRealVar
from base_types import KspArray

from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal

from k_built_ins import FunctionCallback


class kOut(KSP):
    '''special class designed to be function argument to return
        values from it.
    will be used as local var if nothing has passed as value
    within function invocation.
    ref_type has to be one of (int, str, float)
    '''

    def __init__(self, ref_type: (int, str, float), size: int=None):
        self.__ref_type = self._get_ref_type(ref_type)
        self.__size = size

    @staticmethod
    def _get_ref_type(ref_type):
        '''returns KspIntVar, KspStrVar or KspRealVar depends on
        pasted class'''
        if ref_type in (int, KspIntVar):
            return KspIntVar
        if ref_type in (str, KspStrVar):
            return KspStrVar
        if ref_type in (float, KspRealVar):
            return KspRealVar
        raise TypeError(f"can't resolve ref_type. pasted {ref_type}")

    def check(self, variable):
        '''checks if variable can be passed as argument
        returns True or None'''
        if self.__size:
            if not isinstance(variable, KspArray):
                raise TypeError(f"has to be {KspArray} instance")
            if len(variable) != self.__size:
                raise IndexError('size of array is not equal to size ' +
                                 'of out array')
        else:
            if isinstance(variable, KspArray):
                raise TypeError('can not be array')
        try:
            if self.__ref_type not in variable.ref_type:
                raise TypeError('Variable has to be able to accept ' +
                                f'{self.__ref_type} instances')
        except AttributeError:
            raise TypeError('Variable has to be able to accept ' +
                            f'{self.__ref_type} instances')
        return True

    @property
    def ref_type(self):
        '''returns one of (int, str, float)'''
        return self.__ref_type

    @property
    def size(self):
        '''returns int size of var'''
        if not self.__size:
            return 1
        return self.__size


class kArg(KSP):
    '''Special class designed to be annotation of function argument
    if size is specified, KspArray of length of size is expected as arg
    '''

    def __init__(self, ref_type: (int, str, float), size: int=None):
        self.__refs = (int, str, float)
        self.__size = size
        if not size:
            self.__ref_type = self._single_ref(ref_type)
            return
        if ref_type not in (kArrInt, kArrStr, kArrReal, int, str, float):
            raise TypeError(f'ref_type can be only one of {self.__refs}')
        self.__ref_type = self._single_ref(ref_type)

    def _single_ref(self, ref_type):
        '''makes tuple of accepted types from arg'''
        if ref_type is int:
            return (int, KspIntVar)
        if ref_type is str:
            return (str, KspStrVar)
        if ref_type is float:
            return (float, KspRealVar)
        raise TypeError(f'ref_type can be only one of {self.__refs}')

    @property
    def ref_type(self):
        '''returns tuple of types, can be used for
        comparisson with array ref_type'''
        return self.__ref_type

    @property
    def size(self):
        '''returns size, if specified, otherwise None'''
        return self.__size


class FuncArg:
    '''contains one argument of function in the way,
    close to what inspect.Parameter class does
    '''

    def __init__(self, par: ipar):
        self._par = par

        self._is_out = None
        self.__size = None
        self.__ref_type = None

        self._default = par.default
        self._is_local = self._check_if_local(par)
        if self._is_local:
            return
        self._is_out = self._check_if_out(par)
        if self._is_out:
            return
        self.__size = None
        self.__ref_type = self._get_ref_type(par.annotation)
        if self._default != ipar.empty:
            self.check(self._default)
            return
        self._default = None

    def _check_if_local(self, par):
        '''returns True if argument default is kLoc
        raises TypeError if kLoc used as annotation'''
        if isinstance(par.default, kLoc):
            return True
        if isinstance(par.annotation, kLoc):
            raise TypeError(
                f'{kLoc} object has to be set as default value of arg')

    def _check_if_out(self, par):
        '''returns True if argument default is kOut
        raises TypeError if kOut used as annotation'''
        if isinstance(par.default, kOut):
            return True
        if isinstance(par.annotation, kOut):
            raise TypeError(
                f'{kOut} object has to be set as default value of arg')

    def _get_ref_type(self, anno):
        '''returns tuple of acessible types based on annotation'''
        if anno is ipar.empty:
            raise AttributeError(
                f'''arguments of KSP functions has to
                be strongly typed with ":" symbol and class
                attribute name is "{self._par.name}"''')
        if anno in (int, kInt, KspIntVar):
            return (int, KspIntVar)
        if anno in (str, kStr, KspStrVar):
            return (str, KspStrVar)
        if anno in (float, kReal, KspRealVar):
            return (float, KspRealVar)
        if isinstance(anno, kArg):
            if anno.size:
                self.__size = anno.size
            return anno.ref_type
        raise TypeError(
            f'if You wanna no problems use {kArg} for annotation.' +
            f'pasted {anno}')

    @property
    def is_local(self):
        '''returns True if default value is kLoc'''
        return self._is_local

    @property
    def is_out(self):
        '''returns True if default value is kOut'''
        return self._is_out

    @property
    def ref_type(self):
        '''returns tuple of types'''
        return self.__ref_type

    @property
    def size(self):
        '''returns size if specified'''
        return self.__size

    @property
    def default(self):
        '''returns default value of an argument'''
        return self._default

    @property
    def name(self):
        '''returns name of param, as kwargs dict does'''
        return self._par.name

    def check(self, value):
        '''returns default value, or pasted argument
        raises TypeError if value is of wrong type, or
        default value is instance of kLoc'''
        name = self._par.name
        if self._is_local:
            raise TypeError(f'arg "{name}" can not be assigned.' +
                            ' Use it inside func')
        if self._is_out:
            self._default.check(value)
            return value
        if self.__size:
            return self._check_array(value)
        if not isinstance(value, self.__ref_type):
            raise TypeError(
                f'value of "{name}" is of wrong type ' +
                f'({type(value)}) has to be instance of ' +
                f'{self.__ref_type}')
        return value

    def _check_array(self, value: KspArray):
        '''checks if pasted value is instance of KspArray
        and checks ref_type of the array
        returns value, or raises TypeError'''
        name = self._par.name
        if not isinstance(value, KspArray):
            raise TypeError(
                f'arg "{name}" has to be instance of {KspArray}')
        if int in self.__ref_type:
            ref = int
        if str in self.__ref_type:
            ref = str
        if float in self.__ref_type:
            ref = float
        if ref not in value.ref_type:
            raise TypeError(
                f'{ref} is not accepted as value of array, ' +
                f'passed to "{name}"')
        return value


class FuncArgs(KSP):
    '''collects arguments of function and veryfies their annotations
    and default arguments'''

    def __init__(self, func):
        self._func = func
        self._sig = signature(func)
        self._args = list()
        for name, par in self._sig.parameters.items():
            if name == 'self':
                continue
            self._args.append(FuncArg(par))

    @property
    def args(self):
        '''returns list of FuncArg objects'''
        return self._args

    def map(self, *args, **kwargs):
        '''maps pasted arguments to self args
        returns tuplpe (self, mapped, outs) where:
            self is bounded object, or None
            mapped is dict of all args to be pasted
            outs dict of args, has to be reassigned after
                the function invocation
        '''
        args = self._sig.bind(*args, **kwargs).arguments
        maped = dict()
        outs = dict()
        for arg in self._args:
            if arg.name in args:
                val = arg.check(args[arg.name])
                maped[arg.name] = val
                if arg.is_out:
                    outs[arg.name] = val
                continue
            if arg.is_out:
                val = arg.default
                maped[arg.name] = kLoc(val.ref_type, val.size)
                continue
            maped[arg.name] = arg.default
        if 'self' in args:
            f_self = args['self']
        else:
            f_self = False
        return f_self, maped, outs


class FuncCallsStack:
    '''used for sorting functions during generating their executables'''
    stack = list()

    @staticmethod
    def append(seq: set):
        '''puts set to stack.
        later usage of put method will put functions
        to every set of stack items'''
        FuncCallsStack.stack.append(seq)

    @staticmethod
    def put(func):
        '''puts function to every stack item'''
        for item in FuncCallsStack.stack:
            item.add(func)

    @staticmethod
    def pop():
        '''returns last item in stack and removes it'''
        FuncCallsStack.stack.pop()


class FuncStack(metaclass=SingletonMeta):
    '''declares MultiStack object with name "functions" if not declared
    yet. can be used as descriptor'''
    size = 32000

    def __init__(self):
        self._stack = MultiStack('functions', FuncStack.size)
        self._init_lines = self._stack._init_lines

    def __get__(self, obj, cls):
        return self._stack

    def refr(self):
        self._stack = MultiStack('functions', FuncStack.size)


class Function(KspObject):
    '''keeps function, passed as argument of @foo decorator'''
    _functions = dict()
    _sored = False

    def __init__(self, func):
        check = self._check_func(func)
        if check:
            return check
        self._func = func
        name = self._get_func_name(func)
        super().__init__(name, has_init=False, has_executable=True)
        self.__args = FuncArgs(self._func)
        self._cashed_args = None
        self._called = False
        self._call_stack = set()

    @property
    def called(self):
        '''returns True if at least one invocation was used without
        additional argument inline'''
        return self._called

    @called.setter
    def called(self, val):
        '''setter for called'''
        self._called = val

    @property
    def args(self):
        '''returns FuncArgs object, initialized with
        arguments of function'''
        return self.__args

    def cash_args(self, args):
        '''cash args consists of items of Stack arrays
        used for correct naming of args during generation of
        executables'''
        if self._cashed_args:
            return
        self._cashed_args = args

    @staticmethod
    def _get_key(func):
        '''return sting representation of func to be used as key
        in Function._functions dict'''
        return repr(func)

    def _check_func(self, func):
        '''check if function exsists in Function._functions'''
        cls = self.__class__
        key = self._get_key(func)
        if key in cls._functions.keys():
            return cls._functions[key]
        cls._functions[key] = self

    @staticmethod
    def _get_func_name(func):
        '''return name, based on module and name of function'''
        re_name = re.compile(
            r'(?:<function )([a-zA-Z_][\.a-zA-Z0-9_]*\b)')
        name = repr(func)
        # name = re.sub(r'.*functions', '', name)
        name = re.sub('.<locals>', '', name)
        m = re.match(re_name, name)
        if m:
            name = m.group(1)
        name = func.__module__ + name
        name = re.sub(r'\.', '__', name)
        return name

    def _generate_init(self):
        '''raises RuntimeError'''
        raise RuntimeError('can not generate init')

    def _generate_executable(self):
        '''invocates once per all Function objects
        returns list of lines with sorted bodies of all
        functions, that were invocated without inline arg'''
        if not self.called:
            return []
        cls = self.__class__
        if cls._sored:
            return []
        # collect all lines of functions bodies to dict
        # with the same keys as in Function._function
        inits = dict()
        for key, func in cls._functions.items():
            inits[key] = func._generate_ex_proxy()

        # sorting of functions
        cls._sored = list()
        for key in Function._functions.keys():
            instance = Function._functions[key]
            if not instance.called:
                continue
            if len(instance._call_stack) == 0:
                cls._sored.append(instance)
                continue
            if instance in instance._call_stack:
                raise Exception('recursion detected inside' +
                                f'{instance.name()}')
            for func in instance._call_stack:
                if func not in cls._sored:
                    cls._sored.append(func)
                    Function._functions[key]
                continue
            cls._sored.append(instance)

        # generating executable block
        out = list()
        for inst in cls._sored:
            key = self._get_key(inst._func)
            out.extend(inits[key])
            out.append('')
        return out

    def _generate_ex_proxy(self):
        '''generates lines of function body, wraped in the
        function <name>
        end function
        lines'''
        if not self.called:
            return []
        out = list()
        otpt = Output()

        otpt.blocked = True
        args = self._cashed_args[0]
        passed = self._cashed_args[1]
        FuncStack().push(*args)
        otpt.blocked = False

        FunctionCallback.open()
        otpt.set(out)
        otpt.put(f'function {self.name()}')

        self._func(**passed)

        otpt.put('end function')
        Output().release()
        FunctionCallback.close()

        otpt.blocked = True
        FuncStack().pop()
        otpt.blocked = False
        return out

    @staticmethod
    def get_func_name(func):
        '''returns function name, if it was wraped by @func'''
        re_method = re.compile(
            r'(?:<bound method )([a-zA-Z_][\.a-zA-Z0-9_]*\b)')
        re_func = re.compile(
            r'(?:<function )([a-zA-Z_][\.a-zA-Z0-9_]*\b)')
        name = repr(func)
        # return name
        # name = re.sub(r'.*functions', '', name)
        name = re.sub('.<locals>', '', name)
        m = re.match(re_method, name)
        if m:
            name = m.group(1)
        elif re.match(re_func, name):
            name = re.match(re_func, name).group(1)
        name = func.__module__ + name
        name = re.sub(r'\.', '__', name)

        for key, f in Function._functions.items():
            if f.name.full == name:
                return f.name()

    @staticmethod
    def refresh():
        Function._functions = dict()
        Function._sored = False


def func(f):
    '''wraps function to be used as KSP object
    function can be called with additional argument
        "inline=True" to be placed directly inside the code
    All arguments (except of self, if method is being wrapped)
    has to be annotated with types of expecting arguments, as it
    expected by mypy.

    Annotations can be as simple: int, str, float
    as well as objects of special classes kArg, kLoc, kOut
    reccomended to use kArg instead of (int, str, float)

    kArg used as annotation. the first argument has to be
        (int, str or float) and the second argument tells that KspArray
        with the specified size is expected
    kLoc used as default value of an argument. as kArg, type is requeired
        and size is optional. inside the function attribute can be used
        as native KspArray or KspVar
    kOut used as defaul argument and has the same notation as kLoc
        and kArg, but it can not accept basic int, str or float objects.
        returns the last assigned value to the passed KspVar instead

    You can use return statement, but it will not be counted during
    code generation

    I suggest to start from the native python functions for quick
    prototyping, and wrap them only if You need true local variables
    or want to call them without placing to the code entirely.
    '''

    _func_stack = FuncStack()
    _f_obj = Function(f)

    fargs = _f_obj.args

    @wraps(f)
    def wrapper(*a, inline=False, **kv):
        f_self, maped, outs = fargs.map(*a, *kv)
        odict = OrderedDict(**maped)
        args = list()
        for arg, val in odict.items():
            args.append(val)
        args = _func_stack.push(*args)

        passed = dict()
        for arg, name in zip(args, odict):
            passed[name] = arg
        _f_obj.cash_args((args, passed))
        if f_self:
            passed['self'] = f_self
        blocked = None
        if not inline and not KSP.in_init():
            FuncCallsStack.put(_f_obj)
            FuncCallsStack.append(_f_obj._call_stack)
            _f_obj.called = True
            Output().put(f'call {_f_obj.name()}')
            FunctionCallback.open()
            if not Output().blocked:
                Output().blocked = True
                blocked = True
        out = f(**passed)
        if not inline and not KSP.in_init():
            if _f_obj in _f_obj._call_stack:
                raise Exception(f'recursive call of {_f_obj} detected')
            FuncCallsStack.pop()
            FunctionCallback.close()
        if blocked:
            Output().blocked = False
        if outs:
            for name, val in outs.items():
                maped[name] <<= passed[name]
        _func_stack.pop()
        return out
    return wrapper
