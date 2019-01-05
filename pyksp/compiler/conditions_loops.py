# from .base_types import KspVar
from .base_types import AstOperator
from .base_types import KspIntVar
from .base_types import KspArray
from .base_types import get_runtime, get_string_repr

from .abstract import Output
from .abstract import KSP
# from .abstract import SingletonMeta

from .native_types import kInt
from .native_types import kArrInt

from typing import List

# from .dev_tools import unpack_lines


class KspCondError(Exception):
    """Exception tells user he's doing wrong"""
    pass


class KspCondBrake(Exception):
    """Exception break for loops"""
    pass


class KspCondFalse(Exception):
    """exception works kike continue within If() and Select"""
    pass


__condition = True


def Break():
    """Function to break For() loop.
    Equal to val = len(seq)"""
    raise KspCondBrake('statement breaked')


def CondFalse():
    """Function works as operator continue in python.
    For testing purpose, does not translates to KSP.
    """
    raise KspCondFalse()


def check(condition=None):
    """Function for proper work of conditions under tests.
    Has to be on the first line of every context block.
    """
    global __condition

    if condition is None:
        if __condition is False:
            __condition = True
            CondFalse()

        return True
    __condition = condition


can_be_else = list()


class If(KSP):
    """
    If condition can be translated to KSP.
    As For(), While(), Else(), Select and Case() is context manager.
    The first line inside the context block has to contain check()
    function for proper execution under tests.

    Under tests works as normal if-else(elif) condition.
    if Else has bool argument it evaluates as elif.

    Example
    -------
    with If((x == y) & (x != 2)):
        check()
        x += 1
    with If(y == 1):
        check()
        x += 1
        with If(y != 2):
            check()
            x += 1
    with Else((x != y) & (x == 1)):
        check()
        x += 1
    with Else():
        check()
        y += 1
    """

    __condition = True

    @property
    def _condition(self):
        return If.__condition

    @_condition.setter
    def _condition(self, val):
        If.__condition = val

    def __init__(self, condition):
        call = Output().callable_on_put
        if call:
            call()
            Output().callable_on_put = None
        # if not self.is_compiled():
        #     if callable(condition):
        #         condition = condition()
        self.__condition = condition

    def __enter__(self):
        """Checks if condition is True, appends it to new item of
        can_be_else and build if(condition) line"""
        can_be_else.append([self.__condition])
        if not self.is_compiled():
            if not self.__condition:
                check(False)
            return
        self.set_bool(True)
        Output().put(f'if({get_string_repr(self.__condition)})')
        Output().indent()
        self.set_bool(False)
        return

    def __exit__(self, exc_type, value, traceback):
        """Suppresses KspCondFalse and builds 'end if' lines
        on KspCondBrake exceptions."""
        if exc_type is not None:
            if not isinstance(value, (KspCondFalse, KspCondBrake)):
                return
        if self.is_compiled():
            if exc_type is KspCondBrake:
                Output().unindent()
                raise KspCondBrake('end if')
            Output().unindent()
            Output().put('end if')
        Output().callable_on_put = If.refresh
        if exc_type is KspCondBrake:
            return
        return True

    @staticmethod
    def refresh():
        """static method to get the last If stack from can_be_else"""
        global can_be_else
        can_be_else.pop()


class Else(KSP):
    """Else end elif statement of KSP.
    Under tests executed if previous If() was False and/or if
    elif condition is True

    if pass bool expression as argument to Else() it works
    like elif:

    with Else():
        # normal else
    with Else(x==y):
        # elif

    See Also
    --------
    If()
    """

    def __init__(self, condition=None):

        Output().callable_on_put = None
        # Output().put('Else Init')
        self.__if_count = 0
        self.__condition = condition
        self.__if_result = self.is_after_if()
        if condition is None:
            self.__func = self.__is_else
            return
        self.__func = self.__is_elif
        return

    def __enter__(self):
        # Output().put('else enter')
        return self.__func()

    def is_after_if(self):
        """Checks amount of statements and raises exception if
        can_be_else is empty (pure KSP code before Else())"""
        try:
            if_result = can_be_else.pop()
        except IndexError:
            raise KspCondError('has to be right after If()')
        for item in if_result:
            self.__if_count += 1
            if self.is_compiled() and Output().blocked is not True:
                if Output().pop().strip() != 'end if':
                    raise\
                        KspCondError(
                            'something is wrong here. Library bug.')
                # Output().indent()
            last_result = item
        return last_result

    def __is_else(self):
        """Checks the condition and puts 'else' to Output()"""
        # self.__if_result = self.is_after_if()
        if not self.is_compiled():
            if self.__if_result:
                # If.__condition = False
                check(False)
                return
            return True
        Output().put('else')
        Output().indent()

    def __is_elif(self):
        """Restoring if order inside can_be_else,
        puts to Output() else and if(condition) lines"""
        cond = self.__condition
        if not self.is_compiled() and not cond:
            # If.__condition = False
            check(False)
            return
        result = list()
        for idx in range(self.__if_count):
            result.append(False)
        result.append(cond)
        self.__if_count += 1
        can_be_else.append(result)
        if self.is_compiled():
            Output().indent()
            Output().put('else')
            Output().indent()
            self.set_bool(True)
            Output().put(f'if({cond.expand()})')
            Output().indent()
            self.set_bool(False)

    def __exit__(self, exc_type, value, trace):
        """Suppresses KspCondFalse and builds 'end if' lines
        on KspCondBrake exceptions. Puts to Output() If.refresh to
        zero can_be_else list on KSP code input"""
        if exc_type is not None:
            if not isinstance(value, (KspCondFalse, KspCondBrake)):
                return
        self.__build_end_code(value)
        if self.__func is self.__is_elif:
            # Output().unindent()
            Output().callable_on_put = If.refresh
        if isinstance(value, KspCondBrake):
            return
        # Output().unindent()
        return True

    def __build_end_code(self, value):
        """Puts to Output() proper amount of 'end if' lines."""
        if self.is_compiled():
            postfix = ''
            for idx in range(self.__if_count):
                # Output().unindent()
                postfix += 'end if'
                if idx != self.__if_count - 1:
                    postfix += '\n'
            if isinstance(value, KspCondBrake):
                # Output().unindent()
                raise KspCondBrake(postfix)
            for line in postfix.split('\n'):
                Output().unindent()
                Output().put(line)


