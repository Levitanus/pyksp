from typing import Callable
import unittest as t

from interfaces import IOutput
from interfaces import IName
from abstract import KSP
from abstract import KspObject

from native_types import KspNative
from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal


def print_lines(lines):
    print('---------LINES----------')
    for line in lines:
        print(line)
    print('------------------------')


def unpack_lines(lines):
    out = ''
    for line in lines:
        out += '%s\n' % line
    return out


def expand_if_callable(*args):
    """Call and return passed args.

    Returns
    -------
    If passed more than 1 objects returnes tuple
    otherwise, returns obj
    """
    out = list()
    for obj in args:
        if callable(obj):
            obj = obj()
        out.append(obj)
    if len(out) == 1:
        out = out[0]
    return out


class DevTest(t.TestCase):

    def setUp(self):
        IOutput.release()
        IOutput.refresh()
        IName.refresh()
        KspObject.refresh()
        KSP.toggle_test_state(False)

    def tearDown(self):
        self.setUp()


class Infix:
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return Infix(
            lambda x, self=self, other=other:
            self.function(other, x))

    def __or__(self, other):
        return self.function(other)

    def __call__(self, value1, value2):
        return self.function(value1, value2)


def toggle_bool(class_):
    KSP.toggle_bool(True)

    def wrapper(*args, **kwargs):
        return class_(*args, **kwargs)
    KSP.toggle_bool(False)
    return wrapper


def native_from_input(class_) -> KspNative:
    if not isinstance(class_, type):
        raise TypeError('has to be class')
    if class_ in (int, kInt):
        return kInt
    if class_ in (str, kStr):
        return kStr
    if class_ in (float, kReal):
        return kReal
    if class_ in (kArrInt, kArrReal, kArrStr):
        return class_


def native_from_input_obj(obj: object) -> KspNative:
    if isinstance(obj, (int, kInt)):
        return kInt
    if isinstance(obj, (str, kStr)):
        return kStr
    if isinstance(obj, (float, kReal)):
        return kReal
    if isinstance(obj, kArrInt):
        return kArrInt
    if isinstance(obj, kArrReal):
        return kArrReal
    if isinstance(obj, kArrStr):
        return kArrStr
    raise TypeError('has to be instance of %s' % KspNative)


class SingletonMeta(type):

    def __new__(cls, name, bases, dct):
        access = SingletonMeta.access
        dct['__new__'] = access
        dct['instance'] = None
        class_ = type.__new__(cls, name, bases, dct)
        return class_

    def access(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = cls
            return cls.__init__(cls, *args, **kwargs)
        return cls.instance.__call__(cls, *args, **kwargs)
