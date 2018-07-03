import os
import sys
import unittest as t
# import re

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from interfaces import IOutput
from dev_tools import DevTest

from native_types import kStr

from functions_new import *


class TestFuncArgs(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        # self.args = FuncArgs()

    def tearDown(self):
        super().tearDown()

    def test_new_arg(self):

        def Foo(arg):
            pass

        with self.assertRaises(AttributeError):
            FuncArgs(Foo)

        def Foo(arg: dict):
            pass
        with self.assertWarns(FuncArg.warn):
            FuncArgs(Foo)

        def Foo(arg: int, arg2: str,
                vararg: int=1, kwarg: kStr='str'):
            pass

        str_arg = kStr('str')

        args, kwargs = (1, '2', '1'), {'kwarg': str_arg}
        with self.assertRaises(TypeError) as e:
            FuncArgs(Foo).check_args(*args, **kwargs)
            self.assertEqual(
                e.msg,
                "arg vararg is <class 'str'> has to be " +
                "(<class 'int'>, <class 'native_types.kInt'>)")

        args, kwargs = (1, '2'), {'kwarg': str_arg}
        desired_dict = {
            'arg': 1, 'arg2': '2', 'vararg': 1,
            'kwarg': str_arg
        }
        return_full = FuncArgs(Foo).return_full(*args, **kwargs)
        self.assertEqual(desired_dict, return_full)


class TestFuncStack(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        # self.args = FuncArgs()

    def tearDown(self):
        super().tearDown()

    def test_it(self):
        stack = FuncStack('func', 1000, 100)
        x = kInt('x', 1)
        y = kStr('y', '1')
        z = kReal('z', 1.0)
        arr = kArrInt('arr', [1, 2, 3, 5], length=4)

        n_x, n_y, n_z, n_arr = stack.push(x=x, y=y, z=z, arr=arr)
        print(n_x, n_y, n_z, n_arr)
        print(n_x.val(), n_y, n_z, n_arr)


if __name__ == '__main__':
    t.main()
