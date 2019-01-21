import unittest as ut

from .. import abstract as ab
from .. import base_types as bt


class TestBase(ut.TestCase):
    def tearDown(self) -> None:
        ab.KSP.refresh()
        ab.NameVar.refresh()
        bt.KspVar.refresh()


class TestService(ut.TestCase):

    def test_get_value(self) -> None:
        pass


class TestBasics(TestBase):

    def test_AstConcatStrings(self) -> None:
        a = bt.AstConcatString('first', 'second')
        self.assertEqual(a.get_value(), 'firstsecond')
        self.assertEqual(a.expand(), '"first" & "second"')
        with self.assertRaises(RuntimeError):
            a += 'third'
        with self.assertRaises(TypeError):
            a + 2
        with self.assertRaises(TypeError):
            2 + a
        b = a + 'third'
        self.assertIsInstance(b, bt.AstConcatString)
        self.assertEqual(b.get_value(), 'firstsecondthird')
        self.assertEqual(b.expand(), '"first" & "second" & "third"')
        c = 'zeroth' + a
        self.assertIsInstance(c, bt.AstConcatString)
        self.assertEqual(c.get_value(), 'zerothfirstsecond')
        self.assertEqual(c.expand(), '"zeroth" & "first" & "second"')

    def test_Str(self) -> None:
        out = ab.KSP.new_out()
        with self.assertRaises(TypeError):
            bt.Str(2)
        s = bt.Str('s_val', name='s')
        # self.assertEqual(s.val, 's_val')
        self.assertEqual(s.name(), '@s')
        s <<= 'string'
        self.assertEqual(s.val, 'string')
        self.assertEqual(s.name(), '@s')
        self.assertEqual(out.get_str(), '@s := "string"')
        s <<= bt.Str(name='ns', local=True)
        self.assertEqual(s.val, '')
        self.assertEqual(s.name(), '@s')
        self.assertEqual(out.get()[-1].line, '@s := @ns')
        n = bt.Num(2, name='n', local=True)
        s <<= n
        self.assertEqual(s.val, '2')
        self.assertEqual(out.get()[-1].line, '@s := $n')
        s += n
        self.assertEqual(s.val, '22')
        self.assertEqual(s.name(), '@s')
        self.assertEqual(out.get()[-1].line, '@s := @s & $n')
        with self.assertRaises(TypeError):
            s <<= 2
        with self.assertRaises(TypeError):
            s + 2
        s <<= '1' + s
        self.assertEqual(s.val, '122')
        self.assertEqual(out.get()[-1].line, '@s := "1" & @s')
        self.assertEqual(s.get_decl_line(), ['declare @s',
                                             '@s := "s_val"'])
        ab.KSP.refresh()


