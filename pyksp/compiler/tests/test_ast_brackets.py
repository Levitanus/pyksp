import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from native_types import kInt
from abstract import KSP


class TestBrackets(DevTest):

    def runTest(self):
        KSP.set_compiled(True)
        x = kInt(name='x')
        y = kInt(name='y')

        self.assertEqual((x + y).expand(), '$x + $y')
        self.assertEqual((x + y + x).expand(), '$x + $y + $x')
        self.assertEqual((x + (y + x)).expand(), '$x + ($y + $x)')
        self.assertEqual((x + y * x).expand(), '$x + $y * $x')
        self.assertEqual(((x + y) * x).expand(), '($x + $y) * $x')
        self.assertEqual((x * (y * x)).expand(), '$x * ($y * $x)')
        self.assertEqual((x * x * y | y * x).expand(),
                         '$x * $x * $y .or. $y * $x')
        self.assertEqual((x * (x * y | y * x)).expand(),
                         '$x * ($x * $y .or. $y * $x)')


if __name__ == '__main__':
    t.main()
