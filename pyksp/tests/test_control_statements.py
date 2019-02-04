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


range_1_str = """\
%__for_idx__[0] := 0
while(%__for_idx__[0] < 3)
    $target := %__for_idx__[0]
    inc(%__for_idx__[0])
end while"""
range_2_str = """\
%__for_idx__[0] := 3
while(%__for_idx__[0] < 7)
    $target := %__for_idx__[0]
    inc(%__for_idx__[0])
end while
%__for_idx__[0] := 7
while(%__for_idx__[0] > 3)
    $target := %__for_idx__[0]
    dec(%__for_idx__[0])
end while"""
range_3_str = """\
%__for_idx__[0] := 2
while(%__for_idx__[0] < 7)
    $target := %__for_idx__[0]
    %__for_idx__[0] := %__for_idx__[0] + 2
end while
%__for_idx__[0] := 13
while(%__for_idx__[0] > 5)
    $target := %__for_idx__[0]
    %__for_idx__[0] := %__for_idx__[0] + -2
end while"""
break_str = """\
$target := 0
%__for_idx__[0] := 0
while(%__for_idx__[0] < 3)
    if(%__for_idx__[0] = 1)
        %__for_idx__[0] := 3
    end if
    inc($target)
    inc(%__for_idx__[0])
end while"""
nested_str = """\
%__for_idx__[0] := 0
while(%__for_idx__[0] < 3)
    if(%__for_idx__[0] > 1)
        %__for_idx__[1] := 0
        while(%__for_idx__[1] < 3)
            $target := $target + (%__for_idx__[0] + %__for_idx__[1])
            inc(%__for_idx__[1])
        end while
    else
        $target := $target + %__for_idx__[0]
    end if
    inc(%__for_idx__[0])
end while"""
simple_str = """\
%__for_idx__[0] := 0
while(%__for_idx__[0] < 6)
    $target := %iarr[%__for_idx__[0]]
    inc(%__for_idx__[0])
end while"""
zip_str = """\
%__for_idx__[0] := 0
while(%__for_idx__[0] < 3)
    if(int_to_real(%iarr[%__for_idx__[0]]) = ?arr_f[%__for_idx__[0]])
        inc($target)
    end if
    inc(%__for_idx__[0])
end while"""
enum_str = """\
%__for_idx__[0] := 0
while(%__for_idx__[0] < 3)
    if(int_to_real(%iarr[%__for_idx__[0]]) = ?arr_f[%__for_idx__[0]])
        inc($target)
    else
        if(%__for_idx__[0] = 1)
            inc($target)
        end if
    end if
    inc(%__for_idx__[0])
end while
%__for_idx__[0] := 0
while(%__for_idx__[0] < 6)
    if(%__for_idx__[0] = 2)
        $target := %iarr[%__for_idx__[0]]
    end if
    inc(%__for_idx__[0])
end while"""


