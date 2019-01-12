import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from stack import *
# from abstract import IName
from abstract import Output
from abstract import KSP
# from base_types import KspVar
from native_types import kInt
from native_types import kArrInt

# from dev_tools import print_lines
from dev_tools import unpack_lines
from conditions_loops import For


# @t.skip
class TestLocal(DevTest):

    def runTest(self):
        x = kLoc(int)
        self.assertEqual(x._size, 1)
        self.assertEqual(x.ref_type, kInt)

        y = kLoc(str, 10)
        self.assertEqual(y._size, 10)
        self.assertEqual(y.ref_type, kStr)


# @t.skip
class TestStackFrame(DevTest):

    def runTest(self):
        x = kInt(2, 'x')
        y = kLoc(int)
        z = kLoc(int, 5)
        arr = kArrInt([0] * 10, 'arr', size=10)
        with self.assertRaises(TypeError):
            StackFrame(1, 1, 1)
        with self.assertRaises(TypeError):
            StackFrame(x, (y, 1), z)

        KSP.set_compiled(True)
        frame = StackFrame(arr, (x, y), kInt(2, 'idx', is_local=True))
        x, y = frame.vars
        self.assertEqual(x._get_compiled(), '%arr[0 + $idx]')
        self.assertEqual(x._get_runtime(), 2)
        self.assertEqual(y._get_compiled(), '%arr[1 + $idx]')
        self.assertEqual(y._get_runtime(), 0)


push_output = \
    '''inc($_stack_test_pointer)
%_stack_test_arr[0 + %_stack_test_idx[$_stack_test_pointer]] := $x
%_stack_test_arr[1 + %_stack_test_idx[$_stack_test_pointer]] := $y
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 3)
%_stack_test_arr[%_for_loop_idx[$_for_loop_curr_idx] + \
(2 + %_stack_test_idx[$_stack_test_pointer])]\
 := %kArrInt0[%_for_loop_idx[$_for_loop_curr_idx]]
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 3)
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)'''
push_lvl2_output = \
    '''inc($_stack_test_pointer)
%_stack_test_idx[$_stack_test_pointer] :=\
 %_stack_test_idx[$_stack_test_pointer - 1] + 5
%_stack_test_arr[0 + %_stack_test_idx[$_stack_test_pointer]] := 0
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 3)
%_stack_test_arr[%_for_loop_idx[$_for_loop_curr_idx]\
 + 1 + %_stack_test_idx[$_stack_test_pointer]] := 0
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)
%_stack_test_arr[4 + %_stack_test_idx[$_stack_test_pointer]] := 0'''


# @t.skip
class TestStackFrameArray(DevTest):

    def runTest(self):
        KSP.set_compiled(True)
        arr = kArrInt([1, 2, 3, 4, 5])
        f_arr = StackFrameArray(arr, 2, 5)
        idx = kInt(2)
        self.assertEqual(f_arr[idx].val, '%kArrInt0[$kInt0 + 2]')
        self.assertEqual(f_arr[idx]._get_runtime(), 5)
        f_arr[idx] <<= 3
        self.assertEqual(f_arr[idx].val, '%kArrInt0[$kInt0 + 2]')
        self.assertEqual(f_arr[idx]._get_runtime(), 3)

        with For(arr=f_arr) as s:
            for idx, i in enumerate(s):
                self.assertEqual(
                    i.val,
                    '%kArrInt0[%_for_loop_idx[$_for_loop_curr_idx] + 2]')

        for idx, val in enumerate(f_arr.iter_runtime()):
            self.assertEqual(val, arr[idx + 2]._get_runtime())


