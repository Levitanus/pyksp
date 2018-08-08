# from base_types import KspVar
from base_types import AstOperator
from base_types import KspIntVar
from abstract import Output
from abstract import KSP
from abstract import SingletonMeta
from native_types import kInt
from native_types import kArrInt


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
        Output().put(f'if({self.__condition.expand()})')
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
                raise KspCondBrake('end if')
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
        self.__if_count = 0
        self.__condition = condition
        self.__if_result = self.is_after_if()
        if condition is None:
            self.__func = self.__is_else
            return
        self.__func = self.__is_elif
        return

    def __enter__(self):
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
            if self.is_compiled():
                if Output().pop() != 'end if':
                    raise\
                        KspCondError(
                            'something is wrong here. Library bug.')
            last_result = item
        return last_result

    def __is_else(self):
        """Checks the condition and puts 'else' to Output()"""
        if not self.is_compiled():
            if self.__if_result:
                check(False)
                return
            return True
        Output().put('else')

    def __is_elif(self):
        """Restoring if order inside can_be_else,
        puts to Output() else and if(condition) lines"""
        cond = self.__condition
        if not self.is_compiled() and not cond:
            # If._condition = False
            check(False)
            return
        result = list()
        for idx in range(self.__if_count):
            result.append(False)
        result.append(cond)
        self.__if_count += 1
        can_be_else.append(result)
        if self.is_compiled():
            Output().put('else')
            self.set_bool(True)
            Output().put(f'if({cond.expand()})')
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
            Output().callable_on_put(If.refresh)
        if isinstance(value, KspCondBrake):
            return
        return True

    def __build_end_code(self, value):
        """Puts to Output() proper amount of 'end if' lines."""
        if self.is_compiled():
            postfix = ''
            for idx in range(self.__if_count):
                postfix += 'end if'
                if idx != self.__if_count - 1:
                    postfix += '\n'
            if isinstance(value, KspCondBrake):
                raise KspCondBrake(postfix)
            for line in postfix.split('\n'):
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
        Output().exception_on_put = KspCondError(
            '''Wrong syntax. all code has to be in Case context''')

    def __exit__(self, exc_type, value, trace):
        Select._vars.pop()
        Output().exception_on_put = None
        if self.is_compiled():
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
        return True


class ForLoops(metaclass=SingletonMeta):
    '''Handles names and indexes of ForEach and ForRange loops.
    Singleton.

    maxlen can be assigned at the initialization (max amount of
    simultaneously running for-loops. default=20)
    '''

    def __init__(self, maxlen=20):
        self.idx = kInt(-1, '_for_loop_idx_curr')
        self.arr = kArrInt(name='_for_loop_idx', size=maxlen,
                           sequence=[0] * maxlen)
        # self.maxlen = maxlen

    def get_idx(self):
        '''puts in output inc of idx-var, returns string within
        idx-array[idx-var]
        Under tests returns int index var'''
        self.idx.inc()
        return self.arr[self.idx]

    def end(self):
        '''puts in output dec(idx-var) line'''
        self.idx.dec()