class TestFor(ut.TestCase):
    def tearDown(self) -> None:
        bt.VarBase.refresh()
        ab.KSP.refresh()
        ab.NameVar.refresh()

    def setUp(self) -> None:
        self.iarr = bt.Arr[int]([1, 3, 4, 6, 8, 9], 'iarr')
        self.arr_f = bt.Arr[float]([1.0, 3.1, 4.0], 'arr_f')
        self.target = bt.VarInt(name='target')
        self.out = ab.KSP.new_out()

    def test_range_1(self) -> None:
        for i, idx in zip(cs.For(3), range(3)):
            self.assertEqual(i.val, idx)
            self.assertEqual(i.name(), '%__for_idx__[0]')
            self.target <<= i
        self.assertEqual(self.out.get_str(), range_1_str)

    def test_range_2(self) -> None:
        for i, idx in zip(cs.For(3, 7), range(3, 7)):
            self.assertEqual(i.val, idx)
            self.assertEqual(i.name(), '%__for_idx__[0]')
            self.target <<= i
        for i, idx in zip(cs.For(7, 3), [7, 6, 5, 4]):
            self.assertEqual(i.val, idx)
            self.assertEqual(i.name(), '%__for_idx__[0]')
            self.target <<= i
        self.assertEqual(self.out.get_str(), range_2_str)

    def test_range_3(self) -> None:
        for i, idx in zip(cs.For(2, 7, 2), range(2, 7, 2)):
            self.assertEqual(i.val, idx)
            self.assertEqual(i.name(), '%__for_idx__[0]')
            self.target <<= i

        for i, idx in zip(cs.For(13, 5, -2), range(13, 5, -2)):
            self.assertEqual(i.val, idx)
            self.assertEqual(i.name(), '%__for_idx__[0]')
            self.target <<= i
        self.assertEqual(self.out.get_str(), range_3_str)

    def test_break(self) -> None:
        with cs.For(3) as seq:  # type: ignore
            self.target <<= 0
            for i in seq:
                with cs.If(i == 1):
                    seq.break_loop()
                self.target.inc()
        self.assertEqual(self.target.val, 2)
        self.assertEqual(self.out.get_str(), break_str)

    def test_nested(self) -> None:
        self.target.val = 0
        for i1 in cs.For(3):
            with cs.If(i1 > 1):
                for i2 in cs.For(3):
                    self.target += i1 + i2
            with cs.Else():
                self.target += i1
        self.assertEqual(self.target.val, 10)
        self.assertEqual(self.out.get_str(), nested_str)

    def test_simple(self) -> None:
        for idx, i in enumerate(cs.For(self.iarr)):
            self.assertEqual(self.iarr.val[idx], i.val)
            self.target <<= i
        self.assertEqual(self.out.get_str(), simple_str)

    def test_zip(self) -> None:
        # CPD-OFF
        self.target.val = 0
        for idx, t in enumerate(cs.For(self.iarr, self.arr_f)):
            i, f = t
            self.assertEqual(self.iarr.val[idx], i.val)
            self.assertEqual(self.arr_f.val[idx], f.val)
            with cs.If(i.to_float() == f):
                self.target.inc()
        self.assertEqual(self.target.val, 2)
        self.assertEqual(self.out.get_str(), zip_str)
        # CPD-ON

    def test_enum(self) -> None:
        self.target.val = 0
        for idx, t in enumerate(cs.For(cs.enum, self.iarr, self.arr_f)):
            e, i, f = t
            self.assertEqual(self.iarr.val[idx], i.val)
            self.assertEqual(self.arr_f.val[idx], f.val)
            with cs.If(i.to_float() == f):
                self.target.inc()
            with cs.Else(e == 1):
                self.target.inc()
        self.assertEqual(self.target.val, 3)
        self.target.val = 0
        for idx1, i in cs.For(cs.enum, self.iarr):
            with cs.If(idx1 == 2):
                self.target <<= i
        self.assertEqual(self.target.val, 4)
        self.assertEqual(self.out.get_str(), enum_str)

    def test_errors(self) -> None:
        with self.assertRaises(TypeError):
            cs.For(1, self.iarr)  # type: ignore
        with self.assertRaises(TypeError):
            cs.For(self.iarr, 1)  # type: ignore
        with self.assertRaises(TypeError):
            cs.For(1, 2, 3, 4)  # type: ignore
        with self.assertRaises(TypeError):
            cs.For(cs.enum, 2, 3, 4)  # type: ignore
        with self.assertRaises(TypeError):
            cs.For(cs.enum)  # type: ignore
        with self.assertRaises(TypeError):
            cs.For(cs.enum, self.arr_f, 4)  # type: ignore
        with self.assertRaises(TypeError):
            cs.For(0)
        with self.assertRaises(TypeError):
            cs.For(-1)


while_str = """\
while($v = 1)
    inc($v)
end while"""


class TestWhile(ut.TestCase):
    def tearDown(self) -> None:
        bt.VarBase.refresh()
        ab.KSP.refresh()
        ab.NameVar.refresh()

    def runTest(self) -> None:
        out = ab.KSP.new_out()
        v = bt.Var[int](name='v')
        with cs.While(v == 1):
            v.inc()
        self.assertEqual(v.val, 1)
        self.assertEqual(out.get_str(), while_str)
        with self.assertRaises(TypeError):
            cs.While(v)  # type: ignore