# @t.skip
class TestStack(DevTest):

    # @t.skip
    def test_arrays(self):
        KSP.set_compiled(True)
        stack = Stack('test',
                      kArrInt,
                      10)
        arr = kArrInt([1, 2, 3, 4, 5])
        returned = stack.push(arr)[0]
        self.assertIsInstance(returned, StackFrameArray)
        self.assertEqual(
            returned[1].val,
            '%_stack_test_arr[1 + (0 + ' +
            '%_stack_test_idx[$_stack_test_pointer])]')
        idx = kInt(4)
        self.assertEqual(
            returned[idx].val,
            '%_stack_test_arr[$kInt0 + (0 + ' +
            '%_stack_test_idx[$_stack_test_pointer])]')
        with self.assertRaises(IndexError):
            returned[idx + 1].val
        stack.pop()

        returned = stack.push(kLoc(int, 5))[0]
        self.assertIsInstance(returned, StackFrameArray)
        self.assertEqual(
            returned[1].val,
            '%_stack_test_arr[1 + (0 + ' +
            '%_stack_test_idx[$_stack_test_pointer])]')
        idx = kInt(4)
        self.assertEqual(returned[idx].val,
                         '%_stack_test_arr[$kInt1 + (0 + ' +
                         '%_stack_test_idx[$_stack_test_pointer])]')
        with self.assertRaises(IndexError):
            returned[idx + 1].val

    # @t.skip
    def test_push(self):
        self.maxDiff = None
        KSP.set_compiled(True)
        stack = Stack('test',
                      kArrInt,
                      10)
        x = kInt(1, 'x')
        y = kInt(2, 'y')
        arr = kArrInt([3, 4, 5])
        ret_x, ret_y, ret_arr = stack.push(x, y, arr)
        self.assertEqual(
            ret_x._get_compiled(),
            '%_stack_test_arr[0 +' +
            ' %_stack_test_idx[$_stack_test_pointer]]')
        self.assertEqual(
            ret_y._get_compiled(),
            '%_stack_test_arr[1 +' +
            ' %_stack_test_idx[$_stack_test_pointer]]')
        self.assertEqual(ret_x._get_runtime(), 1)
        self.assertEqual(ret_y._get_runtime(), 2)
        # print(ret_arr._get_runtime())
        with For(arr=ret_arr) as s:
            for idx, var in enumerate(s):
                self.assertEqual(
                    var._get_compiled(),
                    '%_stack_test_arr[%_for_loop_idx[' +
                    f'$_for_loop_curr_idx] + (2 + ' +
                    '%_stack_test_idx[$_stack_test_pointer])]')
                self.assertEqual(var._get_runtime(),
                                 arr[idx]._get_runtime())
        if KSP.is_compiled():
            # print(unpack_lines(Output().get()))
            self.assertEqual(unpack_lines(Output().get()), push_output)
        Output().refresh()
        stack.push(kLoc(int), kLoc(int, 3), kLoc(int))
        self.assertEqual(unpack_lines(Output().get()), push_lvl2_output)

    # @t.skip
    def test_pop(self):
        KSP.set_compiled(True)
        stack = Stack('test',
                      kArrInt,
                      10)
        with self.assertRaises(IndexError):
            stack.pop()
        stack.push(kLoc(int), kLoc(int, 2), kLoc(int))
        stack.pop()
        self.assertEqual(Output().pop(), 'dec($_stack_test_pointer)')

    # @t.skip
    def test_empty(self):
        stack = Stack('test',
                      kArrInt,
                      10)
        self.assertTrue(stack.is_empty())
        stack.push(kLoc(int))
        self.assertFalse(stack.is_empty())
        stack.pop()
        self.assertTrue(stack.is_empty())


multi_push = '''inc($_stack_test_int_pointer)
%_stack_test_int_idx[$_stack_test_int_pointer] \
:= %_stack_test_int_idx[$_stack_test_int_pointer - 1] + 4
%_stack_test_int_arr[0 + %_stack_test_int_idx\
[$_stack_test_int_pointer]] := 0
inc($_stack_test_str_pointer)
%_stack_test_str_idx[$_stack_test_str_pointer] \
:= %_stack_test_str_idx[$_stack_test_str_pointer - 1] + 4
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 2)
!_stack_test_str_arr[%_for_loop_idx[$_for_loop_curr_idx] \
+ 0 + %_stack_test_str_idx[$_stack_test_str_pointer]] := ""
%_for_loop_idx[$_for_loop_curr_idx] := %_for_loop_idx\
[$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)'''


