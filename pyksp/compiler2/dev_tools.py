from typing import Any
from typing import Callable


class WrapProp:
    '''wraps class descriptor
    – if wrap_type is WrapProp.before fget/fset will be executed, than
    property get/set will be returned
    – if wrap_type is WrapProp.after property get/set will be executed,
    than fget/fset will be returned
    – if wrap_type is WrapProp.arg property get/set will be passed as
    additional arg to the fget/fset
    '''

    before = object()
    after = object()
    arg = object()
    instead = object()

    def __init__(self, prop: Any, fget: Callable, fset: Callable,
                 wrap_type: int):
        self.prop = prop
        self.fget = fget
        self.fset = fset
        self.wrap_type = wrap_type

    def __get__(self, obj, cls):
        if obj is None:
            return self.prop.__get__(None, cls)
        if self.wrap_type is self.instead:
            return self.fget(obj)
        if self.wrap_type is self.before:
            self.fget(obj)
            return self.prop.__get__(obj, cls)
        if self.wrap_type is self.after:
            self.prop.__get__(obj, cls)
            return self.fget(obj)
        if self.wrap_type is self.arg:
            return self.fget(obj, self.prop.__get__(obj, cls))

    def __set__(self, obj, val):
        if self.wrap_type is self.instead:
            return self.fset(obj, val)
        if self.wrap_type is self.before:
            self.fset(obj, val)
            return self.prop.__set__(obj, val)
        if self.wrap_type is self.after:
            self.prop.__get__(obj, val)
            return self.fset(obj, val)
        if self.wrap_type is self.arg:
            return self.fset(obj, val, self.prop.__get__(obj, val))


def print_lines(arg):
    if isinstance(arg, str):
        print('---print_one_line---')
        print(arg)
        return
    print('---print-lines---')
    for line in arg:
        print(line)
    print('---END---')
    return


def unpack_lines(arg):
    if isinstance(arg, str):
        return arg
    out = ''
    for line in arg:
        out += line + '\n'
    return out[:-1]
