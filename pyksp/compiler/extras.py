from abstract import Output
from abstract import KSP

from typing import Union
from typing import List

from functools import wraps
from inspect import cleandoc


def docstring(f):
    """Decorator for placing docastrings as comments to code
    docstring will be placed at the function invocation place
    if script docs attribute is set to True"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if KSP.docs:
            Output().put('{%s}' % f.__doc__)
        return f(*args, **kwargs)

    return wrapper


def comment(comment: str):
    """Place comment to the result code
    comment will be placed if script docs attribute is set to True"""
    if not KSP.docs:
        return
    comm: Union[str, List[str]]
    if not KSP.indents:
        Output().put('{%s}' % comment)
        return
    # Output().put('{%s}' % cleandoc(comment))
    comm = cleandoc(comment).split('\n')
    new = comm[0]
    if len(comm) > 1:
        for line in comm[1:]:
            new += f'\n{" " * KSP.indents}{line}'
    Output().put('{%s}' % new)
