import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from ksp_code import KspCode
from kspvar import KspVarObj
from interfaces import IOutput
from interfaces import IName

path = os.path.dirname(__file__)


class TestKspCode(t.TestCase):

    def setUp(self):
        IName.refresh()

    def test_file_replacement(self):
        Lines_in = list()
        IOutput.set(Lines_in)

        x = 5
        y = KspVarObj('myvar_object')
        text = 'my_text'
        KspCode(path + '/ksp_source.ksp',
                var1=x, myvar=y, mytextvar=text)

        with open(path + '/ksp_replaced.ksp') as f:
            Lines_out = f.readlines()
            f.close()

        IOutput.release()

        self.assertEqual(Lines_in, Lines_out)


if __name__ == '__main__':
    t.main()
