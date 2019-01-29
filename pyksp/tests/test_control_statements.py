import unittest as ut

from .. import abstract as ab
from .. import base_types as bt
from .. import control_statements as cs

if_lines = '''\
if($a = $b)
    $c := $c + 1
    if($a = 1)
        $c := $c + 1
    else
        $c := $c + 1
    end if
else
    $c := $c + 1
end if
if($a # $b and $a = 1)
    $c := $c + 1
    if($a = $b)
        $c := $c + 1
    end if
end if
if($a # $b)
    $c := $c + 1
else
    $c := $c + 1
end if
if($a = $b)
    $c := $c + 1
else
    if($a = 2)
        $c := $c + 1
    end if
end if
else
    $c := $c + 1
end if'''


class TestIfElse(ut.TestCase):
    def tearDown(self) -> None:
        ab.KSP.refresh()

    def runTest(self) -> None:
        a = bt.Var[int](1, name='a', local=True)
        b = bt.Var[int](2, name='b', local=True)
        c = bt.Var[int](name='c', local=True)

        out = ab.KSP.new_out()
        with self.assertRaises(RuntimeError):
            cs.Else()

        with cs.If(a == b):
            c += 1
            self.assertEqual(c.val, 0)
            with cs.If(a == 1):
                c += 1
                self.assertEqual(c.val, 0)
            with cs.Else():
                c += 1
                self.assertEqual(c.val, 0)
        with cs.Else():
            c += 1
            self.assertEqual(c.val, 1)
        with cs.If((a != b) & (a == 1)):
            c += 1
            self.assertEqual(c.val, 2)
            with cs.If(a == b):
                c += 1
                self.assertEqual(c.val, 2)
        with cs.If(a != b):
            c += 1
            self.assertEqual(c.val, 3)
        with cs.Else():
            c += 1
            self.assertEqual(c.val, 3)
        with cs.If(a == b):
            with self.assertRaises(RuntimeError):
                cs.Else()
            c += 1
            self.assertEqual(c.val, 3)
        with cs.Else(a == 2):
            c += 1
            self.assertEqual(c.val, 3)
        with cs.Else():
            c += 1
            self.assertEqual(c.val, 4)
        out.put_immediatly(ab.AstNull())
        self.assertEqual(out.get_str(), if_lines)
        with self.assertRaises(StopIteration):
            with cs.If(a != b):
                raise StopIteration


case_str = """\
select($var)
    case(4)
        $var := $var + 1
        if($var2 = 3)
            $var := $var + 1
        end if
    case(16)
        $var := $var + 1
    case(17)
        $var := $var + 1
        select($var + $var2)
            case(21)
                $var := $var + 1
                if($var2 = 3)
                    $var := $var + 1
                end if
        end select
end select
inc($var)"""


class TestSelect(ut.TestCase):
    def tearDown(self) -> None:
        ab.KSP.refresh()

    def runTest(self) -> None:
        var = bt.Var[int](16, name='var', local=True)
        var2 = bt.Var[int](3, name='var2', local=True)
        ab.KSP.set_listener(ab.EventListener())
        out = ab.KSP.new_out()

        with cs.Select(var):
            with self.assertRaises(cs.CaseException):
                var <<= 14
            self.assertEqual(var.val, 16)
            with cs.Case(4):
                var += 1
                self.assertEqual(var.val, 16)
                with cs.If(var2 == 3):
                    var += 1
                    self.assertEqual(var.val, 16)
            with cs.Case(16):
                var += 1
                self.assertEqual(var.val, 17)
                with self.assertRaises(RuntimeError):
                    with cs.Case(5):
                        pass
            with cs.Case(17):
                var += 1
                self.assertEqual(var.val, 18)
                with cs.Select(var + var2):
                    with cs.Case(21):
                        var += 1
                        self.assertEqual(var.val, 19)
                        with cs.If(var2 == 3):
                            var += 1
                            self.assertEqual(var.val, 20)

        var.inc()
        self.assertEqual(var.val, 21)
        self.assertEqual(out.get_str(), case_str)
        with self.assertRaises(TypeError):
            cs.Case(var2)  # type: ignore
