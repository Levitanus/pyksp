"""While and For loops.
For handle KSP loops use context managers:

Range loops
-----------
with For(start: int [, stop: int[, step: int]]) as name:
    for val in name:
        # code

ForEach loops
-------------
with For(arr: KspNativeArray=iterable) as name:
    for val in name:
        # code

While loops
-----------
with While() as w:
    while w(condition: bool):
        # code

within For() loops Brake() function can be used:
Example
-------
with For(arr=self.arrX) as seq:
    for val in seq:
        self.x(val)
        with For(arr=arrY) as seq_y:
            for val2 in seq_y:
                with If(self.x == val2):
                    check()
                    y(val2)
                with Else():
                    check()
                    Break()
"""
from context_tools import KspCondBrake
from context_tools import KspCondError

from interfaces import IOutput
from pyksp_ast import AstBool
from pyksp_ast import AstGetItem
# from pyksp_ast import AstGetItem
from abstract import KSP
from abstract import KspObject
from abstract import Singleton

from dev_tools import expand_if_callable

from native_types import kInt
from native_types import KspNativeArray


@Singleton
class ForLoops(KspObject):
    '''Handles names and indexes of ForEach and ForRange loops.
    Singleton.

    maxlen can be assigned at the initialization (max amount of
    simultaneously running for-loops. default=20)
    '''

    def __init__(self, maxlen=20):
        super().__init__('for_loops')
        # self.name = '%_for_loop_idx'
        self.name = self.name_func
        self.idx = '$_for_loop_curr_idx'
        self.maxlen = maxlen

    def name_func(self):
        return '%_for_loop_idx'

    def _generate_init(self):
        init_lines = list()
        init_lines.append(f'declare {self.name}[{self.maxlen}]')
        init_lines.append(f'declare {self.idx} := -1')

        return init_lines

    def get_idx(self):
        '''puts in output inc of idx-var, returns string within
        idx-array[idx-var]
        Under tests returns int index var'''
        if KSP.is_under_test():
            i = 0
            return i
        IOutput.put(f'inc({self.idx})')
        # return f'{self.name}[{self.idx}]'
        return AstGetItem(self, self.idx)

    def end(self):
        '''puts in output dec(idx-var) line'''
        IOutput.put(f'dec({self.idx})')


for_wrong_syntax_msg = '''Wrong syntax.
Syntax for for-each loops
-------------------------
with For(arr: KspNativeArray=[seq]) as name:
    for val in name:
        # code

Syntax for range loops
----------------------
with For(start: int, [stop: int, [step: int]]) as name:
    for val in name:
        # code
'''
for_wrong_arg_msg = 'Wrong syntax. See how range() func works'
for_type_err_msg = 'arg {name} is {arg_typ}. \
has to be one of {classes}'