class Select(KSP):
    """Select (also known as switch) statement of KSP.
    Under tests keeps the expression inside, and if any of
    included Case() statements equals the expression, it will
    be executed.

    Within compilation resolves to
    select(expression)
        case(state)
            # code
        case(state)
            # code
    end select

    Raises
    ------
    KspCondError

    Example
    -------
    with Select(x):
        with Case(1):
            check()
            y += 1
        with Case(2):
            check()
            y += 2
            with Select(y):
                with Case(2):
                    check()
                    y += 1
                with Case(3):
                    check()
                    CondFalse()

    See Also
    --------
    Break()
    CondFalse()
    If()
    """

    _vars = list()

    def __init__(self, expression: int):
        if self.is_compiled():
            if not isinstance(expression, (KspIntVar, AstOperator)):
                raise KspCondError('''
                    can select only KSP variables or expressions
                    with them''')
        self.__var = expression

    def __enter__(self):
        Select._vars.append(self.__var)
        if self.is_compiled():
            Output().put(f'select({self.__var.val})')
            Output().indent()
        Output().exception_on_put = KspCondError(
            '''Wrong syntax. all code has to be in Case context''')

    def __exit__(self, exc_type, value, trace):
        Select._vars.pop()
        Output().exception_on_put = None
        if self.is_compiled():
            Output().unindent()
            Output().put('end select')


