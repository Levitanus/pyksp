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
