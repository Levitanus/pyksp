import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from native_types import *
from abstract import IName
from abstract import Output
from abstract import KSP


# @t.skip
class TestNativeVars(DevTest):

    def test_kInt(self):
        x = kInt()
        self.assertEqual(x.val, 0)
        self.assertEqual(x.name(), '$kInt0')
        self.assertEqual(x._generate_init(), ['declare $kInt0'])

        y = kInt(2)
        self.assertEqual(y.val, 2)
        self.assertEqual(y.name(), '$kInt1')
        self.assertEqual(y._generate_init(), ['declare $kInt1 := 2'])

        z = kInt(3, 'z', persist=True)
        self.assertEqual(z.val, 3)
        self.assertEqual(z.name(), '$z')
        self.assertEqual(z._generate_init(), ['declare $z := 3',
                                              'make_persistent($z)'])
        read = kInt()
        read.read()
        self.assertEqual(read._generate_init(),
                         ['declare $kInt2',
                          'make_persistent($kInt2)'])
        self.assertEqual(Output().get()[-1],
                         'read_persistent_var($kInt2)')
        with self.assertWarns(Warning):
            read.read()
        read.in_init(False)
        with self.assertRaises(RuntimeError):
            read.read()
        read.in_init(True)

        IName.set_compact(True)

        myvar = kInt(1, 'myvar')
        self.assertEqual(myvar.name(), '$cra4x')
        myvar_preserved = kInt(2, 'myvar_preserved', preserve=True)
        self.assertEqual(myvar_preserved.name(), '$myvar_preserved')
        IName.set_compact(False)
        myvar.set_compiled(True)

        myvar <<= myvar_preserved
        self.assertEqual(Output().get()[-1],
                         '$cra4x := $myvar_preserved')
        self.assertEqual(myvar.val, '$cra4x')
        self.assertEqual(myvar._get_runtime(), 2)
        myvar <<= myvar_preserved + 1
        self.assertEqual(Output().get()[-1],
                         '$cra4x := $myvar_preserved + 1')
        self.assertEqual(myvar._get_runtime(), 3)
        myvar *= 2
        self.assertEqual(Output().get()[-1],
                         '$cra4x := $cra4x * 2')
        self.assertEqual(myvar._get_runtime(), 6)

        with self.assertRaises(myvar.TypeWarn):
            myvar += 1.2
        with self.assertRaises(myvar.TypeWarn):
            myvar += 'string'
        myvar.inc()
        self.assertEqual(Output().pop(), 'inc($cra4x)')
        self.assertEqual(myvar._get_runtime(), 7)
        myvar.dec()
        self.assertEqual(Output().pop(), 'dec($cra4x)')
        self.assertEqual(myvar._get_runtime(), 6)

    def test_kReal(self):
        x = kReal()
        self.assertEqual(x.val, 0.0)
        self.assertEqual(x.name(), '~kReal0')
        self.assertEqual(x._generate_init(), ['declare ~kReal0'])

        y = kReal(2.0)
        self.assertEqual(y.val, 2.0)
        self.assertEqual(y.name(), '~kReal1')
        self.assertEqual(y._generate_init(),
                         ['declare ~kReal1 := 2.0'])

        z = kReal(3.0, 'z', persist=True)
        self.assertEqual(z.val, 3)
        self.assertEqual(z.name(), '~z')
        self.assertEqual(z._generate_init(), ['declare ~z := 3.0',
                                              'make_persistent(~z)'])
        read = kReal()
        read.read()
        self.assertEqual(read._generate_init(),
                         ['declare ~kReal2',
                          'make_persistent(~kReal2)'])
        self.assertEqual(Output().get()[-1],
                         'read_persistent_var(~kReal2)')
        with self.assertWarns(Warning):
            read.read()
        read.in_init(False)
        with self.assertRaises(RuntimeError):
            read.read()
        read.in_init(True)

        IName.set_compact(True)

        myvar = kReal(1.0, 'myvar')
        self.assertEqual(myvar.name(), '~cra4x')
        myvar_preserved = kReal(0.2, 'myvar_preserved', preserve=True)
        self.assertEqual(myvar_preserved.name(), '~myvar_preserved')
        IName.set_compact(False)
        myvar.set_compiled(True)

        myvar <<= myvar_preserved
        self.assertEqual(Output().get()[-1],
                         '~cra4x := ~myvar_preserved')
        self.assertEqual(myvar.val, '~cra4x')
        self.assertEqual(myvar._get_runtime(), 0.2)
        myvar <<= myvar_preserved + 1.0
        self.assertEqual(Output().get()[-1],
                         '~cra4x := ~myvar_preserved + 1.0')
        self.assertEqual(myvar._get_runtime(), 1.2)
        myvar *= 2.0
        self.assertEqual(Output().get()[-1],
                         '~cra4x := ~cra4x * 2.0')
        self.assertEqual(myvar._get_runtime(), 2.4)

        with self.assertRaises(myvar.TypeWarn):
            myvar += 1
        with self.assertRaises(myvar.TypeWarn):
            myvar += 'string'

    def test_kStr(self):
        x = kStr()
        self.assertEqual(x.val, '')
        self.assertEqual(x.name(), '@kStr0')
        self.assertEqual(x._generate_init(), ['declare @kStr0'])

        y = kStr('str')
        self.assertEqual(y.val, 'str')
        self.assertEqual(y.name(), '@kStr1')
        self.assertEqual(y._generate_init(),
                         ['declare @kStr1',
                          '@kStr1 := "str"'
                          ])

        z = kStr('3', 'z', persist=True)
        self.assertEqual(z.val, '3')
        self.assertEqual(z.name(), '@z')
        self.assertEqual(z._generate_init(), ['declare @z',
                                              '@z := "3"',
                                              'make_persistent(@z)'])
        read = kStr()
        read.read()
        self.assertEqual(read._generate_init(),
                         ['declare @kStr2',
                          'make_persistent(@kStr2)'])
        self.assertEqual(Output().get()[-1],
                         'read_persistent_var(@kStr2)')
        with self.assertWarns(Warning):
            read.read()
        read.in_init(False)
        with self.assertRaises(RuntimeError):
            read.read()
        read.in_init(True)

        IName.set_compact(True)

        myvar = kStr('str', 'myvar')
        self.assertEqual(myvar.name(), '@cra4x')
        myvar_preserved = kStr('2', 'myvar_preserved', preserve=True)
        self.assertEqual(myvar_preserved.name(), '@myvar_preserved')
        IName.set_compact(False)
        myvar.set_compiled(True)

        myvar <<= myvar_preserved
        self.assertEqual(Output().get()[-1],
                         '@cra4x := @myvar_preserved')
        self.assertEqual(myvar.val, '@cra4x')
        self.assertEqual(myvar._get_runtime(), '2')
        myvar <<= myvar_preserved + 'string'
        self.assertEqual(Output().get()[-1],
                         '@cra4x := @myvar_preserved & "string"')
        self.assertEqual(myvar._get_runtime(), '2string')

        myvar <<= kInt(name='test', value=1, is_local=True)
        self.assertEqual(Output().pop(), '@cra4x := $test')
        self.assertEqual(myvar._get_runtime(), '1')

    def test_locals(self):
        l_int = kInt(name='var', is_local=True)
        l_int.set_compiled(True)
        l_int <<= 2
        self.assertEqual(Output().pop(), '$var := 2')
        with self.assertRaises(RuntimeError):
            l_int.read()
        self.assertEqual(l_int.generate_all_inits(), [])

        l_real = kReal(name='var', is_local=True)
        l_real.set_compiled(True)
        l_real <<= 2.0
        self.assertEqual(Output().pop(), '~var := 2.0')
        with self.assertRaises(RuntimeError):
            l_real.read()
        self.assertEqual(l_real.generate_all_inits(), [])

        l_str = kStr(name='var', is_local=True)
        l_str.set_compiled(True)
        l_str <<= '1'
        self.assertEqual(Output().pop(), '@var := "1"')
        with self.assertRaises(RuntimeError):
            l_str.read()
        self.assertEqual(l_str.generate_all_inits(), [])


