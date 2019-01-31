import unittest as ut

from .. import abstract as ab
from .. import base_types as bt


class TestBase(ut.TestCase):
    """My class docstring.

    with the second line"""

    def tearDown(self) -> None:
        ab.KSP.refresh()
        ab.NameVar.refresh()
        bt.VarBase.refresh()


class TestService(ut.TestCase):
    def test_get_value(self) -> None:
        pass


class TestBasics(TestBase):
    def test_AstConcatStrings(self) -> None:
        a = bt.AstConcatString("first", "second")
        self.assertEqual(a.get_value(), "firstsecond")
        self.assertEqual(a.expand(), '"first" & "second"')
        with self.assertRaises(RuntimeError):
            a += "third"
        with self.assertRaises(TypeError):
            a + 2  # type: ignore
        with self.assertRaises(TypeError):
            2 + a  # type: ignore
        b = a + "third"
        self.assertIsInstance(b, bt.AstConcatString)
        self.assertEqual(b.get_value(), "firstsecondthird")
        self.assertEqual(b.expand(), '"first" & "second" & "third"')
        c = "zeroth" + a
        self.assertIsInstance(c, bt.AstConcatString)
        self.assertEqual(c.get_value(), "zerothfirstsecond")
        self.assertEqual(c.expand(), '"zeroth" & "first" & "second"')

    def test_Str(self) -> None:
        # out = list()
        out = ab.KSP.new_out()
        with self.assertRaises(TypeError):
            bt.VarStr(2)  # type: ignore
        s = bt.VarStr("s_val", name="s")
        # self.assertEqual(s.val, 's_val')
        self.assertEqual(s.name(), "@s")
        s <<= "string"
        self.assertEqual(s.val, "string")
        self.assertEqual(s.name(), "@s")
        self.assertEqual(out.get_str(), '@s := "string"')
        s <<= bt.VarStr(name="ns", local=True)
        self.assertEqual(s.val, "")
        self.assertEqual(s.name(), "@s")
        self.assertEqual(out.get()[-1].line, "@s := @ns")
        n = bt.Var(2, name="n", local=True)
        s <<= n
        self.assertEqual(s.val, "2")
        self.assertEqual(out.get()[-1].line, "@s := $n")
        s += n
        self.assertEqual(s.val, "22")
        self.assertEqual(s.name(), "@s")
        self.assertEqual(out.get()[-1].line, "@s := @s & $n")
        with self.assertRaises(TypeError):
            s <<= 2  # type: ignore
        with self.assertRaises(TypeError):
            s + 2  # type: ignore
        s <<= "1" + s
        self.assertEqual(s.val, "122")
        self.assertEqual(out.get()[-1].line, '@s := "1" & @s')
        self.assertEqual(s.get_decl_line(), ["declare @s", '@s := "s_val"'])
        ab.KSP.refresh()


