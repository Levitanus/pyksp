import os
import sys
import unittest as t
import re

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from functions import Func
from interfaces import IOutput
from interfaces import IName
from abstract import KspObject


@t.skip
class TestFunctions(t.TestCase):

    def tearDown(self):
        IOutput.refresh()
        IName.refresh()
        KspObject.refresh()

    def test_decorator_args(self):

        @Func
        def foo(arg1: int, arg2: int,
                kwarg1: int=5, kwarg2: str='str'):
            IOutput.put('arg1 is %s, arg2 is %s, kwarg1 is %s' %
                        (arg1, arg2, kwarg1))
        with self.assertRaises(TypeError):
            foo(1, 2, kwarg2=2)

        with self.assertRaises(TypeError):
            @Func
            def foo_bad(arg1, arg2: str, kwarg1=2, kwarg2: int=5):
                pass

    def test_full_name(self):

        @Func
        def foo():
            pass
        module_name = globals()['__name__']
        module_name = re.sub(r'\.', '__', module_name)
        self.foo_name = module_name + \
            'TestFunctions__test_full_name__foo'
        foo_name = foo.name()
        self.assertEqual(foo_name, self.foo_name)

    def test_inline_representation(self):

        string = 'arg1 is %s, arg2 is %s, karg1 is %s'

        @Func
        def foo(arg1: int, arg2: int, kwarg1: int=5):
            IOutput.put(string % (arg1, arg2, kwarg1))

        code = list()
        IOutput.set(code)
        foo(1, 2, kwarg1=4, inline=True)
        IOutput.release()
        self.assertEqual(code[0], string % (1, 2, 4))


if __name__ == '__main__':
    t.main()