class TestNativeArrays(DevTest):

    def test_int(self):
        KSP.set_compiled(True)
        x = kArrInt()
        x.append(2)
        self.assertEqual(Output().pop(), '%kArrInt0[0] := 2')
        self.assertEqual(x[0].val, '%kArrInt0[0]')
        self.assertEqual(x._get_compiled(), '%kArrInt0')
        x.append(3)
        self.assertEqual(Output().pop(), '%kArrInt0[1] := 3')
        self.assertEqual(x[1].val, '%kArrInt0[1]')
        self.assertEqual(x._get_runtime(), [2, 3])
        self.assertEqual(x._generate_init(), ['declare %kArrInt0[2]'])

        y = kArrInt([1, 2, 3])
        y.append(4)
        self.assertEqual(Output().pop(), '%kArrInt1[3] := 4')
        self.assertEqual(y._get_runtime(), [1, 2, 3, 4])
        self.assertEqual(y._generate_init(),
                         ['declare %kArrInt1[4] := (1, 2, 3)'])

        IName.set_compact(True)
        z = kArrInt([1, 2], 'z')
        self.assertEqual(z.name(), '%z3yxf')
        self.assertEqual(z[1].val, '%z3yxf[1]')
        self.assertEqual(z[1]._get_runtime(), 2)
        z.read()
        self.assertEqual(Output().pop(), 'read_persistent_var(%z3yxf)')
        self.assertEqual(z._generate_init(),
                         ['declare %z3yxf[2] := (1, 2)',
                          'make_persistent(%z3yxf)'])

        preserved = kArrInt(name='preserved', preserve=True)
        self.assertEqual(preserved.name(), '%preserved')

        big = list(range(0, 1000000))
        big_arr = kArrInt(big)
        self.assertEqual(big_arr[3]._get_runtime(), 3)

    def test_real(self):
        KSP.set_compiled(True)
        x = kArrReal()
        x.append(2.0)
        self.assertEqual(Output().pop(), '?kArrReal0[0] := 2.0')
        self.assertEqual(x[0].val, '?kArrReal0[0]')
        self.assertEqual(x._get_compiled(), '?kArrReal0')
        x.append(3.0)
        self.assertEqual(Output().pop(), '?kArrReal0[1] := 3.0')
        self.assertEqual(x[1].val, '?kArrReal0[1]')
        self.assertEqual(x._get_runtime(), [2.0, 3.0])
        self.assertEqual(x._generate_init(), ['declare ?kArrReal0[2]'])

        y = kArrReal([1.0, 2.0, 3.0])
        y.append(4.0)
        self.assertEqual(Output().pop(), '?kArrReal1[3] := 4.0')
        self.assertEqual(y._get_runtime(), [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(y._generate_init(),
                         ['declare ?kArrReal1[4] := (1.0, 2.0, 3.0)'])

        IName.set_compact(True)
        z = kArrReal([1.0, 2.0], 'z')
        self.assertEqual(z.name(), '?z3yxf')
        self.assertEqual(z[1].val, '?z3yxf[1]')
        self.assertEqual(z[1]._get_runtime(), 2.0)
        z.read()
        self.assertEqual(Output().pop(), 'read_persistent_var(?z3yxf)')
        self.assertEqual(z._generate_init(),
                         ['declare ?z3yxf[2] := (1.0, 2.0)',
                          'make_persistent(?z3yxf)'])

        preserved = kArrReal(name='preserved', preserve=True)
        self.assertEqual(preserved.name(), '?preserved')

    def test_str(self):
        KSP.set_compiled(True)
        x = kArrStr()
        x.append('2')
        self.assertEqual(Output().pop(), '!kArrStr0[0] := "2"')
        self.assertEqual(x[0].val, '!kArrStr0[0]')
        self.assertEqual(x._get_compiled(), '!kArrStr0')
        x.append('3')
        self.assertEqual(Output().pop(), '!kArrStr0[1] := "3"')
        self.assertEqual(x[1].val, '!kArrStr0[1]')
        self.assertEqual(x._get_runtime(), ['2', '3'])
        self.assertEqual(x._generate_init(), ['declare !kArrStr0[2]'])

        y = kArrStr(['1', '2', '3'])
        y.append('4')
        self.assertEqual(Output().pop(), '!kArrStr1[3] := "4"')
        self.assertEqual(y._get_runtime(), ['1', '2', '3', '4'])
        self.assertEqual(y._generate_init(),
                         ['declare !kArrStr1[4]',
                          '!kArrStr1[0] := "1"',
                          '!kArrStr1[1] := "2"',
                          '!kArrStr1[2] := "3"'])

        IName.set_compact(True)
        string = kStr('string', 'str_var', preserve=True)
        z = kArrStr(['1', string], 'z')
        self.assertEqual(z.name(), '!z3yxf')
        self.assertEqual(z[1].val, '!z3yxf[1]')
        self.assertEqual(z[1]._get_runtime(), 'string')
        z.read()
        self.assertEqual(Output().pop(), 'read_persistent_var(!z3yxf)')
        self.assertEqual(z._generate_init(),
                         ['declare !z3yxf[2]',
                          '!z3yxf[0] := "1"',
                          '!z3yxf[1] := @str_var',
                          'make_persistent(!z3yxf)'])

        preserved = kArrStr(name='preserved', preserve=True)
        self.assertEqual(preserved.name(), '!preserved')

    def test_kVar(self):
        x = kVar()
        x <<= 1
        self.assertEqual(x.val, 1)

        arr_x = kVar(size=2)
        arr_x <<= [1, 2]
        self.assertIsInstance(arr_x, kArrInt)
        self.assertEqual(arr_x[0].val, 1)

        KSP.set_compiled(True)
        y = kVar(name='y')
        with self.assertRaises(AttributeError):
            y.val
        y <<= 'string'
        self.assertIsInstance(y, kStr)
        self.assertEqual(y.val, '@y')
        self.assertEqual(y._get_runtime(), 'string')

        z = kVar(1.0, 'z')
        self.assertIsInstance(z, kReal)
        self.assertEqual(z.val, '~z')
        self.assertEqual(z._get_runtime(), 1.0)

        IName.set_compact(True)
        myvar = kVar(1)
        self.assertEqual(myvar.val, '$nyxgq')
        preserved = kVar(1, 'preserved', preserve=True)
        self.assertEqual(preserved.val, '$preserved')
        preserved.read()
        self.assertEqual(Output().pop(),
                         'read_persistent_var($preserved)')
        self.assertEqual(preserved._generate_init(),
                         ['declare $preserved := 1',
                          'make_persistent($preserved)'])

        test = kVar(myvar)
        self.assertEqual(test._get_runtime(), 1)


if __name__ == '__main__':
    t.main()