class TestInts(TestBase):
    def setUp(self) -> None:
        self.out = ab.KSP.new_out()
        self.n = bt.Var(0, name="n")

    def test_type_errors(self) -> None:
        n = self.n
        self.assertIsInstance(n, bt.Num)
        self.assertEqual(n.name(), "$n")
        self.assertEqual(n.val, 0)
        with self.assertRaises(TypeError):
            n <<= "2"  # type: ignore
        with self.assertRaises(TypeError):
            n + "2"  # type: ignore
        with self.assertRaises(TypeError):
            n - "2"  # type: ignore
        with self.assertRaises(TypeError):
            n * 2.0  # type: ignore
        with self.assertRaises(TypeError):
            n / 0.0  # type: ignore
        with self.assertRaises(TypeError):
            n // 0  # type: ignore
        with self.assertRaises(TypeError):
            n**0
        with self.assertRaises(TypeError):
            "2" + n  # type: ignore
        with self.assertRaises(TypeError):
            "2" - n  # type: ignore
        with self.assertRaises(TypeError):
            2.0 * n  # type: ignore
        with self.assertRaises(TypeError):
            0.0 / n  # type: ignore
        with self.assertRaises(TypeError):
            0 // n  # type: ignore
        with self.assertRaises(TypeError):
            0**n
        with self.assertRaises(TypeError):
            n **= 2  # type: ignore
        with self.assertRaises(NotImplementedError):
            n &= 2
        with self.assertRaises(NotImplementedError):
            n |= 2
        with self.assertRaises(AttributeError):
            bt.to_int(n)

    def test_var(self) -> None:
        n = self.n
        out = self.out
        n <<= 1
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "$n := 1")
        self.assertIsInstance(bt.to_float(n), bt.AstFloat)
        self.assertEqual(bt.to_float(n), 1.0)
        self.assertEqual(bt.to_float(n).expand(), "int_to_real($n)")
        with self.assertRaises(TypeError):
            n <<= n.to_float()  # type: ignore
        bt.inc(n)
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, "inc($n)")
        bt.dec(n)
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "dec($n)")
        n.inc()
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, "inc($n)")
        n.dec()
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "dec($n)")
        n.read()
        self.assertEqual(out.get()[-1].line, "read_persistent_var($n)")
        self.assertEqual(n.generate_init(),
                         ['declare $n', 'make_persistent($n)'])
        old = n
        n += 1
        new = n
        self.assertEqual(old.val, new.val)
        self.assertIs(old._value, new._value)

    def test_magic(self) -> None:
        n = self.n
        out = self.out
        n <<= 1
        n += n
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, "$n := $n + $n")
        n -= n
        self.assertEqual(n.val, 0)
        self.assertEqual(out.get()[-1].line, "$n := $n - $n")
        n += n + 2
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, "$n := $n + ($n + 2)")
        n += n - 3
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "$n := $n + ($n - 3)")
        n -= n - 2
        self.assertEqual(n.val, 2)
        self.assertEqual(out.get()[-1].line, "$n := $n - ($n - 2)")
        n -= n + 1
        self.assertEqual(n.val, -1)
        self.assertEqual(out.get()[-1].line, "$n := $n - ($n + 1)")
        n -= n
        self.assertEqual(n.val, 0)
        self.assertEqual(out.get()[-1].line, "$n := $n - $n")
        n <<= 2

        n *= n + 2
        self.assertEqual(n.val, 8)
        self.assertEqual(out.get()[-1].line, "$n := $n * ($n + 2)")
        n *= n
        self.assertEqual(n.val, 64)
        self.assertEqual(out.get()[-1].line, "$n := $n * $n")

        n /= n / 8
        self.assertEqual(n.val, 8)
        self.assertEqual(out.get()[-1].line, "$n := $n / ($n / 8)")
        n /= n
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "$n := $n / $n")
        n /= 0
        self.assertEqual(n.val, 0)
        self.assertEqual(out.get()[-1].line, "$n := $n / 0")
        n <<= 3
        n /= 2
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "$n := $n / 2")

        n <<= 3
        n %= 2
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "$n := $n mod 2")
        n %= 2 + n
        self.assertEqual(n.val, 1)
        self.assertEqual(out.get()[-1].line, "$n := $n mod (2 + $n)")

        n <<= 3
        self.assertEqual(bt.get_value(n << 2), 12)
        self.assertEqual(bt.get_compiled(n << 2), "sh_left($n, 2)")
        self.assertEqual(bt.get_value(n >> 2), 0)
        self.assertEqual(bt.get_compiled(n >> 2), "sh_right($n, 2)")
        self.assertEqual(bt.get_value(2 << n), 16)
        self.assertEqual(bt.get_compiled(2 << n), "sh_left(2, $n)")
        self.assertEqual(bt.get_value(2 >> n), 0)
        self.assertEqual(bt.get_compiled(2 >> n), "sh_right(2, $n)")

    def test_comparisson(self) -> None:
        n = self.n
        n <<= 3
        with self.assertRaises(NotImplementedError):
            bt.get_value(n == 3)

        self.assertTrue(n & 2)
        self.assertFalse(n & (n == 2))
        self.assertEqual((n & 3).get_value(), 3)
        self.assertEqual((n & 3).expand_bool(), "$n and 3")
        self.assertEqual((n & 3).expand(), "$n .and. 3")
        self.assertEqual((3 & n).get_value(), 3)
        self.assertEqual((3 & n).expand_bool(), "3 and $n")

        self.assertTrue(n | 2)
        self.assertFalse((n != 3) | (n == 2))
        self.assertEqual((n | 3).get_value(), 3)
        self.assertEqual(((n != 3) | (n == 2)).expand_bool(),
                         "$n # 3 or $n = 2")
        self.assertEqual(
            ((n != 3) | (n == 2) & (n != 4)).expand_bool(),
            "$n # 3 or $n = 2 and $n # 4",
        )
        self.assertEqual((n | 3).expand_bool(), "$n or 3")
        self.assertEqual((n | 3).expand(), "$n .or. 3")
        self.assertEqual((3 | n).expand_bool(), "3 or $n")
        self.assertEqual((3 | n).expand(), "3 .or. $n")

        self.assertTrue(n == 3)
        self.assertFalse(n == 2)
        self.assertEqual(bt.get_compiled(n == 3), "$n = 3")

        self.assertTrue(n != 2)
        self.assertFalse(n != 3)
        self.assertEqual(bt.get_compiled(n != 3), "$n # 3")

        self.assertTrue(n > 2)
        self.assertFalse(n > 3)
        self.assertEqual(bt.get_compiled(n > 3), "$n > 3")

        self.assertTrue(n < 4)
        self.assertFalse(n < 2)
        self.assertEqual(bt.get_compiled(n < 3), "$n < 3")

        self.assertTrue(n < 4)
        self.assertFalse(n < 2)
        self.assertEqual(bt.get_compiled(n < 3), "$n < 3")

        self.assertTrue(n <= 3)
        self.assertTrue(n <= 4)
        self.assertFalse(n <= 2)
        self.assertEqual(bt.get_compiled(n <= 3), "$n <= 3")

        self.assertTrue(n >= 3)
        self.assertTrue(n >= 2)
        self.assertFalse(n >= 4)
        self.assertEqual(bt.get_compiled(n >= 3), "$n >= 3")

        n <<= -3
        self.assertEqual(bt.get_value(abs(n)), 3)
        self.assertEqual(bt.get_compiled(abs(n)), "abs($n)")
        self.assertEqual(bt.get_value(abs(n - 1)), 4)
        self.assertEqual(bt.get_compiled(abs(n - 1)), "abs($n - 1)")


