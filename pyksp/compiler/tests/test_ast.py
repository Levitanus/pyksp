import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)

from pyksp_ast import *


class TestAst(t.TestCase):

    def test_unary(self):
        args_tupple = [3, 4]
        a = -AstAdd(*args_tupple)
        self.assertEqual(a(), '-(%s + %s)' %
                         (args_tupple[0], args_tupple[1]))

        a = ~AstAdd(*args_tupple)
        self.assertEqual(a(), '.not.(%s + %s)' %
                         (args_tupple[0], args_tupple[1]))

    def test_i_op(self):
        args_tupple = [3, 4]
        addit = 1
        a = AstAdd(*args_tupple)
        a += addit
        self.assertEqual(a(), '%s + %s + %s + %s + %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstSub(*args_tupple)
        a -= addit
        self.assertEqual(a(), '%s - %s - %s - %s - %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstMul(*args_tupple)
        a *= addit
        self.assertEqual(a(), '%s * %s * %s * %s * %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstDiv(*args_tupple)
        a /= addit
        self.assertEqual(a(), '%s / %s / %s / %s / %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstDiv(*args_tupple)
        a //= addit
        self.assertEqual(a(), '%s / %s / %s / %s / %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstMod(*args_tupple)
        a %= addit
        self.assertEqual(a(), '%s mod %s mod %s mod %s mod %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstPow(*args_tupple)
        a **= addit
        self.assertEqual(a(), 'pow(pow(pow(%s, %s), pow(%s, %s)), %s)' %
                         (*args_tupple, *args_tupple, addit))

        a = AstLshift(*args_tupple)
        a <<= addit
        self.assertEqual(a(),
                         'sh_left(sh_left(sh_left(%s, %s), sh_left(%s, %s)), %s)'
                         % (*args_tupple, *args_tupple, addit))

        a = AstRshift(*args_tupple)
        a >>= addit
        self.assertEqual(a(),
                         'sh_right(sh_right(sh_right(%s, %s), sh_right(%s, %s)), %s)'
                         % (*args_tupple, *args_tupple, addit))

        a = AstAnd(*args_tupple)
        a &= addit
        self.assertEqual(a(), '%s .and. %s .and. %s .and. %s .and. %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstOr(*args_tupple)
        a |= addit
        self.assertEqual(a(), '%s .or. %s .or. %s .or. %s .or. %s' %
                         (*args_tupple, *args_tupple, addit))

    def test_di_op(self):
        args_tupple = [3, 4]
        addit = 1
        a = AstAdd(*args_tupple)
        a = a + a + addit
        self.assertEqual(a(), '%s + %s + %s + %s + %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstSub(*args_tupple)
        a = a - a - addit
        self.assertEqual(a(), '%s - %s - %s - %s - %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstMul(*args_tupple)
        a = a * a * addit
        self.assertEqual(a(), '%s * %s * %s * %s * %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstDiv(*args_tupple)
        a = a / a / addit
        self.assertEqual(a(), '%s / %s / %s / %s / %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstDiv(*args_tupple)
        a = a // a // addit
        self.assertEqual(a(), '%s / %s / %s / %s / %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstMod(*args_tupple)
        a = a % a % addit
        self.assertEqual(a(), '%s mod %s mod %s mod %s mod %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstPow(*args_tupple)
        a = a ** a ** addit
        self.assertEqual(a(), 'pow(pow(%s, %s), pow(%s, %s))' %
                         (*args_tupple, *args_tupple))

        a = AstLshift(*args_tupple)
        a = a << a << addit
        self.assertEqual(a(),
                         'sh_left(sh_left(sh_left(%s, %s), sh_left(%s, %s)), %s)'
                         % (*args_tupple, *args_tupple, addit))

        a = AstRshift(*args_tupple)
        a = a >> a >> addit
        self.assertEqual(a(),
                         'sh_right(sh_right(sh_right(%s, %s), sh_right(%s, %s)), %s)'
                         % (*args_tupple, *args_tupple, addit))

        a = AstAnd(*args_tupple)
        a = a & a & addit
        self.assertEqual(a(), '%s .and. %s .and. %s .and. %s .and. %s' %
                         (*args_tupple, *args_tupple, addit))

        a = AstOr(*args_tupple)
        a = a | a | addit
        self.assertEqual(a(), '%s .or. %s .or. %s .or. %s .or. %s' %
                         (*args_tupple, *args_tupple, addit))

    def test_cmp(self):
        args_tupple = ['1', '2']
        a = AstEq(*args_tupple)
        self.assertEqual(a(), '%s = %s' % (args_tupple[0], args_tupple[1]))

        a = AstNe(*args_tupple)
        self.assertEqual(a(), '%s # %s' % (args_tupple[0], args_tupple[1]))

        a = AstLt(*args_tupple)
        self.assertEqual(a(), '%s < %s' % (args_tupple[0], args_tupple[1]))

        a = AstGt(*args_tupple)
        self.assertEqual(a(), '%s > %s' % (args_tupple[0], args_tupple[1]))

        a = AstLe(*args_tupple)
        self.assertEqual(a(), '%s <= %s' % (args_tupple[0], args_tupple[1]))

        a = AstGe(*args_tupple)
        self.assertEqual(a(), '%s >= %s' % (args_tupple[0], args_tupple[1]))


if __name__ == '__main__':
    t.main()