class TestInts(TestBase):

    def setUp(self):
        self.out = ab.KSP.new_out()
        self.n = bt.Num(0, name='n')

    def test_type_errors(self) -> None:
        n = self.n
        self.assertEqual(n.name(), '$n')
        self.assertEqual(n.val, 0)
        with self.assertRaises(TypeError):
            n <<= '2'
        with self.assertRaises(TypeError):
            n + '2'
        with self.assertRaises(TypeError):
            n - '2'
        with self.assertRaises(TypeError):
            n * 2.0
        with self.assertRaises(TypeError):
            n / 0.0
        with self.assertRaises(TypeError):
            n // 0
        with self.assertRaises(TypeError):
            n ** 0
        with self.assertRaises(TypeError):
            '2' + n
        with self.assertRaises(TypeError):
            '2' - n
        with self.assertRaises(TypeError):
            2.0 * n
        with self.assertRaises(TypeError):
            0.0 / n
        with self.assertRaises(TypeError):
            0 // n
        with self.assertRaises(TypeError):
            0 ** n
        with self.assertRaises(TypeError):
            n **= 2
        with self.assertRaises(NotImplementedError):
            n &= 2
        with self.assertRaises(NotImplementedError):
            n |= 2
        with self.assertRaises(TypeError):
            bt.to_int(n)

    def test_var(self) -> None:
        n = self.n
        out = self.out
        n <<= 1
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, '$n := 1')
        self.assertIsInstance(bt.to_float(n), bt.AstFloat)
        self.assertEqual(bt.to_float(n), 1.0)
        self.assertEqual(bt.to_float(n).expand(), 'int_to_real($n)')
        with self.assertRaises(TypeError):
            n <<= n.to_float()

    def test_magic(self) -> None:
        n = self.n
        out = self.out
        n <<= 1
        n += n
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, '$n := $n + $n')
        n -= n
        self.assertEqual(n.val, 0)
        self.assertEqual(out.get()[-1].line, '$n := $n - $n')
        n += n + 2
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, '$n := $n + ($n + 2)')
        n += n - 3
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, '$n := $n + ($n - 3)')
        n -= n - 2
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, '$n := $n - ($n - 2)')
        n -= n + 1
        self.assertEqual(n.val, -1)
        self.assertEqual(out.get()[-1].line, '$n := $n - ($n + 1)')
        n -= n
        self.assertEqual(n.val, 0)
        self.assertEqual(out.get()[-1].line, '$n := $n - $n')
        n <<= 2

        n *= n + 2
        self.assertEqual(n.val, 8)
        self.assertEqual(out.get()[-1].line, '$n := $n * ($n + 2)')
        n *= n
        self.assertEqual(n.val, 64)
        self.assertEqual(out.get()[-1].line, '$n := $n * $n')

        n /= n / 8
        self.assertEqual(n.val, 8)
        self.assertEqual(out.get()[-1].line, '$n := $n / ($n / 8)')
        n /= n
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, '$n := $n / $n')
        n /= 0
        self.assertEqual(n.val, 0)
        self.assertEqual(out.get()[-1].line, '$n := $n / 0')
        n <<= 3
        n /= 2
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, '$n := $n / 2')

        n <<= 3
        n %= 2
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, '$n := $n mod 2')
        n %= 2 + n
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, '$n := $n mod (2 + $n)')

        n <<= 3
        self.assertEqual(bt.get_value(n << 2), 12)
        self.assertEqual(bt.get_compiled(n << 2), 'sh_left($n, 2)')
        self.assertEqual(bt.get_value(n >> 2), 0)
        self.assertEqual(bt.get_compiled(n >> 2), 'sh_right($n, 2)')
        self.assertEqual(bt.get_value(2 << n), 16)
        self.assertEqual(bt.get_compiled(2 << n), 'sh_left(2, $n)')
        self.assertEqual(bt.get_value(2 >> n), 0)
        self.assertEqual(bt.get_compiled(2 >> n), 'sh_right(2, $n)')

    def test_comarisson(self) -> None:
        n = self.n
        n <<= 3
        with self.assertRaises(NotImplementedError):
            bt.get_value(n == 3)

        self.assertTrue(n & 2)
        self.assertFalse(n & (n == 2))
        self.assertEqual((n & 3).get_value(), 3)
        self.assertEqual((n & 3).expand_bool(), '$n and 3')
        self.assertEqual((n & 3).expand(), '$n .and. 3')
        self.assertEqual((3 & n).get_value(), 3)
        self.assertEqual((3 & n).expand_bool(), '3 and $n')

        self.assertTrue(n | 2)
        self.assertFalse((n != 3) | (n == 2))
        self.assertEqual((n | 3).get_value(), 3)
        self.assertEqual(((n != 3) | (n == 2)).expand_bool(),
                         '$n # 3 or $n = 2')
        self.assertEqual(((n != 3) | (n == 2) & (n != 4)).expand_bool(),
                         '$n # 3 or $n = 2 and $n # 4')
        self.assertEqual((n | 3).expand_bool(), '$n or 3')
        self.assertEqual((n | 3).expand(), '$n .or. 3')
        self.assertEqual((3 | n).expand_bool(), '3 or $n')
        self.assertEqual((3 | n).expand(), '3 .or. $n')

        self.assertTrue(n == 3)
        self.assertFalse(n == 2)
        self.assertEqual(bt.get_compiled(n == 3), '$n = 3')

        self.assertTrue(n != 2)
        self.assertFalse(n != 3)
        self.assertEqual(bt.get_compiled(n != 3), '$n # 3')

        self.assertTrue(n > 2)
        self.assertFalse(n > 3)
        self.assertEqual(bt.get_compiled(n > 3), '$n > 3')

        self.assertTrue(n < 4)
        self.assertFalse(n < 2)
        self.assertEqual(bt.get_compiled(n < 3), '$n < 3')

        self.assertTrue(n < 4)
        self.assertFalse(n < 2)
        self.assertEqual(bt.get_compiled(n < 3), '$n < 3')

        self.assertTrue(n <= 3)
        self.assertTrue(n <= 4)
        self.assertFalse(n <= 2)
        self.assertEqual(bt.get_compiled(n <= 3), '$n <= 3')

        self.assertTrue(n >= 3)
        self.assertTrue(n >= 2)
        self.assertFalse(n >= 4)
        self.assertEqual(bt.get_compiled(n >= 3), '$n >= 3')

        n <<= -3
        self.assertEqual(bt.get_value(abs(n)), 3)
        self.assertEqual(bt.get_compiled(abs(n)), 'abs($n)')
        self.assertEqual(bt.get_value(abs(n - 1)), 4)
        self.assertEqual(bt.get_compiled(abs(n - 1)), 'abs($n - 1)')
