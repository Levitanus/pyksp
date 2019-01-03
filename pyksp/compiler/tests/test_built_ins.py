import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from abstract import Output
from abstract import KSP
# from abstract import KspObject

from dev_tools import unpack_lines

from callbacks import *
from k_built_ins import *
from bi_engine_par import *
from bi_load_save import *
from bi_midi import *
from bi_misc import *
from bi_notes_events import *

from native_types import kInt
from native_types import kArrInt

from collections import OrderedDict

my_cb_body = \
    '''on cb
body
body 2
end on'''

func_lines = \
    '''on release
release open
release close
end on'''

ui_lines = \
    '''on ui_control($kInt0)
control_1_line
end on
on ui_control($kInt1)
control_2_line
end on'''


@t.skip
class TestCallback(DevTest):

    def test_mycb(self):
        my_cb = Callback('cb', -1, ())
        my_cb.open()
        Output().put('body')
        self.assertEqual(NI_CALLBACK_TYPE, -1)
        my_cb.close()
        my_cb.open()
        Output().put('body 2')
        my_cb.close()
        self.assertEqual(unpack_lines(my_cb.generate_body()),
                         my_cb_body)
        self.assertEqual(unpack_lines(my_cb.get_all_bodies()),
                         my_cb_body)

    def test_func_callback(self):
        ReleaseCallback.open()
        Output().put('release open')

        FunctionCallback.open()
        Output().put('function1 line')
        self.assertEqual(NI_CALLBACK_TYPE,
                         NI_CB_TYPE_RELEASE)
        FunctionCallback.open()
        Output().put('function2 line')
        self.assertEqual(NI_CALLBACK_TYPE,
                         NI_CB_TYPE_RELEASE)
        FunctionCallback.close()

        Output().put('function1 line')
        FunctionCallback.close()

        Output().put('release close')
        ReleaseCallback.close()
        self.assertEqual(NI_CALLBACK_TYPE,
                         NI_CB_TYPE_INIT)
        self.assertEqual(Output().get(), ['function1 line',
                                          'function2 line',
                                          'function1 line'])
        self.assertEqual(unpack_lines(Callback.get_all_bodies()),
                         func_lines)

    def test_ui_control(self):
        control_1 = kInt()
        control_2 = kInt()
        UiControlCallback.open(control_1)
        Output().put('control_1_line')
        UiControlCallback.close()
        UiControlCallback.open(control_2)
        Output().put('control_2_line')
        UiControlCallback.close()
        with self.assertRaises(RuntimeError):
            UiControlCallback.open(control_1)

        self.assertEqual(
            unpack_lines(UiControlCallback.generate_body()),
            ui_lines)


init_lines = \
    '''on init
foo_line
bar_line
cb body is 4
end on'''

release_lines = \
    '''on release
release
end on'''


class TestWrapers(DevTest):

    def setUp(self):
        Output().refresh()
        # Callback.refresh()
        self.var = 4

    def cb(self):
        Output().put(f'cb body is {self.var}')
        self.var += 1

    def runTest(self):

        @init
        def foo():
            Output().put('foo_line')

        @init
        def bar():
            Output().put('bar_line')

        # init(foo)
        # init(bar)
        init(self.cb)
        self.assertEqual(self.var, 4)
        self.assertEqual(
            unpack_lines(InitCallback.generate_body()), init_lines)
        self.assertEqual(self.var, 5)

        @release
        def rls():
            Output().put('release')
        self.assertEqual(
            unpack_lines(ReleaseCallback.generate_body()), release_lines)
        rls()
        self.assertEqual(Output().pop(), 'release')


