"""Context managers to be used as KSP conditions.

logical expressions as arguments of managers can be as complex
as You wish. But every comparison expression between logical
operators '& |' has to be inside round brackets.
'&' and '|' operators on KSP objects outside conditions works
as bitwise and and or.

Inside the every block of current managers has to be placed
check() function for proper working of condition under tests.

Under tests everything evaluates as normal python code.

If(), Else()
------------
with If((x == y) & (x != 2)):
    check()
    x += 1
with If(y == 1):
    check()
    x += 1
    # nested if
    with If(y != 2):
        check()
        x += 1
# elif
with Else((x != y) & (x == 1)):
    check()
    x += 1
# normal else
with Else():
    check()
    y += 1

translates to
-------------
if($x = $y and $x # 2)
    $x := $x + 1
end if
if($y = 1)
$x := $x + 1
    if($y # 2)
        $x := $x + 1
    end if
else
    if($x # $y and $x = 1)
        $x := $x + 1
    else
        $y := $y + 1
    end if
end if

Select() and Case() conditions
------------------------------
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

translates to
-------------
select($x)
    case(1)
        $y := $y + 1
    case(2)
        $y := $y + 2
    select($y)
        case(2)
            $y := $y + 1
        case(3)
    end select
end select
"""


from interfaces import IOutput
from pyksp_ast import AstBool
from pyksp_ast import AstOperator
from abstract import KSP
from native_types import kInt
from context_tools import check
# from context_tools import Break
from context_tools import KspCondFalse
from context_tools import KspCondBrake
from context_tools import KspCondError


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

    def __init__(self, condition):
        if IOutput.get_callable_on_put():
            IOutput.get_callable_on_put()()
            IOutput.callable_on_put(None)
        if KSP.is_under_test():
            if callable(condition):
                condition = condition()
        self.__condition = condition

    def __enter__(self):
        """Checks if condition is True, appends it to new item of
        can_be_else and build if(condition) line"""
        can_be_else.append([self.__condition])
        if KSP.is_under_test():
            if not self.__condition:
                check(False)
            return
        IOutput.put(f'if({AstBool()(self.__condition)})')
        return

    def __exit__(self, exc_type, value, traceback):
        """Suppresses KspCondFalse and builds 'end if' lines
        on KspCondBrake exceptions."""
        if exc_type is not None:
            if not isinstance(value, (KspCondFalse, KspCondBrake)):
                return
        if not KSP.is_under_test():
            if exc_type is KspCondBrake:
                raise KspCondBrake('end if')
            IOutput.put('end if')
        IOutput.callable_on_put(If.refresh)
        if exc_type is KspCondBrake:
            return
        return True

    @staticmethod
    def refresh():
        """static method to get the las If stack from can_be_else"""
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

        IOutput.callable_on_put(None)
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
            if not KSP.is_under_test():
                if IOutput.pop() != 'end if':
                    raise\
                        KspCondError(
                            'something is wrong here. Library bug.')
            last_result = item
        return last_result

    def __is_else(self):
        """Checks the condition and puts 'else' to IOutput"""
        if KSP.is_under_test():
            if self.__if_result:
                check(False)
                return
            return True
        IOutput.put('else')

    def __is_elif(self):
        """Restoring if order inside can_be_else,
        puts to IOutput else and if(condition) lines"""
        cond = self.__condition
        if KSP.is_under_test() and not cond:
            If._condition(False)
            return
        result = list()
        for idx in range(self.__if_count):
            result.append(False)
        result.append(cond)
        self.__if_count += 1
        can_be_else.append(result)
        if not KSP.is_under_test():
            IOutput.put('else')
            IOutput.put(f'if({AstBool()(cond)})')

    def __exit__(self, exc_type, value, trace):
        """Suppresses KspCondFalse and builds 'end if' lines
        on KspCondBrake exceptions. Puts to IOutput If.refresh to
        zero can_be_else list on KSP code input"""
        if exc_type is not None:
            if not isinstance(value, (KspCondFalse, KspCondBrake)):
                return
        self.__build_end_code(value)
        if self.__func is self.__is_elif:
            IOutput.callable_on_put(If.refresh)
        if isinstance(value, KspCondBrake):
            return
        return True

    def __build_end_code(self, value):
        """Puts to IOutput proper amount of 'end if' lines."""
        if not KSP.is_under_test():
            postfix = ''
            for idx in range(self.__if_count):
                postfix += 'end if'
                if idx != self.__if_count - 1:
                    postfix += '\n'
            if isinstance(value, KspCondBrake):
                raise KspCondBrake(postfix)
            for line in postfix.split('\n'):
                IOutput.put(line)


class Select:
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
        if not KSP.is_under_test():
            if not isinstance(expression, (kInt, AstOperator)):
                raise KspCondError('''
                    can select only KSP variables or expressions
                    with them''')
        self.__var = expression

    def __enter__(self):
        Select._vars.append(self.__var)
        if not KSP.is_under_test():
            IOutput.put(f'select({self.__var()})')
        IOutput.exception_on_put(KspCondError(
            '''Wrong syntax. all code has to be in Case context'''))

    def __exit__(self, exc_type, value, trace):
        Select._vars.pop()
        IOutput.exception_on_put(None)
        if not KSP.is_under_test():
            IOutput.put('end select')


class Case:
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
        IOutput.exception_on_put(None)

    def __enter__(self):
        """Retrieves selected var and building case(state) line"""
        try:
            var = Select._vars[-1]
        except IndexError:
            raise KspCondError(
                '''Case has to be inside Select() context''')
        if not KSP.is_under_test():
            IOutput.put(f'case({self.__state})')
            return
        if callable(var):
            var = var()
        if var != self.__state:
            check(False)

    def __exit__(self, exc_type, value, trace):
        """Supresses KspCondFalse and add KspCondError to IOutput
        for preventing KSP code before end select or new Case"""
        if exc_type is not None:
            if not isinstance(value, KspCondFalse):
                return
        IOutput.exception_on_put(KspCondError(
            '''Wrong syntax. all code hase to be in Case block'''))
        return True
