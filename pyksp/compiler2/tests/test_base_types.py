from main import DevTest
import unittest as t

from base_types import *


class TestAstBase(DevTest):

    class AstChildBad(AstBase):
        pass

    class AstChild(AstBase):

        def expand(self):
            return 'exanded'

    def runTest(self):
        with self.assertRaises(TypeError):
            self.AstChildBad()
        x = self.AstChild()
        self.assertEqual(x.expand(), 'exanded')


if __name__ == '__main__':
    t.main()
