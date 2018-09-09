import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from conditions_loops import *
# from abstract import IName
from abstract import Output
from abstract import KSP
from native_types import kInt

# from dev_tools import print_lines
from dev_tools import unpack_lines

if_lines = \
    '''if(($x < $y) or ($x = 1))
$x := $y
if($y = 2)
$y := $y + 1
else
if(($x = 1) and ($y = 2))
$y := $y + 1
else
$x := $x - 1
end if
end if
end if'''

select_string = '''select($x)
case(1)
$y := $y + 1
case(2)
$y := $y + 2
select($y)
case(2)
$y := $y + 1
case(3)
end select
end select'''

# @t.skip


class TestIf(DevTest):

    def test_compiled(self):
        KSP.set_compiled(True)

        x = kInt(1, 'x')
        y = kInt(2, 'y')
        with If((x < y) | (x == 1)):
            check()
            x <<= y
            with If(y == 2):
                check()
                y += 1
            with Else((x == 1) & (y == 2)):
                check()
                y += 1
            with Else():
                check()
                x -= 1
        self.assertEqual(unpack_lines(Output().get()), if_lines)

    def test_runtime(self):
        x = kInt(1, 'x')
        y = kInt(2, 'y')
        out = list()

        with If(x < y):
            check()
            out.append('True')
        self.assertEqual(out.pop(), 'True')
        with If(x == y):
            check()
            raise Exception('has to be False')
        with Else(x > y):
            check()
            raise Exception('has to be False')
        with Else():
            out.append('True')

        self.assertEqual(out.pop(), 'True')

# @t.skip


class TestSelect(DevTest):

    def runTest(self):
        self.setUp()
        self.code()
        self.setUp()
        KSP.set_compiled(True)
        self.code()

    def code(self):
        x = kInt(2, 'x')
        y = kInt(1, 'y')

        code = list()
        Output().set(code)
        with Select(x):
            with Case(1):
                check()
                y += 1
            with Case(2):
                check()
                y += 2
                with Select(y):
                    with Case(2):
                        check()
                        y += 1
                    with Case(3):
                        check()
                        CondFalse()
        with self.assertRaises(KspCondError):
            with Case(3):
                pass
        if not KSP.is_compiled():
            self.assertEqual(y.val, 3)
        else:
            code = unpack_lines(code)
            self.assertEqual(code, select_string)


default_for_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 5)
$x := %arrX[%_for_loop_idx[$_for_loop_curr_idx]]
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)'''

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
dec($_for_loop_curr_idx)'''


class TestForEach(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.arrX = kArrInt([1, 3, 4, 6, 8], 'arrX', size=5)
        self.x = kInt(name='x')
        self.code = list()
        Output().set(self.code)

    def tearDown(self):
        super().tearDown()
        self.code.clear()

    def test_simple_out(self):
        KSP.set_compiled(True)
        self.simple_for()

    def test_simple_returns(self):
        KSP.set_compiled(False)
        self.simple_for()

    def simple_for(self):
        with For(arr=self.arrX) as seq:
            for idx, val in enumerate(seq):
                self.x <<= val
                if not KSP.is_compiled():
                    with self.subTest():
                        self.assertEqual(self.x.val, self.arrX[idx])
        if KSP.is_compiled():
            out = unpack_lines(self.code)
            self.assertEqual(out, default_for_string)

    # @t.skip
    def test_folded_out(self):
        KSP.set_compiled(True)
        self.folded_for()

    # @t.skip
    def test_folded_returns(self):
        KSP.set_compiled(False)
        self.folded_for()

    def folded_for(self):
        arrY = kArrInt(name='arrY', sequence=[1, 2, 3, 6])
        y = kInt(name='y')
        break_indicies = [0, 2, 3, 3, 3]
        with For(arr=self.arrX) as seq:
            for idx, val in enumerate(seq):
                self.x <<= val
                with For(arr=arrY) as seq_y:
                    for idx2, val2 in enumerate(seq_y):
                        with If(self.x == val2):
                            check()
                            y <<= val2
                            with self.subTest():
                                if not KSP.is_compiled():
                                    self.assertEqual(
                                        idx2, break_indicies[idx])
                        with Else():
                            check()
                            Break()
        if KSP.is_compiled():
            out = unpack_lines(self.code)
            self.assertEqual(out, folded_for_string)


start_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 20)
$x := %_for_loop_idx[$_for_loop_curr_idx]
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)'''

stop_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 2
while(%_for_loop_idx[$_for_loop_curr_idx] < 5)
$x := %_for_loop_idx[$_for_loop_curr_idx]
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)'''

