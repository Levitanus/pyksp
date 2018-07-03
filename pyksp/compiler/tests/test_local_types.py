import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from abstract import KSP
from dev_tools import DevTest

from interfaces import IOutput

from local_types import *


class TestLocalTypes(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_loc_int_return(self):
        KSP.toggle_test_state(True)
        self.loc_int()

    def test_loc_int_code(self):
        KSP.toggle_test_state(False)
        self.loc_int()

    def loc_int(self):
        code = list()
        IOutput.set(code)
        x = kLocInt('x', 1)
        if KSP.is_under_test():
            self.assertEqual(x + 1, 2)
        else:
            self.assertEqual((x + 1)(), '$x + 1')

        x(2)
        if KSP.is_under_test():
            self.assertEqual(x(), 2)
        else:
            self.assertEqual(code[-1], '$x := 2')

        x += 1
        if KSP.is_under_test():
            self.assertEqual(x(), 3)
        else:
            self.assertEqual(code[-1], '$x := $x + 1')

    def test_loc_str_return(self):
        KSP.toggle_test_state(True)
        self.loc_str()

    def test_loc_str_code(self):
        KSP.toggle_test_state(False)
        self.loc_str()

    def loc_str(self):
        code = list()
        IOutput.set(code)
        x = kLocStr('x', '1')
        if KSP.is_under_test():
            self.assertEqual(x + '1', '11')
        else:
            self.assertEqual((x + '1'), '@x & 1')

        x('2')
        if KSP.is_under_test():
            self.assertEqual(x(), '2')
        else:
            self.assertEqual(code[-1], '@x := 2')

        y = kLocInt('y', 2)
        x += y
        if KSP.is_under_test():
            self.assertEqual(x(), '22')
        else:
            self.assertEqual(code[-1], '@x := @x & $y')

    def test_arr_int_return(self):
        KSP.toggle_test_state(True)
        self.arr_int()

    def test_arr_int_code(self):
        KSP.toggle_test_state(False)
        self.arr_int()

    def arr_int(self):
        code = list()
        IOutput.set(code)
        x = kLocArrInt('x', [1, 2, 4, 5])
        if KSP.is_under_test():
            self.assertEqual(x[0] + 1, 2)
        else:
            self.assertEqual((x[0] + 1)(), '%x[0] + 1')

        x[1] = 2
        if KSP.is_under_test():
            self.assertEqual(x[1], 2)
        else:
            self.assertEqual(code[-1], '%x[1] := 2')

        x[1] += 1
        if KSP.is_under_test():
            self.assertEqual(x[1], 3)
        else:
            self.assertEqual(code[-1], '%x[1] := %x[1] + 1')

        x[1] *= 2
        if KSP.is_under_test():
            self.assertEqual(x[1], 6)
        else:
            self.assertEqual(code[-1], '%x[1] := %x[1] * 2')

        y = kLocInt('y', 1)
        x[1] = 1
        x[1] += y
        if KSP.is_under_test():
            self.assertEqual(x[1], 2)
        else:
            self.assertEqual(code[-1], '%x[1] := %x[1] + $y')

    def test_arr_str_return(self):
        KSP.toggle_test_state(True)
        self.arr_str()

    def test_arr_str_code(self):
        KSP.toggle_test_state(False)
        self.arr_str()

    def arr_str(self):
        code = list()
        IOutput.set(code)
        x = kLocArrStr('x', ['1', '2', '4', '5'])
        if KSP.is_under_test():
            self.assertEqual(x[0] + '1', '11')
        else:
            self.assertEqual((x[0] + '1')(), '!x[0] & 1')

        x[1] = 2
        if KSP.is_under_test():
            self.assertEqual(x[1], '2')
        else:
            self.assertEqual(code[-1], '!x[1] := 2')

        x[1] += '1'
        if KSP.is_under_test():
            self.assertEqual(x[1], '21')
        else:
            self.assertEqual(code[-1], '!x[1] := !x[1] & 1')

    def test_arr_real_return(self):
        KSP.toggle_test_state(True)
        self.arr_real()

    def test_arr_real_code(self):
        KSP.toggle_test_state(False)
        self.arr_real()

    def arr_real(self):
        code = list()
        IOutput.set(code)
        x = kLocArrReal('x', [1.0, 2.2, 4.3, 5.0])
        if KSP.is_under_test():
            self.assertEqual(x[0] + 1.1, 2.1)
        else:
            self.assertEqual((x[0] + 1.1)(), '?x[0] + 1.1')

        x[1] = 2.0
        if KSP.is_under_test():
            self.assertEqual(x[1], 2.0)
        else:
            self.assertEqual(code[-1], '?x[1] := 2.0')

        x[1] += 1
        if KSP.is_under_test():
            self.assertEqual(x[1], 3)
        else:
            self.assertEqual(code[-1], '?x[1] := ?x[1] + 1')

        x[1] *= 2
        if KSP.is_under_test():
            self.assertEqual(x[1], 6)
        else:
            self.assertEqual(code[-1], '?x[1] := ?x[1] * 2')


if __name__ == '__main__':
    t.main()
