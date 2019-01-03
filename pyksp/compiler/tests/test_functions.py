import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from inspect import signature

from functions import *

from abstract import Output
from abstract import KSP
from abstract import KspObject

from base_types import KspIntVar

from native_types import kInt
from native_types import kArrInt
from native_types import kStr
from native_types import kArrStr

# from dev_tools import print_lines
from dev_tools import unpack_lines

from conditions_loops import For


class TestOut(DevTest):

    def runTest(self):
        x = kOut(int)
        self.assertTrue(x.check(kInt()))
        with self.assertRaises(TypeError):
            x.check(2)
        with self.assertRaises(TypeError):
            x.check(kArrInt())
        y = kOut(str, 2)
        self.assertTrue(y.check(kArrStr(size=2)))
        with self.assertRaises(IndexError):
            y.check(kArrStr(size=4))
        with self.assertRaises(TypeError):
            y.check(2)
        with self.assertRaises(TypeError):
            y.check(kStr())
        with self.assertRaises(IndexError):
            y.check(kArrStr(size=1))


class TestFuncArg(DevTest):

    def runTest(self):

        def foo(x: int, y: kArg(int, 3), z=kLoc(int, 2), out=kOut(int),
                bad: kOut(int)=1, bad2: int='str'):
            pass
        sig = signature(foo)

        x = FuncArg(sig.parameters['x'])
        self.assertEqual(x.ref_type, (int, KspIntVar))
        y = FuncArg(sig.parameters['y'])
        self.assertEqual(y.ref_type, (int, KspIntVar))
        self.assertEqual(y.size, 3)
        z = FuncArg(sig.parameters['z'])
        self.assertTrue(z.is_local)
        self.assertIsInstance(z.default, kLoc)
        out = FuncArg(sig.parameters['out'])
        self.assertTrue(out.is_out)
        self.assertIsInstance(out.default, kOut)

        with self.assertRaises(TypeError):
            FuncArg(sig.parameters['bad'])
        with self.assertRaises(TypeError):
            FuncArg(sig.parameters['bad2'])

        with self.assertRaises(TypeError):
            x.check('')
        self.assertEqual(x.check(3), 3)

        with self.assertRaises(TypeError):
            y.check(1)
        arr = kArrInt([1, 2])
        self.assertEqual(y.check(arr), arr)

        with self.assertRaises(TypeError):
            z.check(2)

        var = kInt(2)
        self.assertEqual(out.check(var), var)


class TestFuncArgs(DevTest):

    def runTest(self):
        str_arr = kArrStr(['one', 'two'])
        int_arr = kArrInt([1, 2, 3, 4])

        def foo(x: int, y: str, z: kArg(float),
                arr_int: kArg(int, 3), arr_str: kArg(str, 2)=str_arr,
                loc1=kLoc(float), loc2=kLoc(int, 5), out=kOut(int),
                out_str=kOut(str, 2)):
            return True
        fargs = FuncArgs(foo)

        out = kInt()
        pasted1_pos = [
            1,
            'str',
            2.1]
        pasted1_kw = {
            'arr_int': int_arr,
            # 'arr_str': kArrStr(['one', 'two'])
            'out': out
        }
        f_self, maped1, outs = fargs.map(*pasted1_pos, **pasted1_kw)
        self.assertTrue(foo(**maped1))

        self.assertEqual(maped1['x'], 1)
        self.assertEqual(maped1['y'], 'str')
        self.assertEqual(maped1['z'], 2.1)
        self.assertEqual(maped1['arr_int'], int_arr)
        self.assertEqual(maped1['arr_str'], str_arr)
        self.assertEqual(maped1['out'], out)
        self.assertIsInstance(maped1['out_str'], kLoc)

        self.assertEqual(outs['out'], out)


call_out = '''inc($_stack_functions_int_pointer)
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[$_stack_functions_\
int_pointer]] := 0
call {method}
dec($_stack_functions_int_pointer)'''

call_with_out = '''inc($_stack_functions_int_pointer)
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[$_stack_functions_\
int_pointer]] := $x
call {method}
$x := %_stack_functions_int_arr[0 + %_stack_functions_int_idx[$_stack_\
functions_int_pointer]]
dec($_stack_functions_int_pointer)'''