step_string = '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 2
while(%_for_loop_idx[$_for_loop_curr_idx] < 20)
$x := %_for_loop_idx[$_for_loop_curr_idx]
%_for_loop_idx[$_for_loop_curr_idx] := \
%_for_loop_idx[$_for_loop_curr_idx] + 2
end while
dec($_for_loop_curr_idx)'''


# @t.skip
class TestForRange(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.code = list()
        Output().set(self.code)

    def tearDown(self):
        super().tearDown()
        self.code.clear()

    def test_exceptions(self):
        arrX = kArrInt([1, 2, 4], 'arr')
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
        x = kInt(5, 'x')
        self.assertTrue(For(x))
        self.assertTrue(For(arrX[0]))

    # @t.skip
    def test_start_out(self):
        KSP.set_compiled(False)
        self.start()

    # @t.skip
    def test_start_return(self):
        KSP.set_compiled(True)
        self.start()

    def start(self):
        x = kInt(name='x')
        with For(20) as name:
            for idx, i in enumerate(name):
                x <<= i
                if not KSP.is_compiled():
                    with self.subTest():
                        self.assertEqual(i, idx)
        if not KSP.is_compiled():
            self.assertEqual(x.val, 19)
        else:
            out = unpack_lines(self.code)
            self.assertEqual(out, start_string)

    # @t.skip
    def test_stop_out(self):
        KSP.set_compiled(False)
        self.stop()

    # @t.skip
    def test_stop_return(self):
        KSP.set_compiled(True)
        self.stop()

    def stop(self):
        x = kInt(name='x')
        with For(2, 5) as name:
            for idx, i in enumerate(name):
                x <<= i
                if not KSP.is_compiled():
                    with self.subTest():
                        self.assertEqual(i, idx + 2)
        if not KSP.is_compiled():
            self.assertEqual(x.val, 4)
        else:
            out = unpack_lines(self.code)
            self.assertEqual(out, stop_string)

    # @t.skip
    def test_step_out(self):
        KSP.set_compiled(False)
        self.step()

    # @t.skip
    def test_step_return(self):
        KSP.set_compiled(True)
        self.step()

    def step(self):
        x = kInt(name='x')
        with For(2, 20, 2) as name:
            for idx, i in enumerate(name):
                x <<= i
                if not KSP.is_compiled():
                    with self.subTest():
                        self.assertEqual(i, (idx) * 2 + 2)
        if not KSP.is_compiled():
            self.assertEqual(x.val, 18)
        else:
            out = unpack_lines(self.code)
            self.assertEqual(out, step_string)


while_string = '''while($x # $y)
if($y # 10)
$y := 10
end if
$x := $x + 1
end while'''


# @t.skip
class TestWhile(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()
        self.x = kInt(0, 'x')
        self.y = kInt(10, 'y')
        self.x <<= 0
        self.y <<= 10
        self.code = list()
        Output().set(self.code)

    def tearDown(self):
        super().tearDown()

    def test_generator(self):
        KSP.set_compiled(True)
        self.main()

    def test_return(self):
        KSP.set_compiled(False)
        self.main()

    def main(self):
        self.assertEqual(self.x._get_runtime(), 0)
        with While() as w:
            while w(lambda x=self.x, y=self.y: x != y):
                with If(self.y != 10):
                    check()
                    self.y <<= 10
                self.x += 1
        self.assertEqual(self.x._get_runtime(), self.y._get_runtime())
        if KSP.is_compiled():
            out = unpack_lines(self.code)
            self.assertEqual(out, while_string)


if __name__ == '__main__':
    t.main()
