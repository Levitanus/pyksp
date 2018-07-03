import os
import sys
path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from dev_tools import unpack_lines
from dev_tools import DevTest
import unittest as t

from interfaces import IOutput
from native_types import kInt
from abstract import KSP
from conditions import *
from context_tools import check
from context_tools import CondFalse

if_string = '''if($x = $y and $x # 2)
$x := $x + 1
end if
if($y = 1)
$x := $x + 1
if($y # 2)
$x := $x + 1
end if
else
if($x # $y and $x = 1)
$x := $x + 1
else
$y := $y + 1
end if
end if
'''

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
end select
'''


class TestIf(DevTest):

    def runTest(self):
        self.setUp()
        self.code()
        self.setUp()
        KSP.toggle_test_state(True)
        self.code()

    def code(self):
        x = kInt('x', 1)
        y = kInt('y', 2)
        code = list()
        IOutput.set(code)
        with If((x == y) & (x != 2)):
            check()
            x += 1
            if KSP.is_under_test():
                self.assertEqual(x(), 1)
        with If(y == 1):
            check()
            x += 1
            if KSP.is_under_test():
                self.assertEqual(x(), 2)
            with If(y != 2):
                check()
                x += 1
                if KSP.is_under_test():
                    self.assertEqual(x(), 2)
        with Else((x != y) & (x == 1)):
            check()
            x += 1
            if KSP.is_under_test():
                self.assertEqual(x(), 2)
        with Else():
            check()
            y += 1
            if KSP.is_under_test():
                self.assertEqual(y, 3)
        if not KSP.is_under_test():
            code = unpack_lines(code)
            self.assertEqual(code, if_string)

        with self.assertRaises(KspCondError):
            with Else():
                pass
        with self.assertRaises(KspCondError):
            with If(x == y):
                pass
            x(1)
            with Else():
                pass


class TestSelect(DevTest):

    def runTest(self):
        self.setUp()
        self.code()
        self.setUp()
        KSP.toggle_test_state(True)
        self.code()

    def code(self):
        x = kInt('x', 2)
        y = kInt('y', 1)
        y(1)

        code = list()
        IOutput.set(code)
        with Select(x):
            with Case(1):
                check()
                y += 1
            with self.assertRaises(KspCondError):
                y(1)
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
        if KSP.is_under_test():
            self.assertEqual(y(), 3)
        else:
            code = unpack_lines(code)
            self.assertEqual(code, select_string)


if __name__ == '__main__':
    t.main().runTests()