inlined_out = '''inc($_stack_functions_int_pointer)
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[$_stack_functions_\
int_pointer]] := $x
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[$_stack_functions_\
int_pointer]] := 3
$x := %_stack_functions_int_arr[0 + %_stack_functions_int_idx[$_stack_\
functions_int_pointer]]
dec($_stack_functions_int_pointer)'''

executables = '''function {method}
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[\
$_stack_functions_int_pointer]] := 3
end function
function {foo}
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 5)
inc($_stack_functions_int_pointer)
%_stack_functions_int_idx[$_stack_functions_int_pointer] \
:= %_stack_functions_int_idx[$_stack_functions_int_pointer - 1] + 5
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[\
$_stack_functions_int_pointer]] := %_stack_functions_int_arr\
[%_for_loop_idx[$_for_loop_curr_idx] + (0 + %_stack_functions_int_idx\
[$_stack_functions_int_pointer])]
call {method}
%_stack_functions_int_arr[%_for_loop_idx[$_for_loop_curr_idx] + (0 + \
%_stack_functions_int_idx[$_stack_functions_int_pointer])] := \
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[\
$_stack_functions_int_pointer]]
dec($_stack_functions_int_pointer)
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)
end function'''

invoked_in_init = \
    '''inc($_stack_functions_int_pointer)
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[\
$_stack_functions_int_pointer]] := 0
inc($_stack_functions_int_pointer)
%_stack_functions_int_idx[$_stack_functions_int_pointer] := \
%_stack_functions_int_idx[$_stack_functions_int_pointer - 1] + 1
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[\
$_stack_functions_int_pointer]] := %_stack_functions_int_arr[0\
 + %_stack_functions_int_idx[$_stack_functions_int_pointer]]
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[\
$_stack_functions_int_pointer]] := 3
%_stack_functions_int_arr[0 + %_stack_functions_int_idx[\
$_stack_functions_int_pointer]] := %_stack_functions_int_arr[0\
 + %_stack_functions_int_idx[$_stack_functions_int_pointer]]
dec($_stack_functions_int_pointer)
dec($_stack_functions_int_pointer)'''


class TestFunc(DevTest):

    def setUp(self):
        # super().setUp()
        self.int = 3
        self.inlined = False
        KSP.in_init(False)

    def tearDown(self):
        pass

    @func
    def method(self, arg=kOut(int)):
        self.assertEqual(
            arg.name(),
            '%_stack_functions_int_arr[0 + %_stack_functions_int_idx' +
            '[$_stack_functions_int_pointer]]')
        arg <<= self.int

    # @t.skip
    def test_calls(self):
        KSP.set_compiled(True)
        self.method()
        self.assertEqual(unpack_lines(Output().get()),
                         call_out.format(
            method=Function.get_func_name(self.method)))
        Output().refresh()

        x = kInt(name='x')
        self.method(x)
        self.assertEqual(x._get_compiled(), '$x')
        self.assertEqual(x._get_runtime(), 3)
        self.assertEqual(unpack_lines(Output().get()),
                         call_with_out.format(
            method=Function.get_func_name(self.method)))
        Output().refresh()

        self.inlined = True
        self.method(x, inline=True)
        self.assertEqual(unpack_lines(Output().get()), inlined_out)
        Output().refresh()

        arr = kArrInt([1, 2, 3, 4, 5])

        @func
        def foo(loc: kArg(int, 5)=arr):
            with For(arr=loc) as seq:
                for item in seq:
                    self.method(item)

        foo()

        # test for excluding from generation without
        # "calling" it
        @func
        def bar(var: int):
            self.method()
        bar(1, inline=True)

        generated_exec = KspObject.generate_all_executables()
        self.maxDiff = None
        self.assertEqual(
            unpack_lines(generated_exec),
            executables.format(method=Function.get_func_name(self.method),
                               foo=Function.get_func_name(foo)))

        Output().refresh()

        @func
        def foobar(arg=kLoc(int)):
            self.method(arg)
        KSP.in_init(True)
        foobar()
        KSP.in_init(False)
        self.assertEqual(unpack_lines(Output().get()), invoked_in_init)


class TestFuncRefresh(DevTest):

    @func
    def method(self):
        Output().put("I'm here")

    def runTest(self):
        self.method()
        generated = KspObject.generate_all_executables()
        self.assertEqual(generated, [])


if __name__ == '__main__':
    t.main()
