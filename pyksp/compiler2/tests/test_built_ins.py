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
from abstract import KspObject

from dev_tools import unpack_lines

from callbacks import *
from k_built_ins import *

from native_types import kInt
from native_types import kArrInt

from ui_system import kWidget

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


class TestCallback(DevTest):

    def test_mycb(self):
        my_cb = Callback('cb')
        my_cb.open()
        Output().put('body')
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

        FunctionCallback.open()
        Output().put('function2 line')
        FunctionCallback.close()

        Output().put('function1 line')
        FunctionCallback.close()

        Output().put('release close')
        ReleaseCallback.close()
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


class TestWrapers(DevTest):

    def setUp(self):
        Output().refresh()
        self.var = 4

    def cb(self):
        Output().put(f'cb body is {self.var}')

    def runTest(self):

        @init
        def foo():
            Output().put('foo_line')

        @init
        def bar():
            Output().put('bar_line')

        init(self.cb)

        self.assertEqual(
            unpack_lines(InitCallback.generate_body()), init_lines)


class TestBuiltInID(DevTest):

    class SomeId(BuiltInID):
        pass

    def runTest(self):
        a = object()
        a_id = BuiltInID('a_obj', a)
        self.assertEqual(a_id._get_runtime(), 0)
        self.assertEqual(a_id._get_compiled(), '$a_obj')
        self.assertEqual(a_id.obj, a)
        self.assertEqual(BuiltInID.get_by_id(a_id), a)
        b = object()
        b_id = self.SomeId('b_obj', b)
        self.assertEqual(b_id._get_runtime(), 0)
        self.assertEqual(b_id._get_compiled(), '$b_obj')
        self.assertEqual(b_id.obj, b)
        self.assertEqual(self.SomeId.get_by_id(b_id), b)
        c = object()
        c_id = BuiltInID('c_obj', c)
        self.assertEqual(c_id._get_runtime(), 1)
        BuiltInID.refresh()
        with self.assertRaises(IndexError):
            self.SomeId.get_by_id(b_id)
        with self.assertRaises(IndexError):
            BuiltInID.get_by_id(a_id)


class TestBuiltIn(DevTest):

    def test_init(self):
        my_var = BuiltIn('my_var')
        self.assertEqual(my_var._get_runtime(), 0)
        self.assertEqual(my_var._get_compiled(), '$my_var')
        self.assertEqual(BuiltInID.get_by_id(
            my_var._get_runtime()), my_var)

        my_var_int = BuiltIn('my_var_int', ret_type=kInt, ret_value=3)
        self.assertEqual(my_var_int._get_runtime(), 3)
        self.assertEqual(my_var_int._get_compiled(), '$my_var_int')

        my_var_arr = BuiltIn('my_var_arr', ret_type=kArrInt,
                             ret_value=[3, 3])
        self.assertEqual(my_var_arr._get_runtime(), [3, 3])
        self.assertEqual(my_var_arr._get_compiled(), '%my_var_arr')

        self.assertEqual(KspObject.generate_all_inits(), [])

    def test_calls(self):
        all_cb = BuiltIn('all_cb')
        only_init = BuiltIn('only_init', callbacks=(InitCallback,))
        only_async = BuiltIn('only_async',
                             callbacks=(AsyncCompleteCallback,))
        init_async = BuiltIn('only_async',
                             callbacks=(AsyncCompleteCallback,
                                        InitCallback))

        InitCallback.open()
        only_init.val
        all_cb.val
        init_async.val
        InitCallback.close()
        only_init.val
        all_cb.val
        KSP.in_init(False)
        with self.assertRaises(RuntimeError):
            only_init.val

        with self.assertRaises(RuntimeError):
            only_async.val
        with self.assertRaises(RuntimeError):
            init_async.val
        AsyncCompleteCallback.open()
        only_async.val
        init_async.val


class TestControlPar(DevTest):

    def runTest(self):
        cpar = ControlPar('POS_X', 'x')
        self.assertEqual(cpar._get_compiled(), '$CONTROL_PAR_POS_X')


my_control_init = '''declare ui_my_control $x
%_MyControl_ids[0] := get_ui_id($x)'''

generated_null_control =\
    '''declare %_MyControl_ids[3]
declare ui_my_control $x
%_MyControl_ids[0] := get_ui_id($x)
declare ui_my_control $y
%_MyControl_ids[1] := get_ui_id($y)
declare ui_my_control $z
%_MyControl_ids[2] := get_ui_id($z)
declare %_MyControl_x[3] := (5, -1, 3)
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 3)
if(-1 # %_MyControl_x[%_for_loop_idx[$_for_loop_curr_idx]])
set_control_par(%_MyControl_ids[%_for_loop_idx[$_for_loop_curr_idx]],\
 $CONTROL_PAR_POS_X, %_MyControl_x[%_for_loop_idx[$_for_loop_curr_idx]])
end if
%_for_loop_idx[$_for_loop_curr_idx] := %_for_loop_idx[\
$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)'''

# @t.skip


class TestNativeControl(DevTest):

    def setUp(self):
        super().setUp()
        # kNativeControl.refresh()

    class MyControl(kNativeControl):
        def _get_init_line(self):
            return f'declare ui_my_control {self._get_compiled()}'

    def test_null(self):
        KSP.set_compiled(True)
        x = self.MyControl(kInt(name='x', is_local=True))
        self.assertEqual(x.id._get_runtime(), 0)
        self.assertEqual(x.id._get_compiled(), '%_MyControl_ids[0]')
        self.assertEqual(x.get_by_id(0), x)
        self.assertEqual(x._get_runtime(), 0)
        self.assertEqual(x._get_compiled(), '$x')
        self.assertEqual(Output().get(), [])
        # self.assertEqual(unpack_lines(
        #     KspObject.generate_all_inits()), generated_null_control)

        self.assertEqual(Output().get(), [])
        x.x = 5
        self.assertEqual(Output().get(), [])
        # kNativeControl._init_is_generated = False
        self.MyControl(kInt(name='y', is_local=True))
        z = self.MyControl(kInt(name='z', is_local=True))
        # y.x = 3
        z.x = 3
        self.maxDiff = None
        self.assertEqual(unpack_lines(
            KspObject.generate_all_inits()), generated_null_control)
        self.assertEqual(Output().get(), [])
        with self.assertRaises(NameError):
            self.MyControl(kInt(name='x', is_local=True))

    def test_widget(self):
        KSP.set_compiled(True)
        w = kWidget(x=10, y=20, width=90, height=80)
        c = self.MyControl(kInt(name='c', is_local=True), parent=w, x=1)
        # c.x = 2
        # c.x = 5
        c.pack(sticky='senw')
        self.assertEqual(
            Output().get()[-1],
            'set_control_par(%_MyControl_ids[4], $CONTROL_PAR_POS_X, 10)')
        self.assertEqual(c.x._get_runtime(), 10)
        self.assertEqual(c.y._get_runtime(), 20)
        self.assertEqual(c.width._get_runtime(), 90)
        self.assertEqual(c.height._get_runtime(), 80)


if __name__ == '__main__':
    t.main()
