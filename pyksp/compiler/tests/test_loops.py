import os
import sys
path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from dev_tools import unpack_lines
from dev_tools import DevTest
import unittest as t

from interfaces import IOutput
from native_types import kInt
from native_types import kArrInt
from abstract import KSP
from loops import *

from context_tools import check
from context_tools import Break
from context_tools import KspCondError

from conditions import If, Else

default_for_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 5)
$x := %arrX[%_for_loop_idx[$_for_loop_curr_idx]]
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)
'''
folded_for_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 5)
$x := %arrX[%_for_loop_idx[$_for_loop_curr_idx]]
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 4)
if($x = %arrY[%_for_loop_idx[$_for_loop_curr_idx]])
$y := %arrY[%_for_loop_idx[$_for_loop_curr_idx]]
else
%_for_loop_idx[$_for_loop_curr_idx] := 4
end if
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)
'''


class TestForEach(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.arrX = kArrInt('arrX', [1, 3, 4, 6, 8], length=5)
        self.x = kInt('x')
        self.code = list()
        IOutput.set(self.code)

    def tearDown(self):
        super().tearDown()
        self.code.clear()

    def test_simple_out(self):
        self.simple_for()

    def test_simple_returns(self):
        KSP.toggle_test_state(True)
        self.simple_for()

    def simple_for(self):
        with For(arr=self.arrX) as seq:
            for idx, val in enumerate(seq):
                self.x(val)
                if KSP.is_under_test():
                    with self.subTest():
                        self.assertEqual(self.x(), self.arrX[idx])
        if not KSP.is_under_test():
            out = unpack_lines(self.code)
            self.assertEqual(out, default_for_string)

    def test_folded_out(self):
        KSP.toggle_test_state(False)
        self.folded_for()

    def test_folded_returns(self):
        KSP.toggle_test_state(True)
        self.folded_for()

    def folded_for(self):
        arrY = kArrInt('arrY', [1, 2, 3, 6])
        y = kInt('y')
        break_indicies = [0, 2, 3, 3, 3]
        with For(arr=self.arrX) as seq:
            for idx, val in enumerate(seq):
                self.x(val)
                with For(arr=arrY) as seq_y:
                    for idx2, val2 in enumerate(seq_y):
                        with If(self.x == val2):
                            check()
                            y(val2)
                            with self.subTest():
                                self.assertEqual(
                                    idx2, break_indicies[idx])
                        with Else():
                            check()
                            Break()
        if not KSP.is_under_test():
            out = unpack_lines(self.code)
            self.assertEqual(out, folded_for_string)


start_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 20)
$x := %_for_loop_idx[$_for_loop_curr_idx]
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)
'''

stop_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 2
while(%_for_loop_idx[$_for_loop_curr_idx] < 5)
$x := %_for_loop_idx[$_for_loop_curr_idx]
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)
'''

step_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 2
while(%_for_loop_idx[$_for_loop_curr_idx] < 20)
$x := %_for_loop_idx[$_for_loop_curr_idx]
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 2
end while
dec($_for_loop_curr_idx)
'''


class TestForRange(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.code = list()
        IOutput.set(self.code)

    def tearDown(self):
        super().tearDown()
        self.code.clear()

    def test_exceptions(self):
        arrX = kArrInt('arr', [1, 2, 4])
        with self.assertRaises(KspCondError):
            For(arr=[1, 2, 5])
        with self.assertRaises(KspCondError):
            For(1, arr=arrX)
        with self.assertRaises(KspCondError):
            For(stop=2)
        with self.assertRaises(KspCondError):
            For(step=2)
        with self.assertRaises(KspCondError):
            For(stop=2, step=2)
        with self.assertRaises(KspCondError):
            For(20.3)
        with self.assertRaises(KspCondError):
            For(20, 0.3)
        with self.assertRaises(KspCondError):
            For(20, 10, 4.0)
        with self.assertRaises(KspCondError):
            For()
        x = kInt('x', 5)
        self.assertTrue(For(x))
        self.assertTrue(For(arrX[0]))

    def test_start_out(self):
        KSP.toggle_test_state(False)
        self.start()

    def test_start_return(self):
        KSP.toggle_test_state(True)
        self.start()

    def start(self):
        x = kInt('x')
        with For(20) as name:
            for idx, i in enumerate(name):
                x(i)
                if KSP.is_under_test():
                    with self.subTest():
                        self.assertEqual(i, idx)
        if KSP.is_under_test():
            self.assertEqual(x(), 19)
        if not KSP.is_under_test():
            out = unpack_lines(self.code)
            self.assertEqual(out, start_string)

    def test_stop_out(self):
        KSP.toggle_test_state(False)
        self.stop()

    def test_stop_return(self):
        KSP.toggle_test_state(True)
        self.stop()

    def stop(self):
        x = kInt('x')
        with For(2, 5) as name:
            for idx, i in enumerate(name):
                x(i)
                if KSP.is_under_test():
                    with self.subTest():
                        self.assertEqual(i, idx + 2)
        if KSP.is_under_test():
            self.assertEqual(x(), 4)
        if not KSP.is_under_test():
            out = unpack_lines(self.code)
            self.assertEqual(out, stop_string)

    def test_step_out(self):
        KSP.toggle_test_state(False)
        self.step()

    def test_step_return(self):
        KSP.toggle_test_state(True)
        self.step()

    def step(self):
        x = kInt('x')
        with For(2, 20, 2) as name:
            for idx, i in enumerate(name):
                x(i)
                if KSP.is_under_test():
                    with self.subTest():
                        self.assertEqual(i, (idx) * 2 + 2)
        if KSP.is_under_test():
            self.assertEqual(x(), 18)
        if not KSP.is_under_test():
            out = unpack_lines(self.code)
            self.assertEqual(out, step_string)


while_string = '''while($x # $y)
if($y # 10)
$y := 10
end if
$x := $x + 1
end while
'''


class TestWhile(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.x = kInt('x', 0)
        self.y = kInt('y', 10)
        self.x(0)
        self.y(10)
        self.code = list()
        IOutput.set(self.code)

    def tearDown(self):
        super().tearDown()

    def test_generator(self):
        KSP.toggle_test_state(False)
        self.main()

    def test_return(self):
        KSP.toggle_test_state(True)
        self.main()

    def main(self):
        if KSP.is_under_test():
            self.assertEqual(self.x(), 0)
        with While() as w:
            while w(lambda x=self.x, y=self.y: x != y):
                with If(self.y != 10):
                    check()
                    self.y(10)
                self.x += 1
        if KSP.is_under_test():
            self.assertEqual(self.x(), self.y())
        else:
            out = unpack_lines(self.code)
            self.assertEqual(out, while_string)


if __name__ == '__main__':
    t.main()
