import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)


from native_types import *
from abstract import KSP
from dev_tools import DevTest


class TestNative(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().setUp()

    def test_ksp_native(self):
        KSP.toggle_test_state(False)
        x = KspNative(1, 'name', '$')
        self.assertEqual(x(), '$name')
        KSP.toggle_test_state()
        self.assertEqual(x(), 1)
        KSP.toggle_test_state()

    def test_k_int(self):
        KSP.toggle_test_state(False)
        x = kInt('int')
        self.assertEqual(x(), '$int')
        KSP.toggle_test_state()
        self.assertEqual(x(), 0)
        x += 1
        self.assertEqual(x(), 1)
        with self.assertRaises(TypeError):
            x('1')
        with self.assertRaises(TypeError):
            x(1.0)

    def test_k_str(self):
        KSP.toggle_test_state(False)
        x = kStr('str')
        self.assertEqual(x(), '@str')
        KSP.toggle_test_state()
        self.assertEqual(x(), '')
        x += '1'
        self.assertEqual(x(), '1')
        with self.assertRaises(TypeError):
            x(1)
        with self.assertRaises(TypeError):
            x(1.0)
        y = kInt('int', 4)
        x += y
        self.assertEqual(x(), '14')

    def test_k_arr_int(self):
        KSP.toggle_test_state(False)
        x = kArrInt('arr_int')
        self.assertEqual(x(), r'%arr_int')
        KSP.toggle_test_state(True)
        self.assertEqual(x(), [])
        x.append(1)
        self.assertEqual(x(), [1])
        x.append(1)
        self.assertEqual(x(), [1, 1])
        x.extend([2, 3])
        self.assertEqual(x(), [1, 1, 2, 3])
        with self.assertRaises(TypeError):
            x(1)
        with self.assertRaises(TypeError):
            x(1.0)
        KSP.toggle_test_state(False)
        with self.assertRaises(KspNativeArray.error):
            for item in x:
                continue
        KSP.toggle_test_state(True)
        y = kInt('int', 4)
        x.append(y)
        self.assertEqual(x(), [1, 1, 2, 3, 4])

    def test_k_arr_str(self):
        KSP.toggle_test_state(False)
        x = kArrStr('arr_str')
        self.assertEqual(x(), r'!arr_str')
        KSP.toggle_test_state(True)
        self.assertEqual(x(), [])
        x.append('1')
        self.assertEqual(x(), ['1'])
        x.append('1')
        self.assertEqual(x(), ['1', '1'])
        x.extend(['2', '3'])
        self.assertEqual(x(), ['1', '1', '2', '3'])
        with self.assertRaises(TypeError):
            x.append(1)
        with self.assertRaises(TypeError):
            x.append(1.0)
        KSP.toggle_test_state(False)
        with self.assertRaises(KspNativeArray.error):
            for item in x:
                continue
        KSP.toggle_test_state(True)
        y = kInt('int', 4)
        x.append(y)
        self.assertEqual(x(), ['1', '1', '2', '3', '4'])
        y = kStr('str', 'string')
        x.append(y)
        self.assertEqual(x(), ['1', '1', '2', '3', '4', 'string'])

    def test_k_arr_real(self):
        KSP.toggle_test_state(False)
        x = kArrReal('arr_real')
        self.assertEqual(x(), '?arr_real')
        KSP.toggle_test_state(True)
        self.assertEqual(x(), [])
        x.append(1.0)
        self.assertEqual(x(), [1.0])
        x.append(1.0)
        self.assertEqual(x(), [1.0, 1.0])
        x.extend([2.0, 3.0])
        self.assertEqual(x(), [1.0, 1.0, 2.0, 3.0])
        with self.assertRaises(TypeError):
            x(1)
        with self.assertRaises(TypeError):
            x.append(1)
        KSP.toggle_test_state(False)
        with self.assertRaises(KspNativeArray.error):
            for item in x:
                continue
        KSP.toggle_test_state(True)
        y = kReal('real', 4.0)
        x.append(y)
        self.assertEqual(x(), [1.0, 1.0, 2.0, 3.0, 4.0])


class TestVar(DevTest, t.TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_return_types(self):
        kint = kVar(1)
        self.assertIsInstance(kint, kInt)

        kstr = kVar('1')
        self.assertIsInstance(kstr, kStr)

        kreal = kVar(1.0)
        self.assertIsInstance(kreal, kReal)

        karrInt = kVar([1, 2, 3])
        self.assertIsInstance(karrInt, kArrInt)

        karrReal = kVar([1.0, 2.0, 3.0])
        self.assertIsInstance(karrReal, kArrReal)

        karrStr = kVar(['1', "2", '3'])
        self.assertIsInstance(karrStr, kArrStr)


if __name__ == '__main__':
    t.main()
