import unittest as t

ismain: bool = False
if __name__ == '__main__':
    __name__ = 'pyksp.compiler.tests.test_base_types'
    ismain = True

from .mytests import DevTest

from ..base_types import *


class NumericWarn:
    pass


class SimpleAst(AstBase):

    def expand(self):
        return 'SimpleAst_expanded'

    def get_value(self):
        return 1


class GoodKspVar(KspVar):

    def __init__(self, name, is_local=False, value=None,
                 name_prefix='', name_postfix=''):
        if is_local is True:
            has_init = False
        else:
            has_init = True
        super().__init__(name, is_local=is_local,
                         has_init=has_init, value=value,
                         ref_type=(KspVar, int, str, float, AstBase),
                         name_prefix=name_prefix,
                         name_postfix=name_postfix)
        # self._compiled = 'compiled'
        self._runtime = value

    def _get_compiled(self):
        super()._get_compiled()
        return self.name()

    def _get_runtime(self):
        super()._get_runtime()
        return self._runtime

    def _set_runtime(self, val):
        super()._set_runtime(val)
        self._runtime = val

    @property
    def val(self):
        if self.is_compiled():
            return self._get_compiled()
        return self._get_runtime()

    def _generate_executable(self):
        super()._generate_executable()
        return

    def _generate_init(self):
        super()._generate_init()
        return [f'GoodKspVar ({self.name()}) init']


class ValuebleKspVar(GoodKspVar):

    def _set_runtime(self, val):
        self._value = val

    def _get_runtime(self):
        return self._value


class TestAstBase(DevTest):

    class AstChildBad(AstBase):
        pass

    class AstChild(AstBase):

        def expand(self):
            return 'exanded'

        def get_value(self):
            return 123

    def runTest(self):
        with self.assertRaises(TypeError):
            self.AstChildBad()
        x = self.AstChild()
        self.assertEqual(x.expand(), 'exanded')
        self.assertEqual(x.get_value(), 123)


class TestAstAssign(DevTest):

    class TestAst(AstBase):

        def expand(self):
            return 'TestAstExpanded'

        def get_value(self):
            return 1

    class TestKspVar(KspVar):

        def __init__(self, name):
            super().__init__(name)

        def null(self):
            pass

        _get_compiled = null
        _get_runtime = null
        _set_runtime = null
        _generate_executable = null
        _generate_init = null

        @property
        def val(self):
            return self.name()

    def test_AstBase(self):
        x = self.TestKspVar('x')
        y = self.TestAst()

        a = AstAssign(x, 'y_string')
        self.assertEqual(a.expand(), 'x := y_string')

        a = AstAssign(x, y)
        self.assertEqual(a.expand(), 'x := TestAstExpanded')

        a = AstAssign(x, x)
        self.assertEqual(a.expand(), 'x := x')

        with self.assertRaises(TypeError):
            AstAssign(1, x)

    def test_AstAddString(self):
        x = self.TestKspVar('x')
        y = self.TestAst()

        a = AstAddString(x, y)
        self.assertEqual(a.expand(), 'x & TestAstExpanded')

        a = AstAddString(x, 'string')
        self.assertEqual(a.expand(), 'x & "string"')

        a = AstAddString('string', y)
        self.assertEqual(a.expand(), '"string" & TestAstExpanded')

        def called():
            return y

        a = AstAddString('string', called)
        self.assertEqual(a.expand(), '"string" & TestAstExpanded')
        self.assertEqual((a + '1').expand(),
                         '"string" & TestAstExpanded & "1"')
        self.assertEqual((a + a).expand(),
                         '"string" & TestAstExpanded & ' +
                         '"string" & TestAstExpanded')


