import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from stack import *
from kspvar import KspVarObj
from interfaces import IOutput
# from interfaces import IName
from native_types import kInt
from native_types import kArrInt
from native_types import kStr
from native_types import kReal

from dev_tools import DevTest
from dev_tools import unpack_lines

from abstract import KSP
from abstract import KspObject


class TestFrameVar(DevTest):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_attributes(self):
        var = FrameVar('name', 2)
        self.assertEqual(var.val, 2)
        self.assertEqual(var.len, 1)

    def test_kInt_code(self):
        KSP.toggle_test_state(False)
        x = kInt('x', 3)
        var_x = FrameVar('x', x)
        self.assertEqual((var_x.val + 2)(), '$x + 2')

    def test_kArrInt_code(self):
        KSP.toggle_test_state(False)
        arr = kArrInt('arr', [1, 2, 3, 4, 5], length=5)
        seq = [arr[2:4]]
        var_arr = FrameVar('arr', seq)
        for idx, val in enumerate(var_arr.val):
            self.assertEqual(val, f'%arr[{idx+2}]')


class TestStackFrame(DevTest):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def runTest(self):
        x = FrameVar('x', 1)
        y = FrameVar('y', 3)
        arr = FrameVar('arr', [1, 2, 4, 5])
        frame = StackFrame(x, y, arr)
        self.assertEqual(frame.size, 6)
        self.assertIs(frame['x'], x)
        self.assertIs(frame['y'], y)
        self.assertIs(frame['arr'], arr)
        self.assertEqual(frame['arr'].len, 4)


couple_push_lines = '''%stack_methods_arr\
[%stack_methods_idx[$stack_methods_curr] + 0]\
 := $x
%stack_methods_arr[%stack_methods_idx[$stack_methods_curr] + 1] := $y
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 3)
%stack_methods_arr[%stack_methods_idx[$stack_methods_curr] + 2 + 0]\
 := %arr[%_for_loop_idx[$_for_loop_curr_idx]]
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)
%stack_methods_idx[$stack_methods_curr + 1] := \
%stack_methods_idx[$stack_methods_curr] + 5
$stack_methods_curr := $stack_methods_curr + 1
%stack_methods_arr[%stack_methods_idx[$stack_methods_curr] + 0] := $x
%stack_methods_arr[%stack_methods_idx[$stack_methods_curr] + 1] := $y
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 3)
%stack_methods_arr[%stack_methods_idx[$stack_methods_curr] + 2 + 0]\
 := %arr[%_for_loop_idx[$_for_loop_curr_idx]]
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)
'''


class TestStackMethods(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.stack = Stack('methods', 1000, kInt)

    def tearDown(self):
        super().tearDown()

    def test_push_arg_code(self):
        KSP.toggle_test_state(False)
        self.push_arg()

    def test_push_arg_returns(self):
        KSP.toggle_test_state(True)
        self.push_arg()

    def push_arg(self):
        func = self.stack.push_arg

        var, count = func('arg1', 1, 0)
        self.assertIsInstance(var, FrameVar)
        self.assertIsInstance(count, int)
        self.assertEqual(var.name, 'arg1')
        self.assertEqual(var.val, 1)
        self.assertEqual(var.len, 1)
        self.assertEqual(count, 1)

        code = list()
        IOutput.set(code)
        arg2 = kArrInt('arg2', [1, 2, 3])
        var, count = func('arg2', arg2, 1)
        self.assertEqual(var.len, 3)
        self.assertEqual(count, 4)
        if not KSP.is_under_test():
            desired_out = [
                'inc($_for_loop_curr_idx)',
                '%_for_loop_idx[$_for_loop_curr_idx] := 0',
                'while(%_for_loop_idx[$_for_loop_curr_idx] < 3)',
                '%stack_methods_arr[%stack_methods_idx[$stack_methods_curr]' +
                ' + 1 + 0] := %arg2[%_for_loop_idx[$_for_loop_curr_idx]]',
                'inc(%_for_loop_idx[$_for_loop_curr_idx])',
                'end while',
                'dec($_for_loop_curr_idx)'
            ]
            self.assertEqual(code, desired_out)

    def test_push_local_code(self):
        KSP.toggle_test_state(False)
        self.push_local()

    def test_push_local_returns(self):
        KSP.toggle_test_state(True)
        self.push_local()

    def push_local(self):
        func = self.stack.puch_local_arg

        var, count = func('arg1', 1, 0)
        self.assertIsInstance(var, FrameVar)
        self.assertIsInstance(count, int)
        self.assertEqual(var.name, 'arg1')
        self.assertEqual(var(), 0)
        self.assertEqual(var.len, 1)
        self.assertEqual(count, 1)

        code = list()
        IOutput.set(code)
        arg2 = kArrInt('arg2', [1, 2, 3])
        var, count = func('arg2', arg2, 1)
        self.assertEqual(var.len, 3)
        self.assertEqual(count, 4)
        if not KSP.is_under_test():
            desired_out = []
            self.assertEqual(code, desired_out)

    def test_push_vals(self):
        KSP.toggle_test_state(True)
        self.push()

    def test_push_code(self):
        KSP.toggle_test_state(False)
        self.push()

    def push(self):
        func = self.stack.push
        frame_vars = dict()
        frame_vars['x'] = kInt('x', 1)
        frame_vars['y'] = kInt('y', 3)
        frame_vars['arr'] = kArrInt('arr', [2, 4, 5])

        code = list()
        IOutput.set(code)
        func(**frame_vars)
        func(**frame_vars)
        frame = self.stack.peek()
        self.assertEqual(frame.size, 5)
        if KSP.is_under_test():
            self.assertEqual(frame['x'].val, frame_vars['x']())
            self.assertEqual(frame['y'].val, frame_vars['y']())
            self.assertEqual(frame['arr'].val, frame_vars['arr']())
            frame['x'].val += 1
            self.assertEqual(frame['x'].val, frame_vars['x']() + 1)
        if not KSP.is_under_test():
            self.assertEqual(
                frame['x'].val(),
                '%stack_methods_arr[%stack_methods_idx' +
                '[$stack_methods_curr] + 0]')
            self.assertEqual(
                frame['y'].val(),
                '%stack_methods_arr[%stack_methods_idx' +
                '[$stack_methods_curr] + 1]')
            self.assertEqual(
                frame['arr'].val[0],
                '%stack_methods_arr[%stack_methods_idx' +
                '[$stack_methods_curr] + 2 + 0]')
            self.assertEqual(
                frame['arr'].val[1],
                '%stack_methods_arr[%stack_methods_idx' +
                '[$stack_methods_curr] + 2 + 1]')
            self.assertEqual(
                frame['arr'].val[2],
                '%stack_methods_arr[%stack_methods_idx' +
                '[$stack_methods_curr] + 2 + 2]')

            self.assertEqual(unpack_lines(code), couple_push_lines)

    def test_generate_init(self):
        self.generate_init_proxy('int', kInt, '%')
        self.generate_init_proxy('str', kStr, '!')
        self.generate_init_proxy('real', kReal, '?')

    def generate_init_proxy(self, name, type_ref, prefix):
        KspVarObj.refresh()
        IOutput.refresh()
        name = name
        size = 1000
        depth = 100
        Stack(name, size, type_ref, depth)
        desired_init = [
            'declare $stack_%s_curr' % name,
            'declare {}stack_{}_arr[{}]'.format(prefix, name, size),
            'declare %stack_{}_idx[{}]'.format(name, depth)
        ]
        KspObject_init = KspObject.generate_init()
        self.assertEqual(KspObject_init, desired_init)


if __name__ == '__main__':
    t.main()
