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

from dev_tools import print_lines
from dev_tools import unpack_lines

if_lines = \
    '''if($x < $y or $x = 1)
$x := $y
if($y = 2)
$y := $y + 1
else
if($x = 1 and $y = 2)
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
        # with self.assertRaises(KspCondError):
        #     y <<= 1
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


class TestLoops(DevTest):

    def test_ForLoops(self):
        KSP.set_compiled(True)
        f = ForLoops()
        d = ForLoops()
        x = f.get_idx()
        self.assertEqual(x.val, '%_for_loop_idx[$_for_loop_idx_curr]')
        self.assertEqual(Output().pop(), 'inc($_for_loop_idx_curr)')
        y = d.get_idx()
        self.assertEqual(y.val, '%_for_loop_idx[$_for_loop_idx_curr]')
        self.assertEqual(Output().pop(), 'inc($_for_loop_idx_curr)')
        f.end()
        self.assertEqual(Output().pop(), 'dec($_for_loop_idx_curr)')
        f.end()
        self.assertEqual(Output().pop(), 'dec($_for_loop_idx_curr)')


if __name__ == '__main__':
    t.main()