# @t.skip
class TestMultiStack(DevTest):

    def runTest(self):
        KSP.set_compiled(True)
        stack = MultiStack('test', 10)
        _int1 = kInt(1)
        _int2 = kInt(2)
        _int_arr = kArrInt([3, 4])
        _str1 = kStr('1')
        _str2 = kStr('2')
        _str_arr = kArrStr(['3', '4'])
        _real1 = kReal(1.0)
        _real2 = kReal(2.0)
        _real_arr = kArrReal([3.0, 4.0])

        self.assertTrue(stack.is_empty())

        _int1, _int2, _int_arr, _str1, _str2, _str_arr, _real1, \
            _real2, _real_arr = stack.push(_int1,
                                           _int2,
                                           _int_arr,
                                           _str1,
                                           _str2,
                                           _str_arr,
                                           _real1,
                                           _real2,
                                           _real_arr)
        self.assertFalse(stack.is_empty())
        self.assertEqual(_int1.val,
                         '%_stack_test_int_arr[0 + ' +
                         '%_stack_test_int_idx[$_stack_test_int_pointer]]')
        self.assertEqual(_int1._get_runtime(), 1)
        self.assertEqual(_int2.val,
                         '%_stack_test_int_arr[1 + ' +
                         '%_stack_test_int_idx[$_stack_test_int_pointer]]')
        self.assertEqual(_int2._get_runtime(), 2)
        self.assertEqual(_int_arr[0].val,
                         '%_stack_test_int_arr[0 + (2 + ' +
                         '%_stack_test_int_idx[$_stack_test_int_pointer])]')
        self.assertEqual(_int_arr[0]._get_runtime(), 3)
        self.assertEqual(_int_arr[1].val,
                         '%_stack_test_int_arr[1 + (2 + ' +
                         '%_stack_test_int_idx[$_stack_test_int_pointer])]')
        self.assertEqual(_int_arr[1]._get_runtime(), 4)

        self.assertEqual(_str1.val,
                         '!_stack_test_str_arr[0 + ' +
                         '%_stack_test_str_idx[$_stack_test_str_pointer]]')
        self.assertEqual(_str1._get_runtime(), '1')
        self.assertEqual(_str2.val,
                         '!_stack_test_str_arr[1 + ' +
                         '%_stack_test_str_idx[$_stack_test_str_pointer]]')
        self.assertEqual(_str2._get_runtime(), '2')
        self.assertEqual(_str_arr[0].val,
                         '!_stack_test_str_arr[0 + (2 + ' +
                         '%_stack_test_str_idx[$_stack_test_str_pointer])]')
        self.assertEqual(_str_arr[0]._get_runtime(), '3')
        self.assertEqual(_str_arr[1].val,
                         '!_stack_test_str_arr[1 + (2 + ' +
                         '%_stack_test_str_idx[$_stack_test_str_pointer])]')
        self.assertEqual(_str_arr[1]._get_runtime(), '4')

        self.assertEqual(
            _real1.val,
            '?_stack_test_real_arr[0 + ' +
            '%_stack_test_real_idx[$_stack_test_real_pointer]]')
        self.assertEqual(_real1._get_runtime(), 1.0)
        self.assertEqual(
            _real2.val,
            '?_stack_test_real_arr[1 + ' +
            '%_stack_test_real_idx[$_stack_test_real_pointer]]')
        self.assertEqual(_real2._get_runtime(), 2.0)
        self.assertEqual(
            _real_arr[0].val,
            '?_stack_test_real_arr[0 + (2 + ' +
            '%_stack_test_real_idx[$_stack_test_real_pointer])]')
        self.assertEqual(_real_arr[0]._get_runtime(), 3.0)
        self.assertEqual(
            _real_arr[1].val,
            '?_stack_test_real_arr[1 + (2 + ' +
            '%_stack_test_real_idx[$_stack_test_real_pointer])]')
        self.assertEqual(_real_arr[1]._get_runtime(), 4.0)

        Output().refresh()

        loc_int, loc_str_arr = stack.push(kLoc(int), kLoc(str, 2))
        self.assertEqual(unpack_lines(Output().get()), multi_push)

        with self.assertRaises(IndexError):
            stack.push(kLoc(str, 5))

        Output().refresh()
        stack.pop()
        self.assertEqual(Output().get(), [
            'dec($_stack_test_int_pointer)',
            'dec($_stack_test_str_pointer)'
        ])

        Output().refresh()
        stack.pop()
        self.assertEqual(Output().get(), [
            'dec($_stack_test_int_pointer)',
            'dec($_stack_test_str_pointer)',
            'dec($_stack_test_real_pointer)'
        ])
        self.assertTrue(stack.is_empty())


if __name__ == '__main__':
    t.main()
