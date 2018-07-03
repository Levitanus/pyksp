import re
import inspect

from abstract import KspObject
from interfaces import IOutput
from stack import Stack

from native_types import kInt
from native_types import kStr
from native_types import kReal

# from native_types import kArrInt
# from native_types import kArrStr
# from native_types import kArrReal


class FuncArg:
    '''
    Handles inspected arguments of decorated function
    '''

    def __init__(self, val, cls, default, name=None):
        self.name = name
        if not name:
            self.name = val
        self.val = val
        self.cls = cls
        self.default = default


class FuncArgs:

    def __contains__(self, key):
        if key in self.__named:
            return True
        return False

    def __getitem__(self, key):
        if key not in self.__named:
            raise IndexError('There no %s in %s arguments' %
                             (key, self.name))
        return self.__named[key]


class Func(KspObject):
    '''
    class-based decorator, implements KSP functions
    usage:
        @Func
        def Foo(*args, **kwargs):
            pass

    TODO:
        implement stack
        implement function for calling functions by id
    '''

    size = 32768
    stack_int = Stack('native_func_int',
                      size, kInt, 100)
    stack_str = Stack('native_func_str',
                      size, kStr, 100)
    stack_real = Stack('native_func_real',
                       size, kReal, 100)

    def __init__(self, func, **kwargs):

        self.code = list()
        self.func = func
        full_name = self.get_func_name()
        super().__init__(full_name)

        self.args = self.build_args()

    def build_args(self):
        args = list()
        sig = inspect.signature(self.func)
        for par in sig.parameters:
            par_class = sig.parameters[par].annotation
            if par_class is inspect._empty:
                raise TypeError('''arg %s is wrong:
                arguments of KSP functions has to be
                strongly typed with ":" symbol and class''' % par)
            par_default = sig.parameters[par].default
            # print(par, par_class, par_default)
            args.append(FuncArg(par, par_class, par_default))
        return args

    def get_func_name(self):
        re_name = re.compile(
            r'(?:<function )([a-zA-Z_][\.a-zA-Z0-9_]*\b)')
        name = repr(self.func)
        # print(name)
        # name = re.sub(r'.*functions', '', name)
        name = re.sub('.<locals>', '', name)
        m = re.match(re_name, name)
        if m:
            name = m.group(1)
        name = self.func.__module__ + name
        name = re.sub(r'\.', '__', name)
        return name

    def __call__(self, *args, inline: bool=False, **kwargs):
        self.check_args(*args, **kwargs)
        print('args are:', args, 'kwargs are:', kwargs)
        blocked = False
        if inline:
            try:
                IOutput.set(self.code)
            except IOutput.IsSetError:
                blocked = True
            finally:
                out = self.func(*args, **kwargs)
            if blocked is False:
                IOutput.release()
                return out
        return self.called(*args, **kwargs)

    def check_args(self, *args, **kwargs):
        arguments = list()
        for arg in args:
            arguments.append(arg)
        for idx, arg in enumerate(arguments):
            if not isinstance(arg, self.args[idx].cls):
                raise TypeError(
                    'arg %s is %s, has to be %s' % (
                        self.args[idx].name,
                        type(arg),
                        self.args[idx].cls))
        for arg, val in kwargs.items():
            arguments.append(val)

    def called(self, *args, **kwargs):
        self.__push_args(*args, **kwargs)

        IOutput.put('call %s' % self.name())
        IOutput.lock()
        out = self.func(*args, **kwargs)
        IOutput.unlock()
        return out

    def __push_args(self, *args, **kwargs):
        self.update_args(*args, **kwargs)
        l_int = list()
        l_str = list()
        l_real = list()

    def update_args(self, *args, **kwargs):
        for idx, val in enumerate(args):
            self.args[idx].val = val
        for key, val in kwargs.items():
            for arg in self.args:
                if arg.name == key:
                    arg.val == val