class For(KSP):
    """For loop can be translated to KSP.
    works as python foreach: 'for val in Iterable' as well as
    range: 'for val in range(start, [stop, [step]])'

    As While, If, Else, Select and Case, it's context manager.

    Returns
    -------
    iteration generator

    Raises
    ------
    KspCondError

    ForRange syntax
    ---------------
    with For(start: int[, stop: int[, step: int]]) as seq:
        for val in seq:
            # code

    ForEach syntax
    --------------
    with For(arr: KspNativeArray=array) as seq:
        for val in seq:
            # code

    See Also
    --------
    Break()
    """

    def __init__(self, start: int=None, stop: int=None,
                 step: int=None, arr: KspNativeArray=None,
                 enumerate=False):
        self.__master = ForLoops()
        self.__idx = expand_if_callable(self.__master.get_idx())
        if self.__is_foreach(arr, start, stop, step):
            self.enumerate = enumerate
            return
        if enumerate:
            raise AttributeError(
                'enumerate par accesible only in for_each loop')
        self.__duck_typing(start, stop, step)
        self.__func = self.__range_handler
        args = list()
        args.append(start)
        if stop:
            args.append(stop)
        if step:
            args.append(step)
        self.__args = args
        self.__start, self.__stop, self.__step = self.__parse_args()

    def __is_foreach(self, arr, start, stop, step):
        '''Returns True if arr is only argument'''
        if arr:
            if start or stop or step:
                raise KspCondError(for_wrong_syntax_msg)
            if not isinstance(arr, KspNativeArray):
                raise KspCondError(
                    'For loop accepts only KSP arrays.' +
                    f' Pasted {type(arr)}')
            self.__func = self.__foreach_handler
            self.__seq = arr
            return True
        return False

    def __check_duck_arg(self, arg, arg_name: str,
                         requirement: int):
        if arg:
            if not requirement:
                raise KspCondError(for_wrong_arg_msg)
            if not isinstance(arg, (int, kInt, AstGetItem)):
                raise KspCondError(for_type_err_msg.format(
                    name=arg_name,
                    arg_typ=type(arg),
                    classes=(int, 'KSP int variable(%s)' % kInt)))

    def __duck_typing(self, start, stop, step):
        '''Checks types or range arguments.
        Raises exception on non-int args'''
        if not start:
            raise KspCondError(
                f'''has to be at least one arg:
                start: [{int}, {kInt}] or arr: [{KspNativeArray}]''')
        self.__check_duck_arg(start, 'start', start)
        self.__check_duck_arg(stop, 'stop', start)
        self.__check_duck_arg(step, 'step', stop)

    def __enter__(self):
        '''Returns generator, depends on loop-type'''
        return self.__func()

    def __exit__(self, exc, value, trace):
        '''Supresses Brake exceptions and generates
        postfix (end) code'''
        if exc is not None and exc is not KspCondBrake:
            return
        if isinstance(value, KspCondBrake):
            IOutput.put(f'{self.__idx} := {len(self.__seq)}')
            IOutput.put(value)
        self.__generate_exit_code()
        return True

    def __generate_exit_code(self):
        '''inc(self.__idx) if for, step line if range'''
        if not KSP.is_under_test():
            if self.__func == self.__foreach_handler:
                IOutput.put(f'inc({self.__idx})')
            if self.__func == self.__range_handler:
                IOutput.put(
                    f'{self.__idx} := {self.__idx} + {self.__step}')
            IOutput.put('end while')
            self.__master.end()

    def __foreach_handler(self):
        '''Uder tests returns iterator over self.__seq,
        under compilation idx assignement and while cond lines'''
        if KSP.is_under_test():
            if self.enumerate:
                seq = enumerate(self.__seq)
            else:
                seq = self.__seq
            for item in seq:
                yield item
            return

        IOutput.put(f'{self.__idx} := 0')
        IOutput.put(f'while({self.__idx} < {len(self.__seq)})')

        if self.enumerate:
            out = self.__idx, AstGetItem(self.__seq, self.__idx)
        else:
            out = AstGetItem(self.__seq, self.__idx)
        yield out

        return True

    # def enumerate(self):
    #     if KSP.is_under_test():
    #         return [(idx, val) for idx, val in enumerate(self.__seq)]

    def __parse_args(self):
        '''Prepares arguments rof range() function'''
        if len(self.__args) == 1:
            return (0, expand_if_callable(self.__args[0]), 1)
        if len(self.__args) == 2:
            self.__args[0], self.__args[1] =\
                expand_if_callable(self.__args[0], self.__args[1])
            return (self.__args[0], self.__args[1], 1)
        return expand_if_callable(self.__args)

    def __range_handler(self):
        '''Under tests returns generator over range(args) function
        Under compilation idx assignement and while cond lines'''
        if KSP.is_under_test():
            for i in range(*self.__args):
                yield i
            return
        IOutput.put(f'{self.__idx} := {self.__start}')
        IOutput.put(f'while({self.__idx} < {self.__stop})')
        yield self.__idx
        return True


class While(KSP):
    """While loop can be translated to KSP.
    Instead of For() can not handle Break() function yet.

    As For(), If(), Else(), Select() and Case() is context
    manager.

    Returns
    -------
    self

    Raises
    ------
    KspCondError

    Example
    -------
    with While() as w:
    ....while w(lambda x=x, y=y: x != y):
    ........with If(y != 10):
    ............check()
    ............y(10)
    ........x += 1
    """

    def __init__(self):
        self.__count = 0

    def __call__(self, condition: bool):
        self.__condition = expand_if_callable(condition)
        if KSP.is_under_test():
            if self.__condition:
                return True
            raise KspCondBrake()
        if self.__count == 0:
            IOutput.put(f'while({AstBool()(self.__condition)})')
            self.__count += 1
            return True
        raise KspCondBrake()

    def __enter__(self):
        return self

    def __exit__(self, exc, value, trace):
        if exc is not None:
            if exc is not KspCondBrake:
                return
        if not KSP.is_under_test():
            if isinstance(value, KspCondBrake):
                if str(value) != '':
                    raise KspCondError(
                        'While loop can not be breaked')
            IOutput.put('end while')
        return True
