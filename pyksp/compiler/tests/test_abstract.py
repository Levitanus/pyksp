import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from abstract import *


class TestSingleton(DevTest):

    class Test(metaclass=SingletonMeta):
        def __init__(self, val):
            self.val = val

    def runTest(self):
        a = self.Test(1)
        b = self.Test(2)
        self.assertEqual(a.val, 1)
        self.assertEqual(b.val, 1)
        b.val = 2
        self.assertEqual(a.val, 2)


class TestKspBoolProp(DevTest):

    class Test:
        a = KspBoolProp()

    def runTest(self):
        a = self.Test()
        self.assertEqual(a.a, False)
        with self.assertRaises(TypeError):
            a.a = 4
        a.a = True
        self.assertEqual(a.a, True)
        b = self.Test()
        self.assertEqual(b.a, True)


class TestKSP(DevTest):

    class Test(KSP):
        pass

    def runTest(self):
        a = KSP()
        self.assertEqual(a.is_compiled(), False)
        a.set_compiled(True)
        self.assertEqual(a.is_compiled(), True)
        b = self.Test()
        self.assertEqual(b.is_compiled(), True)
        self.assertEqual(a.is_compiled(), True)
        self.assertEqual(b.is_bool(), False)
        KSP.set_bool(True)
        self.assertEqual(b.is_bool(), True)
        a.set_bool(False)
        self.assertEqual(b.is_bool(), False)
        a.set_bool(True)
        self.assertEqual(b.is_bool(), True)
        self.assertTrue(a.in_init())
        a.in_init(False)
        self.assertFalse(b.in_init())


class TestName(DevTest):

    class Test:

        def __init__(self, name='my name'):
            self.name = INameLocal(name)

    class Test2:

        def __init__(self, name='my name'):
            self.name = INameLocal(name, prefix='$')

    class Test3:

        def __init__(self, name='my name', preserve=False):
            self.name = IName(name, prefix='$', preserve=preserve)

    class Test4:
        def __init__(self, name='my name', postfix='[20]'):
            self.name = IName(name, prefix='@', postfix=postfix)

    def test_name(self):
        a = self.Test()
        self.assertEqual(a.name(), 'my name')
        b = self.Test2()
        self.assertEqual(b.name(), '$my name')
        self.assertEqual(a.name(), 'my name')

        c = self.Test3()
        with self.assertRaises(NameError):
            self.Test3()
        IName.set_compact(True)
        d = self.Test3(name='my name1', preserve=True)
        self.assertEqual(c.name(), '$my name')
        self.assertEqual(d.name(), '$my name1')

        e = self.Test3(name='my name2')
        self.assertEqual(e.name(), '$ccbab')
        IName.refresh()
        f = self.Test2()
        self.assertEqual(f.name(), '$my name')
        IName.set_compact(True)
        g = self.Test4()
        self.assertEqual(g.name(), '@bu20h[20]')


class TestKspObject(DevTest):

    class Test(KspObject):

        def __init__(self, name, preserve_name=False,
                     has_init=True, is_local=False, has_executable=False):
            super().__init__(name=name, preserve_name=preserve_name,
                             has_init=has_init, is_local=is_local,
                             has_executable=has_executable)

        def _generate_executable(self):
            super()._generate_executable()
            return [f'{self.name()} executable']

        def _generate_init(self):
            super()._generate_init()
            return [f'{self.name()} init']

    class BadGenerators(KspObject):

        def __init__(self, name, preserve_name=False,
                     has_init=True, is_local=False, has_executable=True):
            super().__init__(name=name, preserve_name=preserve_name,
                             has_init=has_init, is_local=is_local,
                             has_executable=has_executable)

        def _generate_executable(self):
            super()._generate_executable()
            return f'{self.name()} executable'

        def _generate_init(self):
            super()._generate_init()
            return f'{self.name()} init'

    def runTest(self):
        a = self.Test('a')

        self.assertEqual(a.generate_all_inits(), ['a init'])
        self.assertEqual(a.generate_all_executables(), [])

        b = self.BadGenerators('b')
        with self.assertRaises(TypeError):
            b.generate_all_inits()
        with self.assertRaises(TypeError):
            b.generate_all_executables()

        b.refresh()


class TestOutput(DevTest):

    def runTest(self):
        self.temp = None
        output = Output()
        out = list()
        output.set(out)
        with self.assertRaises(output.IsSetError):
            output.set(out)
        output.put('some')
        self.assertEqual(out[-1], 'some')
        self.assertEqual(output.get()[-1], 'some')
        output.release()
        output.put('else')
        self.assertEqual(out[-1], 'some')
        self.assertEqual(output.get()[-1], 'else')
        output.set(out)
        x = output.pop()
        self.assertEqual(x, 'some')
        self.assertEqual(out, [])
        output.refresh()
        self.assertEqual(output.get(), [])
        output.callable_on_put = self.my_call
        output.put('called')
        self.assertEqual(self.temp, 'my_call')
        self.assertEqual(output.get()[-1], 'called')
        output.exception_on_put = TypeError
        with self.assertRaises(TypeError):
            output.put('some')

    def my_call(self):
        self.temp = 'my_call'


if __name__ == '__main__':
    t.main()