class TestBuiltInClasses(DevTest):

    def test_vars(self):
        x = BuiltInIntVar('x', def_val=7)
        self.assertEqual(x._get_runtime(), 7)
        self.assertEqual(x._get_compiled(), '$x')
        self.assertEqual(x.id, 0)
        self.assertEqual(x.val, 7)
        with self.assertRaises(NotImplementedError):
            x <<= 4
        var = kInt(x)
        self.assertEqual(var.val, 7)

        y = BuiltInRealVar('y', def_val=3.0,
                           callbacks=(InitCallback, ReleaseCallback))
        self.assertEqual(y._get_runtime(), 3.0)
        self.assertEqual(y._get_compiled(), '~y')
        self.assertEqual(y.id, 1)

        y.set_value(2.1)
        self.assertEqual(y.val, 2.1)

        arr = BuiltInArrayInt('arr', size=4)
        with self.assertRaises(NotImplementedError):
            arr[2] = 3
        self.assertEqual(arr.id, 2)
        arr.set_value(2, 3)
        self.assertEqual(arr[2], 3)
        self.assertEqual(arr[2]._get_compiled(), '%arr[2]')

        self.assertEqual(CURRENT_SCRIPT_SLOT._get_compiled(),
                         '$CURRENT_SCRIPT_SLOT')

    class MyFunc(BuiltInFunc):
        def __init__(self, name: str, callbacks=all_callbacks,
                     args: OrderedDict=None):
            super().__init__(name, callbacks, args)
            self._var = kInt(name=name)

        def calculate(self, arg1, arg2):
            if hasattr(arg1, '_get_runtime'):
                arg1 = arg1._get_runtime()
            if hasattr(arg2, '_get_runtime'):
                arg2 = arg2._get_runtime()
            return arg1 + arg2

    class MyFuncInt(BuiltInFuncInt):
        def __init__(self, name: str, callbacks=all_callbacks,
                     args: OrderedDict=None):
            super().__init__(name, callbacks, args)

        def calculate(self, arg1, arg2):
            if hasattr(arg1, '_get_runtime'):
                arg1 = arg1._get_runtime()
            if hasattr(arg2, '_get_runtime'):
                arg2 = arg2._get_runtime()
            return arg1 + arg2

    def test_func(self):
        x = self.MyFunc('my_func',
                        args=OrderedDict(arg1=int, arg2=BuiltInIntVar))
        self.assertEqual(x.id, 0)
        bi = BuiltInIntVar('BI', def_val=1)

        val = x(2, bi)
        self.assertEqual(val._get_compiled(), 'my_func(2, $BI)')
        self.assertEqual(val._get_runtime(), 3)
        val = x(val, bi)
        self.assertEqual(val._get_compiled(),
                         'my_func(my_func(2, $BI), $BI)')
        self.assertEqual(val._get_runtime(), 4)
        y = self.MyFuncInt('y_func',
                           args=OrderedDict(arg1=int, arg2=BuiltInIntVar))
        self.assertEqual(y.id, 2)
        val = y(x(1, bi), bi)
        self.assertEqual(val._get_compiled(),
                         'y_func(my_func(1, $BI), $BI)')
        self.assertEqual(val._get_runtime(), 3)
        KSP.set_compiled(True)
        self.assertEqual((y(1, bi) + x(2, bi)).expand(),
                         'y_func(1, $BI) + my_func(2, $BI)')

        Output().refresh()
        y(1, bi)
        self.assertEqual(Output().get()[-1], 'y_func(1, $BI)')
        Output().refresh()
        y(x(1, bi), bi)
        self.assertEqual(unpack_lines(Output().get()),
                         'y_func(my_func(1, $BI), $BI)')

    def test_message(self):
        KSP.set_compiled(True)
        message(3)
        self.assertEqual(Output().pop(), 'message(3)')
        message(2, 'string')
        self.assertEqual(Output().pop(), 'message(2 & ", " & "string")')
        message(2, 'string', sep=':')
        with self.assertRaises(AttributeError):
            message(2, 'string', sep='\n')
        self.assertEqual(Output().pop(), 'message(2 & ":" & "string")')
        set_controller(1, 5)
        self.assertEqual(Output().pop(), 'set_controller(1, 5)')
        self.assertEqual(CC[1]._get_runtime(), 5)

        arr = kArrInt(sequence=list(range(11)))
        self.assertEqual(arr._get_runtime(),
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        get_event_ids(arr)
        self.assertEqual(arr._get_runtime(),
                         [0, 1, 2, 3, 4, 5, 6, 0, 0, 0, 0])

        Output().refresh()
        seq = [1, 2, 3, 4]
        arr1, arr2, arr3 = kArrInt(seq), kArrInt(seq), \
            kArrInt([2, 3, 4, 5])
        self.assertTrue(array_equal(arr1, arr2))
        self.assertEqual(Output().pop(),
                         'array_equal(%kArrInt1, %kArrInt2)')
        self.assertFalse(array_equal(arr1, arr3)._get_runtime())
        self.assertEqual(Output().pop(),
                         'array_equal(%kArrInt1, %kArrInt3)')
        self.assertEqual(num_elements(arr1)._get_runtime(), 4)
        self.assertEqual(num_elements(arr1)._get_compiled(),
                         'num_elements(%kArrInt1)')
        self.assertEqual(search(arr3, 4)._get_runtime(), 2)
        self.assertEqual(search(arr3, 4)._get_compiled(),
                         'search(%kArrInt3, 4)')
        x = kInt(4, 'x')
        self.assertEqual(search(arr3, x)._get_compiled(),
                         'search(%kArrInt3, $x)')
        self.assertEqual(search(arr3, x)._get_runtime(), 2)
        arr2[1]._set_runtime(5)
        self.assertEqual(arr2._get_runtime(), [1, 5, 3, 4])
        sort(arr2, 0)
        self.assertEqual(arr2._get_runtime(), [1, 3, 4, 5])
        sort(arr2, 3)
        self.assertEqual(arr2._get_runtime(), [5, 4, 3, 1])

        KSP.set_compiled(False)
        self.assertTrue(get_key_color(0) == KEY_COLOR_NONE.id)
        set_key_color(0, KEY_COLOR_BLUE)
        self.assertFalse(get_key_color(0) == KEY_COLOR_NONE.id)
        self.assertTrue(get_key_color(0) == KEY_COLOR_BLUE.id)
        set_key_type(3, NI_KEY_TYPE_DEFAULT)
        self.assertEqual(get_key_type(3), NI_KEY_TYPE_DEFAULT.id)
        KSP.set_compiled(True)

        self.assertEqual(get_key_name(2)._get_runtime(), '')
        set_key_name(2, 'named')
        self.assertEqual(get_key_name(2)._get_runtime(), 'named')
        with self.assertRaises(RuntimeError):
            set_key_pressed(1, 1)
        set_key_pressed_support(1)
        set_key_pressed(1, 1)
        self.assertEqual(get_key_triggerstate(1)._get_runtime(), 1)
        self.assertEqual(get_key_triggerstate(1).val,
                         'get_key_triggerstate(1)')

        self.assertEqual(get_engine_par(
            ENGINE_PAR_RELEASE_TRIGGER, 1, 1, -1)._get_runtime(),
            1)
        self.assertEqual(get_engine_par_disp(
            ENGINE_PAR_RELEASE_TRIGGER, 1, 1, -1)._get_runtime(),
            'display')
        set_engine_par(ENGINE_PAR_RELEASE_TRIGGER, 50, 1, 1, -1)
        self.assertEqual(get_engine_par(
            ENGINE_PAR_RELEASE_TRIGGER, 1, 1, -1)._get_runtime(),
            50)
        self.assertEqual(get_engine_par_disp(
            ENGINE_PAR_RELEASE_TRIGGER, 1, 1, -1)._get_runtime(),
            '50')
        SET_CONDITION(NO_SYS_SCRIPT_RLS_TRIG)
        self.assertEqual(Output().pop(),
                         'SET_CONDITION(NO_SYS_SCRIPT_RLS_TRIG)')

        pgs_create_key('key', 2)
        self.assertEqual(Output().pop(),
                         'pgs_create_key(key, 2)')
        pgs_create_str_key('key')
        self.assertEqual(Output().pop(),
                         'pgs_create_str_key(key)')
        self.assertEqual(pgs_key_exists('key')._get_runtime(), int(1))
        self.assertEqual(pgs_str_key_exists('key')._get_runtime(), int(1))
        with self.assertRaises(IndexError):
            pgs_set_key_val('key', 2, 1)
        pgs_set_key_val('key', 1, 1)
        self.assertEqual(Output().pop(), 'pgs_set_key_val(key, 1, 1)')
        self.assertEqual(pgs_get_key_val('key', 1)._get_runtime(), 1)
        pgs_set_str_key_val('key', 'string')
        self.assertEqual(Output().pop(),
                         'pgs_set_str_key_val(key, "string")')
        self.assertEqual(pgs_get_str_key_val('key')._get_runtime(),
                         'string')


if __name__ == '__main__':
    t.main()