class TestArray(TestBase):
    def testi_int(self) -> None:
        with self.assertRaises(TypeError):
            bt.Arr[int]("s")  # type: ignore
        a = bt.Arr[int]([5, 6], name="a")
        with self.assertRaises(TypeError):
            a <<= 1
        self.assertTrue(issubclass(a._ref_type, int))
        self.assertEqual(a.val, [5, 6])
        self.assertEqual(a.get_decl_line(), ["declare %a[2] := (5, 6)"])
        self.assertEqual(len(a), 2)
        self.assertIsInstance(a[0], bt.Var[int])
        self.assertEqual(a[0].val, 5)
        self.assertEqual(a[0].name(), "%a[0]")
        out = ab.KSP.new_out()
        a[0] <<= bt.Var[int](2, name="intvar")
        self.assertEqual(a[0].val, 2)
        self.assertEqual(a[0].name(), "%a[0]")
        self.assertEqual(out.get()[-1].line, "%a[0] := $intvar")

        a[0] <<= 8
        self.assertEqual(a[0].val, 8)
        self.assertEqual(a[0].name(), "%a[0]")
        self.assertEqual(out.get()[-1].line, "%a[0] := 8")

        test = bt.Var[int](5, "test", local=True)
        test1 = bt.Var[int](1, "test1", local=True)

        a[0] <<= test
        self.assertEqual(a[0].val, 5)
        self.assertEqual(a[0].name(), "%a[0]")
        self.assertEqual(out.get()[-1].line, "%a[0] := $test")

        with self.assertRaises(IndexError):
            a[2]
        with self.assertRaises(TypeError):
            a[1] = 3  # type: ignore
        a.append(4)
        self.assertEqual(len(a), 3)
        self.assertIsInstance(a[2], bt.Var[int])
        self.assertEqual(a[2].val, 4)
        with self.assertRaises(TypeError):
            a.append(4.9)  # type: ignore
        a.append(test)
        self.assertEqual(out.get()[-1].line, "%a[3] := $test")
        self.assertEqual(len(a), 4)
        self.assertEqual(a.get_decl_line(), ["declare %a[4] := (5, 6, 4)"])
        ab.KSP.set_callback(True)  # type: ignore
        with self.assertRaises(RuntimeError):
            a.append(2)
        ab.KSP.set_callback(None)
        with self.assertRaises(TypeError):
            a.append(3.0)  # type: ignore

        a[test1] <<= test
        self.assertEqual(a[1].val, 5)
        self.assertEqual(a[test1].name(), "%a[$test1]")
        self.assertEqual(out.get()[-1].line, "%a[$test1] := $test")

        a_sized = bt.Arr[int](2, name="a_sized", size=3)
        self.assertEqual(len(a_sized), 3)
        self.assertEqual(a_sized[2].val, 2)
        self.assertEqual(a_sized[2].val, a_sized[-1].val)
        a_sized.append(3)
        a_sized.append(4)
        with self.assertRaises(RuntimeError):
            a_sized.append(5)
        assigned = a_sized[0]
        assigned <<= 8
        self.assertEqual(a_sized[0].val, 8)
        assigned += 1
        self.assertEqual(a_sized[0].val, 9)

        a_bad = bt.Arr([1, test])  # type: ignore
        with self.assertRaises(TypeError):
            a_bad.get_decl_line()  # type: ignore

        with self.assertRaises(TypeError):
            a_sized[0] = 4  # type: ignore

        self.assertEqual(a_sized[0].val, 9)
        test = a_sized[0]
        a_sized[0] = bt.Var[int](4, name='local', local=True)
        self.assertEqual(a_sized[0].val, 4)
        self.assertEqual(test.val, 4)
        with self.assertRaises(IndexError):
            a_sized[0.4]  # type: ignore

    def test_str(self) -> None:
        a = bt.Arr[str](['a', 'b'], name='str_arr')
        a.append('c')
        self.assertEqual(a.get_decl_line(), [
            'declare !str_arr[3]',
            '!str_arr[0] := "a"',
            '!str_arr[1] := "b"',
            '!str_arr[2] := "c"',
        ])
        with self.assertRaises(RuntimeError):
            a.read()

        with self.assertRaises(NotImplementedError):
            for i in a:  # type: ignore
                pass

    def test_ideas(self) -> None:
        pass