class TestAstOperator(DevTest):

    class Operator(AstOperator):
        priority = 4

        def __init__(self, arg=1):
            super().__init__(arg)

        def expand(self):
            return 'expanded'

        def get_value(self):
            return super().get_value(lambda arg: arg)

    def setUp(self):
        super().setUp()
        self.op = self.Operator(1)

    def test_unpack(self):
        args = [1]
        self.assertEqual(
            self.op.unpack_args(*args),
            1)
        args = [1, SimpleAst()]
        self.assertEqual(
            self.op.unpack_args(*args),
            [1, 'SimpleAst_expanded'])

        args = [1, ValuebleKspVar('x', is_local=True, value=3)]
        self.assertEqual(
            self.op.unpack_args(*args),
            [1, 3])
        SimpleAst().set_compiled(True)
        args = [1, ValuebleKspVar('x', is_local=True, value=3)]
        self.assertEqual(
            self.op.unpack_args(*args),
            [1, 'x'])

    def test_get_value(self):
        self.assertEqual(self.op.get_value(), 1)
        x = AstAdd(GoodKspVar('x', is_local=True, value=2), self.op)
        self.assertEqual(x.get_value(), 3)

    def test_methods(self):
        self.assertEqual(self.op.unary('+', 1), '+1')
        self.assertEqual(self.op.unary('+', 'e'), '+e')

        self.assertEqual(self.op.bracket_unary('+', 1), '+(1)')
        self.assertEqual(self.op.bracket_unary('+', 'e'), '+(e)')

        # self.assertEqual(self.op.standart('+', 1, 2), '1 + 2')
        # self.assertEqual(self.op.standart('+', 1, 'e'), '1 + e')

        self.assertEqual(self.op.bracket_double('+', 1, 2), '+(1, 2)')
        self.assertEqual(self.op.bracket_double('+', 1, 'e'),
                         '+(1, e)')

    def test_magic(self):
        with self.assertRaises(ArithmeticError):
            self.op // 1

        with self.assertRaises(ArithmeticError):
            1 // self.op

        with self.assertRaises(NotImplementedError):
            self.op //= 1

        self.assertEqual((-self.op).expand(), '-expanded')
        self.assertEqual((-self.op).get_value(), -1)
        self.assertEqual((~self.op).expand(), '.not.expanded')
        self.assertEqual((~self.op).get_value(), ~1)

        self.assertEqual((self.op + 1).expand(), 'expanded + 1')
        self.assertEqual((self.op + 1 + 1 + 1).expand(),
                         'expanded + 1 + 1 + 1')
        self.assertEqual((1 + self.op).expand(), '1 + (expanded)')
        self.assertEqual((1 + self.op).get_value(), 1 + 1)
        with self.assertRaises(NotImplementedError):
            self.op += 1

        self.assertEqual((self.op - 1).expand(), 'expanded - 1')
        self.assertEqual((1 - self.op).expand(), '1 - (expanded)')
        self.assertEqual((1 - self.op).get_value(), 1 - 1)
        with self.assertRaises(NotImplementedError):
            self.op -= 1

        self.assertEqual((self.op * 1).expand(), '(expanded) * 1')
        self.assertEqual((1 * self.op).expand(), '1 * (expanded)')
        self.assertEqual((1 * self.op).get_value(), 1 * 1)
        with self.assertRaises(NotImplementedError):
            self.op *= 1

        self.assertEqual((self.op / 1).expand(), '(expanded) / 1')
        self.assertEqual((1 / self.op).expand(), '1 / (expanded)')
        self.assertEqual((1 / self.op).get_value(), 1 / 1)
        with self.assertRaises(NotImplementedError):
            self.op /= 1

        self.assertEqual((self.op % 1).expand(), '(expanded) mod 1')
        self.assertEqual((1 % self.op).expand(), '1 mod (expanded)')
        self.assertEqual((4 % self.op).get_value(), 4 % 1)
        with self.assertRaises(NotImplementedError):
            self.op %= 1

        self.assertEqual((self.op ** 1).expand(), 'pow(expanded, 1)')
        self.assertEqual((1 ** self.op).expand(), 'pow(1, expanded)')
        self.assertEqual((4 ** self.op).get_value(), 4 ** 1)
        with self.assertRaises(NotImplementedError):
            self.op **= 1

        self.assertEqual((self.op == 1).expand(), 'expanded = 1')
        self.assertEqual((1 == self.op).expand(), 'expanded = 1')

        self.assertEqual((self.op != 1).expand(), 'expanded # 1')
        self.assertEqual((1 != self.op).expand(), 'expanded # 1')

        self.assertEqual((self.op < 1).expand(), 'expanded < 1')
        self.assertEqual((self.op > 1).expand(), 'expanded > 1')
        self.assertEqual((1 < self.op).expand(), 'expanded > 1')
        self.assertEqual((1 > self.op).expand(), 'expanded < 1')

        self.assertEqual((self.op <= 1).expand(), 'expanded <= 1')
        self.assertEqual((self.op >= 1).expand(), 'expanded >= 1')
        self.assertEqual((1 <= self.op).expand(), 'expanded >= 1')
        self.assertEqual((1 >= self.op).expand(), 'expanded <= 1')

        KSP.set_bool(False)
        self.assertEqual((1 | self.op).expand(), '1 .or. expanded')
        self.assertEqual((self.op | 1).expand(), 'expanded .or. 1')
        KSP.set_bool(True)
        self.assertEqual((1 | self.op).expand(), '1 or expanded')
        self.assertEqual((self.op | 1).expand(), 'expanded or 1')

        KSP.set_bool(False)
        self.assertEqual((1 & self.op).expand(), '1 .and. expanded')
        self.assertEqual((self.op & 1).expand(), 'expanded .and. 1')
        KSP.set_bool(True)
        self.assertEqual((1 & self.op).expand(), '1 and expanded')
        self.assertEqual((self.op & 1).expand(), 'expanded and 1')

