class KspCondError(Exception):
    """Exception tells user he's doing wrong"""
    pass


class KspCondBrake(Exception):
    """Eceptions breaks for loops"""
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