class Case(KSP):
    """Case statement of KSP.
    Under tests executed if expression insinde the Select()
    condition equals expression inside current Case() statement.

    Within compilation resolves to case(state) line

    See Also
    --------
    Select()
    """

    def __init__(self, state: int):
        if callable(state):
            state = state()
        self.__state = state
        Output().exception_on_put = None

    def __enter__(self):
        """Retrieves selected var and building case(state) line"""
        try:
            var = Select._vars[-1]
        except IndexError:
            raise KspCondError(
                '''Case has to be inside Select() context''')
        if self.is_compiled():
            Output().put(f'case({self.__state})')
            Output().indent()
            return
        if callable(var):
            var = var()
        if var != self.__state:
            check(False)

    def __exit__(self, exc_type, value, trace):
        """Supresses KspCondFalse and add KspCondError to Output()
        for preventing KSP code before end select or new Case"""
        if exc_type is not None:
            if not isinstance(value, KspCondFalse):
                return
        Output().exception_on_put = KspCondError(
            '''Wrong syntax. all code hase to be in Case block''')
        Output().unindent()
        return True


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

    __maxlen = 20
    idx = None
    arr = None

    running_instances: List['For'] = list()

    def maxlen(self, val):
        For.__maxlen = val

    @classmethod
    def init_arrays(cls):
        out = list()
        if cls.arr is not None:
            return out
        cls.idx = kInt(-1, '_for_loop_curr_idx')
        cls.arr = kArrInt(name='_for_loop_idx', size=cls.__maxlen)
        out.extend(cls.idx._generate_init())
        out.extend(cls.arr._generate_init())
        return out

    def __init__(self, start: int=None, stop: int=None,
                 step: int=None, arr: KspArray=None):
        self.init_arrays()
        self.running_instances.append(self)
        self._out_touched = False
        For.idx.inc()
        self._idx = For.arr[For.idx]
        for idx, inst in enumerate(reversed(self.running_instances)):
            if idx == 0:
                formule = For.idx
            else:
                formule = For.idx - idx
            inst._idx = For.arr[formule]
        if self.__is_foreach(arr, start, stop, step):
            # self.enumerate = enumerate
            return
        # if enumerate:
        #     raise AttributeError(
        #         'enumerate par accesible only in for_each loop')
        self.__duck_typing(start, stop, step)
        self.__func = self.__range_handler
        args = list()
        args.append(start)
        if stop:
            args.append(stop)
        if step:
            args.append(step)
        self.__args = self.__parse_args(*args)
        self.__start, self.__stop, self.__step = self.__args

    def __is_foreach(self, arr, start, stop, step):
        '''Returns True if arr is only argument'''
        if not arr:
            return False
        if start or stop or step:
            raise KspCondError(for_wrong_syntax_msg)
        if not isinstance(arr, KspArray):
            raise KspCondError(
                'For loop accepts only KSP arrays.' +
                f' Pasted {type(arr)}')
        self.__func = self.__foreach_handler
        self.__seq = arr
        return True

    def __check_duck_arg(self, arg, arg_name: str,
                         requirement: int):
        if not arg:
            return
        if not requirement:
            raise KspCondError(for_wrong_arg_msg)
        if not isinstance(arg, (int, KspIntVar, AstOperator)):
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
                start: [{int}, {kInt}] or arr: [{KspArray}]''')
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
            if self._out_touched:
                Output().blocked = False
                self._out_touched = False
            return
        if isinstance(value, KspCondBrake):
            if self.__func is self.__foreach_handler:
                self._idx <<= len(self.__seq)
            else:
                self._idx <<= self.__stop
            Output().put(f'{value}')
        self.__generate_exit_code()
        if self._out_touched:
            Output().blocked = False
            self._out_touched = False
        return True

    def __generate_exit_code(self):
        '''inc(self._idx) if for, step line if range'''
        if self.is_compiled():
            if self.__func == self.__foreach_handler:
                self._idx.inc()
            if self.__func == self.__range_handler:
                self._idx += self.__step
            Output().unindent()
            Output().put('end while')
        For.idx.dec()
        self.running_instances.pop()
        for idx, inst in enumerate(reversed(self.running_instances)):
            if idx == 0:
                formule = For.idx
            else:
                formule = For.idx - idx
            inst._idx = For.arr[formule]

    def __foreach_handler(self):
        '''Uder tests returns iterator over self.__seq,
        under compilation idx assignement and while cond lines'''
        self._idx <<= 0
        if self.is_compiled():
            Output().put(f'while({self._idx.val} < {len(self.__seq)})')
            Output().indent()
        for idx in range(len(self.__seq)):
            if idx > 0 and self.is_compiled() and not Output().blocked:
                self._out_touched = True
                Output().blocked = True
            self._idx._set_runtime(idx)
            item = self.__seq[self._idx]
            yield item
        if self._out_touched:
            Output().blocked = False
            self._out_touched = False
        return
        # yield out

        return True

    def __parse_args(self, *args):
        '''Prepares arguments for range() function'''
        if len(args) == 1:
            return (0, args[0], 1)
        if len(args) == 2:
            return (args[0], args[1], 1)
        return args

    def __range_handler(self):
        '''Under tests returns generator over range(args) function
        Under compilation idx assignement and while cond lines'''
        self._idx <<= self.__start
        if self.is_compiled():
            Output().put(
                f'while({self._idx.val} < {get_string_repr(self.__stop)})')
            Output().indent()
        for i in range(*get_runtime(*self.__args)):
            self._idx._set_runtime(i)
            if i > get_runtime(self.__start) and \
                    self.is_compiled()and not Output().blocked:
                self._out_touched = True
                Output().blocked = True
            yield self._idx
        if self._out_touched:
            self._out_touched = False
            Output().blocked = False
        return

    @staticmethod
    def refresh():
        For.arr = None
        For.idx = None


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
    ............y += 1
    ........x += 1
    """

    def __init__(self):
        self.__count = 0
        self._blocked = False

    def __call__(self, condition: bool):
        if self.__count and not Output().blocked:
            self._blocked = True
            Output().blocked = True
        if callable(condition):
            condition = condition()
        self.__condition = condition
        if not self.is_compiled():
            if self.__condition:
                return True
            raise KspCondBrake()
        if self.__condition.get_value():
            self.set_bool(True)
            Output().put(f'while({self.__condition.expand()})')
            Output().indent()
            self.set_bool(False)
            self.__count += 1
            return True
        if self._blocked:
            self._blocked = False
            Output().blocked = False
        raise KspCondBrake()

    def __enter__(self):
        return self

    def __exit__(self, exc, value, trace):
        if self._blocked:
            self._blocked = False
            Output().blocked = False
        if exc is not None:
            if exc is not KspCondBrake:
                return
        if self.is_compiled():
            # if isinstance(value, KspCondBrake):
            #     if str(value) != '':
            #         raise KspCondError(
            #             'While loop can not be breaked')
            Output().unindent()
            Output().put('end while')
        return True