# I don't know why they don't have self._get_runtime_other
# kInt, kReal have


# @t.skip
class TestKspVar(DevTest):

    class BadKspVar(KspVar):
        pass

    def test_bad(self):
        with self.assertRaises(TypeError) as e:
            self.BadKspVar()

        self.assertEqual(
            str(e.exception),
            "Can't instantiate abstract class" +
            " BadKspVar with abstract methods _generate_executable" +
            ", _generate_init, _get_compiled, _get_runtime" +
            ", _set_runtime")

    def test_good(self):
        x = GoodKspVar('x')
        x <<= 2
        self.assertEqual(x.val, 2)
        y = int()
        y <<= x
        self.assertEqual(y, 2)
        y = x.val
        self.assertEqual(y, 2)
        x <<= 3
        self.assertEqual(x.val, 3)
        KSP.set_compiled(True)
        self.assertEqual(x.val, 'x')
        x <<= 'compiled_2'
        self.assertEqual(Output().get()[-1],
                         'x := compiled_2')
        self.assertEqual(x.val, 'x')

        with self.assertRaises(TypeError):
            x <<= AstAssign('a', 'a')

        x <<= 1
        self.assertEqual(Output().get()[-1],
                         'x := 1')
        x <<= AstAddString('a', 'a')
        self.assertEqual(Output().get()[-1],
                         'x := "a" & "a"')

        self.assertEqual(x._generate_init(),
                         ['GoodKspVar (x) init'])

        self.assertEqual(x.generate_all_inits(),
                         ['GoodKspVar (x) init'])
        self.assertEqual(x.generate_all_executables(), [])
        y = GoodKspVar('y', is_local=True)
        self.assertEqual(y.generate_all_inits(),
                         ['GoodKspVar (x) init'])

        KSP.set_compiled(False)
        z = ValuebleKspVar('z', value=3)
        self.assertEqual(z.val, 3)

    class GoodStrVar(GoodKspVar, KspStrVar):
        pass

    def test_str_var(self):
        x = self.GoodStrVar('x')
        x <<= 'mystring'
        self.assertEqual(x.val, 'mystring')
        self.assertEqual(x + '_1', 'mystring_1')
        self.assertEqual('_1' + x, 'mystring_1')
        x += '_1'
        self.assertEqual(x.val, 'mystring_1')

        KSP.set_compiled(True)
        out = Output().get
        x <<= 'mystring'
        self.assertEqual(out()[-1], 'x := "mystring"')
        self.assertEqual((x + 'string').expand(),
                         'x & "string"')
        self.assertEqual(('string' + x).expand(),
                         '"string" & x')
        x += 'string'
        self.assertEqual(out()[-1],
                         'x := x & "string"')

    class BadNumericNot(KspNumeric, GoodKspVar):
        pass

    class BadNumericNotTuple(KspNumeric, GoodKspVar):
        warning_types = KSP

    class BadNumericNotType(KspNumeric, GoodKspVar):
        warning_types = (str, 4)

    class GoodNumeric(KspNumeric, GoodKspVar):
        warning_types = (NumericWarn,)

        def __truediv__(self, other):
            pass

        def __rtruediv__(self, other):
            pass

        def __itruediv__(self, other):
            pass

        def __floordiv__(self, other):
            raise ArithmeticError('use regular / instead')

        def __rfloordiv__(self, other):
            raise ArithmeticError('use regular / instead')

        def __ifloordiv__(self, other):
            raise ArithmeticError('use regular / instead')

    def test_numeric(self):
        with self.assertRaises(TypeError):
            self.BadNumericNot('x')
        with self.assertRaises(TypeError):
            self.BadNumericNotTuple('x')
        with self.assertRaises(TypeError):
            self.BadNumericNotType('x')

        self.assertTrue(self.GoodNumeric('w'))

    class TestIntVar(KspIntVar, GoodKspVar):
        warning_types = (float,)

    def test_int(self):
        x = self.TestIntVar('x')

        with self.assertRaises(ArithmeticError):
            x // 1
        with self.assertRaises(ArithmeticError):
            1 // x
        with self.assertRaises(ArithmeticError):
            x //= 1

        x.set_compiled(False)
        x <<= 1
        self.assertEqual(x + 1, 2)
        self.assertEqual(1 + x, 2)
        x += 1
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x + 1.2
        with self.assertRaises(x.TypeWarn):
            1.2 + x
        with self.assertRaises(x.TypeWarn):
            x += 1.2
        x.set_compiled(True)
        self.assertEqual((x + 1).expand(), 'x + 1')
        self.assertEqual((x + 1).get_value(), 3)
        self.assertEqual((1 + x).expand(), '1 + x')
        x += 1
        self.assertEqual(x.val, 'x')
        self.assertEqual(x._get_runtime(), 3)
        self.assertEqual(
            Output().get()[-1],
            'x := x + 1')

        x.set_compiled(False)
        x <<= 3
        self.assertEqual(x - 1, 2)
        self.assertEqual(1 - x, 2)
        x -= 1
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x - 1.2
        with self.assertRaises(x.TypeWarn):
            1.2 - x
        with self.assertRaises(x.TypeWarn):
            x -= 1.2
        x.set_compiled(True)
        self.assertEqual((x - 1).get_value(), 1)
        self.assertEqual((x - 1).expand(), 'x - 1')
        self.assertEqual((1 - x).expand(), '1 - x')
        x -= 1
        self.assertEqual(x.val, 'x')
        self.assertEqual(x._get_runtime(), 1)
        self.assertEqual(
            Output().get()[-1],
            'x := x - 1')

        x.set_compiled(False)
        x <<= 1
        self.assertEqual(x * 2, 2)
        self.assertEqual(2 * x, 2)
        x *= 2
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x * 2.2
        with self.assertRaises(x.TypeWarn):
            2.2 * x
        with self.assertRaises(x.TypeWarn):
            x *= 2.2
        x.set_compiled(True)
        self.assertEqual((x * 2).expand(), 'x * 2')
        self.assertEqual((2 * x).expand(), '2 * x')
        x *= 2
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x * 2')

        x.set_compiled(False)
        x <<= 4
        self.assertEqual(x / 2, 2)
        self.assertEqual(2 / x, 2)
        x /= 2
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x / 2.2
        with self.assertRaises(x.TypeWarn):
            2.2 / x
        with self.assertRaises(x.TypeWarn):
            x /= 2.2
        x.set_compiled(True)
        self.assertEqual((x / 2).expand(), 'x / 2')
        self.assertEqual((2 / x).expand(), '2 / x')
        x /= 2
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x / 2')

        x.set_compiled(False)
        x <<= 1
        self.assertEqual(x * 2, 2)
        self.assertEqual(2 * x, 2)
        x *= 2
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x * 2.2
        with self.assertRaises(x.TypeWarn):
            2.2 * x
        with self.assertRaises(x.TypeWarn):
            x *= 2.2
        x.set_compiled(True)
        self.assertEqual((x * 2).expand(), 'x * 2')
        self.assertEqual((2 * x).expand(), '2 * x')
        x *= 2
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x * 2')

        x.set_compiled(False)
        x <<= 1
        self.assertFalse(x == 2)
        self.assertTrue(x == 1)
        self.assertFalse(2 == x)
        self.assertTrue(1 == x)
        x.set_compiled(True)
        self.assertEqual((x == 2).expand(), 'x = 2')
        self.assertEqual((2 == x).expand(), 'x = 2')

        x.set_compiled(False)
        x <<= 1
        self.assertFalse(x != 1)
        self.assertTrue(x != 2)
        self.assertFalse(1 != x)
        self.assertTrue(2 != x)
        x.set_compiled(True)
        self.assertEqual((x != 2).expand(), 'x # 2')
        self.assertEqual((2 != x).expand(), 'x # 2')

        x.set_compiled(False)
        x <<= 1
        self.assertFalse(x < 1)
        self.assertTrue(x < 2)
        self.assertFalse(2 < x)
        self.assertTrue(0 < x)
        x.set_compiled(True)
        self.assertEqual((x < 2).expand(), 'x < 2')
        self.assertEqual((2 > x).expand(), 'x < 2')

        x.set_compiled(False)
        x <<= 1
        self.assertFalse(x > 2)
        self.assertTrue(x > 0)
        self.assertFalse(1 > x)
        self.assertTrue(2 > x)
        x.set_compiled(True)
        self.assertEqual((x > 2).expand(), 'x > 2')
        self.assertEqual((2 < x).expand(), 'x > 2')

        x.set_compiled(False)
        x <<= 1
        self.assertFalse(x <= 0)
        self.assertTrue(x <= 1)
        self.assertTrue(x <= 2)
        self.assertFalse(2 <= x)
        self.assertTrue(1 <= x)
        self.assertTrue(0 <= x)
        x.set_compiled(True)
        self.assertEqual((x <= 2).expand(), 'x <= 2')
        self.assertEqual((2 >= x).expand(), 'x <= 2')

        x.set_compiled(False)
        x <<= 1
        self.assertFalse(x >= 2)
        self.assertTrue(x >= 1)
        self.assertTrue(x >= 0)
        self.assertFalse(0 >= x)
        self.assertTrue(1 >= x)
        self.assertTrue(2 >= x)
        x.set_compiled(True)
        self.assertEqual((x >= 2).expand(), 'x >= 2')
        self.assertEqual((2 <= x).expand(), 'x >= 2')

        x.set_bool(False)
        x.set_compiled(False)
        x <<= 1
        self.assertEqual(x | 2, 3)
        self.assertEqual(2 | x, 3)
        with self.assertRaises(NotImplementedError):
            x |= 2
        x.set_compiled(True)
        self.assertEqual((x | 2).expand(), 'x .or. 2')
        self.assertEqual((2 | x).expand(), '2 .or. x')

        x.set_bool(True)
        x.set_compiled(False)
        x <<= 1
        self.assertEqual(x | 2, 1)
        self.assertEqual(2 | x, 1)
        with self.assertRaises(NotImplementedError):
            x |= 2
        x.set_compiled(True)
        self.assertEqual((x | 2).expand(), 'x or 2')
        self.assertEqual((2 | x).expand(), '2 or x')

        x.set_bool(False)
        x.set_compiled(False)
        x <<= 1
        self.assertEqual(x & 2, 0)
        self.assertEqual(2 & x, 0)
        with self.assertRaises(NotImplementedError):
            x &= 2
        x.set_compiled(True)
        self.assertEqual((x & 2).expand(), 'x .and. 2')
        self.assertEqual((2 & x).expand(), '2 .and. x')

        x.set_bool(True)
        x.set_compiled(False)
        x <<= 1
        self.assertEqual(x & 2, 2)
        self.assertEqual(2 & x, 2)
        with self.assertRaises(NotImplementedError):
            x &= 2
        x.set_compiled(True)
        self.assertEqual((x & 2).expand(), 'x and 2')
        self.assertEqual((2 & x).expand(), '2 and x')

    class TestRealVar(KspRealVar):
        warning_types = (int,)

        def __init__(self, name):
            super().__init__(name,
                             ref_type=(float, KspRealVar, AstOperator))

        def _generate_init(self):
            return []

        def _get_compiled(self):
            return self.name()

        def _get_runtime(self):
            return self._value

        def _set_runtime(self, val):
            self._value = val

    def test_real(self):
        x = self.TestRealVar('x')

        with self.assertRaises(ArithmeticError):
            x // 1
        with self.assertRaises(ArithmeticError):
            1 // x
        with self.assertRaises(ArithmeticError):
            x //= 1

        x.set_compiled(False)
        x <<= 1.0
        self.assertEqual(x + 1.0, 2)
        self.assertEqual(1.0 + x, 2)
        x += 1.0
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x + 1
        with self.assertRaises(x.TypeWarn):
            1 + x
        with self.assertRaises(x.TypeWarn):
            x += 1
        x.set_compiled(True)
        self.assertEqual((x + 1.0).expand(), 'x + 1.0')
        self.assertEqual((1.0 + x).expand(), '1.0 + x')
        x += 1.0
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x + 1.0')

        x.set_compiled(False)
        x <<= 3.0
        self.assertEqual(x - 1.0, 2)
        self.assertEqual(1.0 - x, 2)
        x -= 1.0
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x - 1
        with self.assertRaises(x.TypeWarn):
            1 - x
        with self.assertRaises(x.TypeWarn):
            x -= 1
        x.set_compiled(True)
        self.assertEqual((x - 1.0).expand(), 'x - 1.0')
        self.assertEqual((1.0 - x).expand(), '1.0 - x')
        x -= 1.0
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x - 1.0')

        x.set_compiled(False)
        x <<= 1.0
        self.assertEqual(x * 2.0, 2)
        self.assertEqual(2.0 * x, 2)
        x *= 2.0
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x * 2
        with self.assertRaises(x.TypeWarn):
            2 * x
        with self.assertRaises(x.TypeWarn):
            x *= 2
        x.set_compiled(True)
        self.assertEqual((x * 2.0).expand(), 'x * 2.0')
        self.assertEqual((2.0 * x).expand(), '2.0 * x')
        x *= 2.0
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x * 2.0')

        x.set_compiled(False)
        x <<= 4.0
        self.assertEqual(x / 2.0, 2)
        self.assertEqual(2.0 / x, 2)
        x /= 2.0
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x / 2
        with self.assertRaises(x.TypeWarn):
            2 / x
        with self.assertRaises(x.TypeWarn):
            x /= 2
        x.set_compiled(True)
        self.assertEqual((x / 2.0).expand(), 'x / 2.0')
        self.assertEqual((2.0 / x).expand(), '2.0 / x')
        x /= 2.0
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x / 2.0')

        x.set_compiled(False)
        x <<= 1.0
        self.assertEqual(x * 2.0, 2)
        self.assertEqual(2.0 * x, 2)
        x *= 2.0
        self.assertEqual(x.val, 2)
        with self.assertRaises(x.TypeWarn):
            x * 2
        with self.assertRaises(x.TypeWarn):
            2 * x
        with self.assertRaises(x.TypeWarn):
            x *= 2
        x.set_compiled(True)
        self.assertEqual((x * 2.0).expand(), 'x * 2.0')
        self.assertEqual((2.0 * x).expand(), '2.0 * x')
        x *= 2.0
        self.assertEqual(x.val, 'x')
        self.assertEqual(
            Output().get()[-1],
            'x := x * 2.0')

        x.set_compiled(False)
        x <<= 1.0
        self.assertFalse(x == 2.0)
        self.assertTrue(x == 1.0)
        self.assertFalse(2.0 == x)
        self.assertTrue(1.0 == x)
        x.set_compiled(True)
        self.assertEqual((x == 2).expand(), 'x = 2')
        self.assertEqual((2 == x).expand(), 'x = 2')

        x.set_compiled(False)
        x <<= 1.0
        self.assertFalse(x != 1.0)
        self.assertTrue(x != 2.0)
        self.assertFalse(1.0 != x)
        self.assertTrue(2.0 != x)
        x.set_compiled(True)
        self.assertEqual((x != 2).expand(), 'x # 2')
        self.assertEqual((2 != x).expand(), 'x # 2')

        x.set_compiled(False)
        x <<= 1.0
        self.assertFalse(x < 1.0)
        self.assertTrue(x < 2.0)
        self.assertFalse(2.0 < x)
        self.assertTrue(0.0 < x)
        x.set_compiled(True)
        self.assertEqual((x < 2).expand(), 'x < 2')
        self.assertEqual((2 > x).expand(), 'x < 2')

        x.set_compiled(False)
        x <<= 1.0
        self.assertFalse(x > 2.0)
        self.assertTrue(x > 0.0)
        self.assertFalse(1.0 > x)
        self.assertTrue(2.0 > x)
        x.set_compiled(True)
        self.assertEqual((x > 2).expand(), 'x > 2')
        self.assertEqual((2 < x).expand(), 'x > 2')

        x.set_compiled(False)
        x <<= 1.0
        self.assertFalse(x <= 0.0)
        self.assertTrue(x <= 1.0)
        self.assertTrue(x <= 2.0)
        self.assertFalse(2.0 <= x)
        self.assertTrue(1.0 <= x)
        self.assertTrue(0.0 <= x)
        x.set_compiled(True)
        self.assertEqual((x <= 2).expand(), 'x <= 2')
        self.assertEqual((2 >= x).expand(), 'x <= 2')

        x.set_compiled(False)
        x <<= 1.0
        self.assertFalse(x >= 2.0)
        self.assertTrue(x >= 1.0)
        self.assertTrue(x >= 0.0)
        self.assertFalse(0.0 >= x)
        self.assertTrue(1.0 >= x)
        self.assertTrue(2.0 >= x)
        x.set_compiled(True)
        self.assertEqual((x >= 2).expand(), 'x >= 2')
        self.assertEqual((2 <= x).expand(), 'x >= 2')

        x.set_bool(False)
        x.set_compiled(False)
        x <<= 1.0
        with self.assertRaises(NotImplementedError):
            self.assertEqual(x | 2.0, 3)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(2.0 | x, 3)
        with self.assertRaises(NotImplementedError):
            x |= 2
        x.set_compiled(True)
        with self.assertRaises(NotImplementedError):
            self.assertEqual((x | 2).expand(), 'x .or. 2')
        with self.assertRaises(NotImplementedError):
            self.assertEqual((2 | x).expand(), '2 .or. x')

        x.set_bool(True)
        x.set_compiled(False)
        x <<= 1.0
        self.assertEqual(x | 2.0, 1)
        self.assertEqual(2.0 | x, 1)
        with self.assertRaises(NotImplementedError):
            x |= 2.0
        x.set_compiled(True)
        self.assertEqual((x | 2).expand(), 'x or 2')
        self.assertEqual((2 | x).expand(), '2 or x')

        x.set_bool(False)
        x.set_compiled(False)
        x <<= 1.0
        with self.assertRaises(NotImplementedError):
            self.assertEqual(x & 2, 0)
        with self.assertRaises(NotImplementedError):
            self.assertEqual(2 & x, 0)
        with self.assertRaises(NotImplementedError):
            x &= 2
        x.set_compiled(True)
        with self.assertRaises(NotImplementedError):
            self.assertEqual((x & 2).expand(), 'x .and. 2')
        with self.assertRaises(NotImplementedError):
            self.assertEqual((2 & x).expand(), '2 .and. x')

        x.set_bool(True)
        x.set_compiled(False)
        x <<= 1.0
        self.assertEqual(x & 2.0, 2)
        self.assertEqual(2.0 & x, 2)
        with self.assertRaises(NotImplementedError):
            x &= 2.0
        x.set_compiled(True)
        self.assertEqual((x & 2).expand(), 'x and 2')
        self.assertEqual((2 & x).expand(), '2 and x')


