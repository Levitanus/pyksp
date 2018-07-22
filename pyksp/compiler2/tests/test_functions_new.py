import os
import sys
import unittest as t
import re

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from abstract import KSP

from interfaces import IOutput
# from interfaces import IName
from dev_tools import DevTest
from dev_tools import print_lines
# from dev_tools import expand_if_callable
from stack import kLocal

from native_types import kStr

from functions_new import *


@t.skip
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
        obj, return_full = FuncArgs(Foo).return_full(*args, **kwargs)
        self.assertEqual(desired_dict, return_full)

        def foo(x=kLocal(int)):
            pass
        FuncArgs(foo)
        with self.assertRaises(AttributeError):
            FuncArgs(foo).return_full(1)


@t.skip
class TestOut(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_anno(self):
        out = kInt('out')

        def foo(self, arg: int, arg2: kOut(int)):
            arg2(arg)

        obj, return_full = FuncArgs(foo).return_full(self, 1, out)
        self.assertEqual(
            return_full,
            {'arg': 1, 'arg2': out})
        self.assertEqual(obj, self)


@t.skip
class TestFuncStack(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        # self.args = FuncArgs()

    def tearDown(self):
        super().tearDown()

    def test_it_code(self):
        KSP.toggle_test_state(False)
        self.it()

    def test_it_return(self):
        KSP.toggle_test_state(True)
        self.it()

    def it(self):
        stack = FuncStack('func', 1000, 100)
        self.assertTrue(stack.IsEmpty())

        x = kInt('x', 1)
        y = kStr('y', '1')
        z = kReal('z', 1.0)
        arr = kArrInt('arr', [1, 2, 3, 5], length=4)
        loc_int = kLocal(int)
        loc_str = kLocal(str)
        loc_arrReal = kLocal(float, 10)

        n_x, n_y, n_z, n_arr, \
            n_loc_int, n_loc_str, \
            n_loc_arrReal = \
            stack.push(x=x,
                       y=y,
                       z=z,
                       arr=arr,
                       loc_int=loc_int,
                       loc_str=loc_str,
                       loc_arrReal=loc_arrReal)
        self.assertFalse(stack.IsEmpty())
        if KSP.is_under_test():
            self.assertEqual(n_x(), 1)
            self.assertEqual(n_y(), '1')
            self.assertEqual(n_z(), 1.0)
            self.assertEqual(n_arr(), [1, 2, 3, 5])
        n_loc_arrReal[3] = 15.0
        if KSP.is_under_test():
            self.assertEqual(n_loc_arrReal[3], 15.0)
        else:
            self.assertEqual(
                IOutput.get()[-1],
                '?stack_func_real_arr[%stack_func_real_idx' +
                '[$stack_func_real_curr] + 1 + 3] := 15.0')
        n_loc_str('my_string')
        if KSP.is_under_test():
            self.assertEqual(n_loc_str(), 'my_string')
        else:
            self.assertEqual(
                IOutput.get()[-1],
                '!stack_func_str_arr[%stack_func_str_idx' +
                '[$stack_func_str_curr] + 1] := "my_string"')

        x = kLocal(int)
        x = stack.push(x=x)[0]
        x += 1
        if not KSP.is_under_test():
            self.assertEqual(
                IOutput.get()[-1],
                '%stack_func_int_arr[%stack_func_int_idx[' +
                '$stack_func_int_curr] + 0] := %stack_func_int_arr' +
                '[%stack_func_int_idx[$stack_func_int_curr]' +
                ' + 0] + 1')
        stack.pop()
        stack.pop()
        self.assertTrue(stack.IsEmpty())


# @t.skip
class TestFunc(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.str = 'self string'
        self.ret = kStr('ret')

    def tearDown(self):
        super().tearDown()

    def test_name(self):
        @Func
        def myfunc():
            pass
        name = myfunc.name
        module = re.sub(r'\.', '__', __name__)
        self.assertEqual(name(),
                         module + 'TestFunc__test_name__myfunc')

    @Func
    def myfunc(self, arg: int, int_arg: int, arg2: str='string',
               ret: kOut(str)=None):
        arg += 1
        ret(int_arg)
        ret += arg
        ret += arg2
        ret(self.str)
        return self.str

    @t.skip
    def test_call(self):
        x = kStr('x')
        y = kInt('y')

        self.myfunc(y, 1, ret=x)
        # print_lines(IOutput.get())
        expected_output = [
            '%stack_func_int_arr[%stack_func_int_idx[' +
            '$stack_func_int_curr] + 0] := $y',
            '%stack_func_int_arr[%stack_func_int_idx' +
            '[$stack_func_int_curr] + 1] := 1',
            '!stack_func_str_arr[%stack_func_str_idx' +
            '[$stack_func_str_curr] + 0] := "string"',
            '!stack_func_str_arr[%stack_func_str_idx' +
            '[$stack_func_str_curr] + 1] := @x',
            f'call {TestFunc.myfunc.name()}',
            '@x := !stack_func_str_arr[%stack_func_str_idx' +
            '[$stack_func_str_curr] + 1]',
            '$stack_func_int_curr := $stack_func_int_curr - 1',
            '$stack_func_str_curr := $stack_func_str_curr - 1'
        ]
        self.assertEqual(IOutput.get(), expected_output)

        KSP.toggle_test_state(True)
        string = self.myfunc(y, 1, ret=x)
        self.assertEqual(x, '11string')
        self.assertEqual(x(), '11string')
        self.assertEqual(string, self.str)

    def test_simple(self):
        KSP.toggle_test_state(False)
        y = kInt('y')
        self.myfunc(2, y, ret=self.ret, inline=True)
        print_lines(IOutput.get())


if __name__ == '__main__':
    t.main()
