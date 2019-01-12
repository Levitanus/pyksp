
import unittest as t

ismain: bool = False
if __name__ == '__main__':
    __name__ = 'pyksp.compiler.tests.test_abstract'
    ismain = True
from .mytests import DevTest
from ..abstract import *


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

        IName.set_compact(False)
        IName.scope('lvl1_')
        scoped_a = self.Test3()
        self.assertEqual(scoped_a.name(), '$lvl1_my name')

        IName.scope('lvl2_')
        scoped_b = self.Test3()
        self.assertEqual(scoped_b.name(), '$lvl2_my name')
        self.assertEqual(scoped_a.name(), '$lvl1_my name')

        IName.scope()
        with self.assertRaises(NameError):
            self.Test3()
        scoped_c = self.Test3(name='name')
        self.assertEqual(scoped_c.name(), '$lvl1_name')
        IName.scope()


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

    def setUp(self)->None:
        Output().refresh()
        Output().release()

    def test_core(self):
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

    def test_indents(self):
        otpt = Output()
        KSP.indents = 2
        otpt.put('line1')
        otpt.indent()
        otpt.put('line2')
        otpt.indent()
        otpt.put('line3')
        KSP.indents = 3
        otpt.put('line4')
        otpt.unindent()
        otpt.put('line5')
        otpt.unindent()
        otpt.put('line6')
        with self.assertRaises(otpt.IndentError):
            otpt.unindent()
        otpt.put('line7')
        self.assertEqual(otpt.get(),
                         ['line1',
                          '  line2',
                          '    line3',
                          # indents = 3
                          '      line4',
                          '   line5',
                          'line6',
                          'line7'])

    def test_block(self):
        otpt = Output()
        otpt.put('before passed')
        otpt.blocked = True
        otpt.put('blocked')
        self.assertTrue(otpt.blocked)
        otpt.blocked = False
        otpt.put('after passed')
        self.assertEqual(otpt.get(),
                         ['before passed',
                          'after passed'])

    def my_call(self):
        self.temp = 'my_call'


if ismain:
    t.main()