class TestTypes(ut.TestCase):
    def runTest(self) -> None:
        n = "local"
        iv = bt.Var[int](name=n, local=True)
        sv = bt.Var[str](name=n, local=True)
        fv = bt.Var[float](name=n, local=True)

        i = bt.VarInt(name=n, local=True)
        f = bt.VarFloat(name=n, local=True)
        s = bt.VarStr(name=n, local=True)

        ia = bt.Arr[int](name=n, local=True, size=6)
        sa = bt.Arr[str](name=n, local=True, size=6)
        fa = bt.Arr[float](name=n, local=True, size=6)

        self.assertIsInstance(iv, bt.Var[int])
        self.assertIsInstance(sv, bt.Var[str])
        self.assertIsInstance(fv, bt.Var[float])
        self.assertIsInstance(iv, bt.Num)
        self.assertIsInstance(sv, bt.VarStr)
        self.assertIsInstance(fv, bt.Num)
        self.assertIsInstance(iv, bt.Var)
        self.assertIsInstance(sv, bt.Var)
        self.assertIsInstance(fv, bt.Var)
        self.assertNotIsInstance(iv, bt.Var[str])
        self.assertNotIsInstance(sv, bt.Var[float])
        self.assertNotIsInstance(fv, bt.Var[int])
        self.assertNotIsInstance(5, bt.Var[str])

        self.assertIsInstance(i, bt.Var[int])
        self.assertIsInstance(f, bt.Var[float])
        self.assertIsInstance(s, bt.Var[str])
        self.assertNotIsInstance(i, bt.Var[str])
        self.assertNotIsInstance(s, bt.Var[float])
        self.assertNotIsInstance(f, bt.Var[int])

        self.assertNotIsInstance(ia, bt.Var[int])
        self.assertNotIsInstance(sa, bt.Var[str])
        self.assertNotIsInstance(fa, bt.Var[float])

        # TODO TOTHINK
        # self.assertIsInstance(ia, bt.Var[int, 0])
        # self.assertIsInstance(sa, bt.Var[str, 0])
        # self.assertIsInstance(fa, bt.Var[float, 0])

        # self.assertIsInstance(ia, bt.Var[int, 4])
        # self.assertIsInstance(sa, bt.Var[str, 2])
        # self.assertIsInstance(fa, bt.Var[float, 1])

        # self.assertIsInstance(ia, bt.Var[int, 6])
        # self.assertIsInstance(sa, bt.Var[str, 6])
        # self.assertIsInstance(fa, bt.Var[float, 6])

        # self.assertNotIsInstance(ia, bt.Var[int, 7])
        # self.assertNotIsInstance(sa, bt.Var[str, 7])
        # self.assertNotIsInstance(fa, bt.Var[float, 7])

        # self.assertNotIsInstance(ia, bt.Var[str, 0])
        # self.assertNotIsInstance(sa, bt.Var[float, 0])
        # self.assertNotIsInstance(fa, bt.Var[int, 0])

        with self.assertRaises(TypeError):
            self.assertNotIsInstance(fa, bt.Var[object()])  # type: ignore
        with self.assertRaises(TypeError):
            self.assertNotIsInstance(fa, bt.Var[float, -1])

        self.assertIsInstance(bt.Var(2, name=n, local=True), bt.Var[int])
        self.assertIsInstance(bt.Var("2", name=n, local=True), bt.Var[str])
        self.assertIsInstance(bt.Var(2.0, name=n, local=True), bt.Var[float])

        self.assertNotIsInstance(bt.Var(2, name=n, local=True), bt.Var[float])
        self.assertNotIsInstance(
            bt.Var("2", name=n, local=True), bt.Var[float])
        self.assertNotIsInstance(bt.Var(2.0, name=n, local=True), bt.Var[int])
