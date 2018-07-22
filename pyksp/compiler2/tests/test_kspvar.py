import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from kspvar import *
from interfaces import IName
from interfaces import IOutput
from abstract import KSP


class TestKspVarObj(t.TestCase):

    def setUp(self):
        IName.refresh()
        KSP.toggle_test_state(False)
        IOutput.release()

    def tearDown(self):
        IName.refresh()
        KSP.toggle_test_state(False)
        IOutput.release()

    def test_init(self):
        self.assertTrue(KspVarObj('', 1), None)
        with self.assertRaises(TypeError) as e:
            KspVarObj(5, 1)
            self.assertEqual(e.msg, 'name has to be string')
        with self.assertRaises(TypeError) as e:
            KspVarObj('5', preserve_name=1)
            self.assertEqual(e.msg, 'preserve_name has to be bool')

    def test_name(self):
        o = KspVarObj('var')
        self.assertEqual(o.name(), 'var')

        IName.compact = True
        self.assertEqual(o.name(), 'fuhgd')
        self.assertEqual(o.name(full=True), 'var')
        o = KspVarObj('var1', preserve_name=True)
        self.assertEqual(o.name(), 'var1')
        IName.compact = False

    def test_value(self):
        code = list()
        IOutput.set(code)

        var2 = KspVarObj('var1', 1)
        self.assertEqual(var2(), 'var1')
        var2(2)
        self.assertEqual(code[0], 'var1 := 2')

        KSP.toggle_test_state()
        self.assertEqual(var2(), 2)

    def test_magic(self):
        x = 4
        var = KspVarObj('var', 2)
        self.magic_proxy(var.__neg__, '-var', -var.value_get())
        var(2)

        self.magic_proxy(var.__invert__, '.not.var', ~var.value_get())
        var(2)

        self.magic_proxy(lambda x=x: var.__add__(x),
                         'var + %s' % x, var.value_get() + x)
        self.magic_proxy(lambda x=x: var.__radd__(x),
                         '%s + var' % x, var.value_get() + x)
        self.imagic_proxy(lambda x=x: var.__iadd__(x),
                          'var := var + %s' % x, var.value_get() + x)
        var(2)

        self.magic_proxy(lambda x=x: var.__sub__(x),
                         'var - %s' % x, var.value_get() - x)
        self.magic_proxy(lambda x=x: var.__rsub__(x),
                         '%s - var' % x, x - var.value_get())
        self.imagic_proxy(lambda x=x: var.__isub__(x),
                          'var := var - %s' % x, var.value_get() - x)
        var(2)

        self.magic_proxy(lambda x=x: var.__mul__(x),
                         'var * %s' % x, var.value_get() * x)
        self.magic_proxy(lambda x=x: var.__rmul__(x),
                         '%s * var' % x, x * var.value_get())
        self.imagic_proxy(lambda x=x: var.__imul__(x),
                          'var := var * %s' % x, var.value_get() * x)
        var(2)

        self.magic_proxy(lambda x=x: var.__truediv__(x),
                         'var / %s' % x, var.value_get() / x)
        self.magic_proxy(lambda x=x: var.__rtruediv__(x),
                         '%s / var' % x, x / var.value_get())
        self.imagic_proxy(lambda x=x: var.__itruediv__(x),
                          'var := var / %s' % x, var.value_get() / x)
        var(2)

        self.magic_proxy(lambda x=x: var.__floordiv__(x),
                         'var / %s' % x, var.value_get() // x)
        self.magic_proxy(lambda x=x: var.__rfloordiv__(x),
                         '%s / var' % x, x // var.value_get())
        # self.imagic_proxy(lambda x=x: var.__ifloordiv__(x),
        #                   'var := var / %s' % x, var.value_get() // x)
        var(2)

        self.magic_proxy(lambda x=x: var.__mod__(x),
                         'var mod %s' % x, var.value_get() % x)

        self.magic_proxy(lambda x=x: var.__rmod__(x),
                         '%s mod var' % x, x % var.value_get())

        self.imagic_proxy(lambda x=x: var.__imod__(x),
                          'var := var mod %s' % x, var.value_get() % x)
        var(2)

        self.magic_proxy(lambda x=x: var.__pow__(x),
                         'pow(var, %s)' % x, var.value_get() ** x)

        self.magic_proxy(lambda x=x: var.__rpow__(x),
                         'pow(%s, var)' % x, x ** var.value_get())

        self.imagic_proxy(lambda x=x: var.__ipow__(x),
                          'var := pow(var, %s)' % x, var.value_get() ** x)
        var(2)

        self.magic_proxy(lambda x=x: var.__lshift__(x),
                         'sh_left(var, %s)' % x, var.value_get() << x)

        self.magic_proxy(lambda x=x: var.__rlshift__(x),
                         'sh_left(%s, var)' % x, x << var.value_get())

        self.imagic_proxy(lambda x=x: var.__ilshift__(x),
                          'var := sh_left(var, %s)' % x, var.value_get() << x)
        var(2)

        self.magic_proxy(lambda x=x: var.__rshift__(x),
                         'sh_right(var, %s)' % x, var.value_get() >> x)

        self.magic_proxy(lambda x=x: var.__rrshift__(x),
                         'sh_right(%s, var)' % x, x >> var.value_get())

        self.imagic_proxy(lambda x=x: var.__irshift__(x),
                          'var := sh_right(var, %s)' % x, var.value_get() >> x)
        var(2)

        self.magic_proxy(lambda x=x: var.__and__(x),
                         'var .and. %s' % x, var.value_get() & x)

        self.magic_proxy(lambda x=x: var.__rand__(x),
                         '%s .and. var' % x, x & var.value_get())

        self.imagic_proxy(lambda x=x: var.__iand__(x),
                          'var := var .and. %s' % x, var.value_get() & x)
        var(2)

        self.magic_proxy(lambda x=x: var.__or__(x),
                         'var .or. %s' % x, var.value_get() | x)
        self.magic_proxy(lambda x=x: var.__ror__(x),
                         '%s .or. var' % x, x | var.value_get())
        self.imagic_proxy(lambda x=x: var.__ior__(x),
                          'var := var .or. %s' % x, var.value_get() | x)
        var(2)

        self.magic_proxy(lambda x=x: var.__eq__(x),
                         'var = %s' % x, var.value_get() == x)

        self.magic_proxy(lambda x=x: var.__ne__(x),
                         'var # %s' % x, var.value_get() != x)
        self.magic_proxy(lambda x=x: var.__lt__(x),
                         'var < %s' % x, var.value_get() < x)
        self.magic_proxy(lambda x=x: var.__gt__(x),
                         'var > %s' % x, var.value_get() > x)
        self.magic_proxy(lambda x=x: var.__le__(x),
                         'var <= %s' % x, var.value_get() <= x)
        self.magic_proxy(lambda x=x: var.__ge__(x),
                         'var >= %s' % x, var.value_get() >= x)

    def magic_proxy(self, operator, string, val):
        KSP.toggle_test_state(True)
        self.assertEqual(operator(), val)
        KSP.toggle_test_state(False)
        self.assertEqual(operator()(), string)
        return True

    def imagic_proxy(self, operator, string, val):
        KSP.toggle_test_state(True)
        # print(operator().value)
        self.assertEqual(operator().value_get(), val)

        KSP.toggle_test_state(False)
        code = list()
        IOutput.set(code)
        operator()
        self.assertEqual(code[0], string)
        IOutput.release()
        return True


if __name__ == '__main__':
    t.main()