class TestKspArray(DevTest):
    class TestArr(KspArray):
        def __init__(self, name, seq=None, ref_type=(GoodKspVar, int),
                     is_local=False, item_type=GoodKspVar, size=None,
                     name_prefix=''):
            if is_local:
                has_init = False
            else:
                has_init = True
            super().__init__(name, seq=seq,
                             ref_type=ref_type,
                             name_prefix=name_prefix,
                             name_postfix='',
                             preserve_name=False,
                             has_init=has_init, is_local=is_local,
                             item_type=item_type,
                             size=size)
            self._compiled = self.name()

        def _get_compiled(self):
            super()._get_compiled()
            return self._compiled

        def _get_runtime(self):
            super()._get_runtime()
            return self._seq

        @property
        def val(self):
            if self.is_compiled():
                return self._get_compiled()
            return self._get_runtime()

        def _generate_executable(self):
            super()._generate_executable()
            return

    class TestIntVar(KspIntVar, GoodKspVar):
        warning_types = (float,)

        def _get_runtime(self):
            return self._value

    def test_item(self):
        x = self.TestArr(name='x', size=5, item_type=GoodKspVar,
                         seq=[1, 2, 3, 4, 5])
        self.assertEqual(x[4].val, 5)
        x[4] <<= 6
        self.assertEqual(x[4].val, 6)
        KSP.set_compiled(True)
        x[3] <<= 5
        self.assertEqual(Output().get()[-1], 'x[3] := 5')
        self.assertEqual(x[3]._get_runtime(), 5)
        y = GoodKspVar('y', value=3)
        x[3] <<= y
        self.assertEqual(Output().get()[-1], 'x[3] := y')
        self.assertEqual(x[3]._get_runtime(), 3)
        KSP.set_compiled(False)
        self.assertEqual(x[3].val, 3)

        z = self.TestArr(name='z', size=5, item_type=self.TestIntVar,
                         seq=[1, 2, 3, 4, 5])
        KSP.set_compiled(True)
        z[0] += 1
        self.assertEqual(z[0].val, 'z[0]')
        self.assertEqual(z[0]._get_runtime(), 2)
        idx = self.TestIntVar('idx_var', is_local=False, value=3,
                              name_prefix='$')
        self.assertEqual(z[idx]._get_runtime(), 4)
        self.assertEqual(z[idx].val, 'z[$idx_var]')

    def test_size(self):
        x = self.TestArr(name='x', size=5, item_type=GoodKspVar)
        x.append(2)
        self.assertEqual(x[0].val, 2)
        x[4] = 3
        self.assertEqual(x[4].val, 3)
        with self.assertRaises(IndexError):
            x[5] = 3
        with self.assertRaises(RuntimeError):
            x.append(3)
        self.assertEqual(KspObject.generate_all_inits(),
                         ['declare x[5]'])
        with self.assertRaises(AttributeError):
            self.TestArr(name='x', size=2, seq=[1, 2, 3],
                         is_local=True)
        seq = list(range(1000000))
        seq[1] = '1'
        big = self.TestArr('big', seq=seq)
        self.assertEqual(big[0].val, 0)
        self.assertEqual(big[3].val, 3)
        self.assertEqual(big[999999].val, 999999)
        self.assertEqual(big.val, seq)
        with self.assertRaises(TypeError):
            big[1:2]
        with self.assertRaises(TypeError):
            big[1]

    def test_generate_init(self):
        KSP.set_compiled(True)
        x = self.TestArr(name='x', size=5, item_type=GoodKspVar,
                         name_prefix='%')
        x.append(2)
        x[4] = 3
        self.assertEqual(x._generate_init(), ['declare %x[5]'])
        self.assertEqual(Output().get(), ['%x[0] := 2', '%x[4] := 3'])
        Output().refresh()

        seq = list(range(100))
        y = self.TestArr('y', seq=seq, item_type=KspNumeric)
        self.assertEqual(
            y._generate_init(),
            ['declare y[100] := (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,' +
             ' 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,' +
             ' 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,' +
             ' 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,' +
             ' 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62,' +
             ' 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75,' +
             ' 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88,' +
             ' 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99)'])

        seq = ['a', 'b', 'c']
        z = self.TestArr('z', seq=seq, item_type=KspStrVar)
        self.assertEqual(
            z._generate_init(), ['declare z[3]',
                                 'z[0] := "a"',
                                 'z[1] := "b"',
                                 'z[2] := "c"'])

    def test_iter(self):
        x = self.TestArr(name='x', seq=[1, 2, 3, 4, 5],
                         item_type=GoodKspVar,
                         name_prefix='%')
        with self.assertRaises(NotImplementedError):
            for item in x:
                print(item)
        out = list()
        for item in x.iter_runtime():
            out.append(item.val)
        self.assertEqual(out, [1, 2, 3, 4, 5])
        out = list()
        for item in x.iter_runtime_fast():
            out.append(item)
        self.assertEqual(out, [1, 2, 3, 4, 5])


if ismain:
    t.main()
