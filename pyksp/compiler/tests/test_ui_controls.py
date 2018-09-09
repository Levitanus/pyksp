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

from dev_tools import unpack_lines
from bi_ui_controls import *
from abstract import KspObject
from base_types import KspVar
from bi_engine_par import NI_BUS_OFFSET

from native_types import kInt
from native_types import kArrInt

from conditions_loops import For, check, Else


def oget():
    return Output().get()


def olines():
    return unpack_lines(Output().get())


def opop():
    return Output().pop()


@t.skip
class TestContolParVars(DevTest):

    def test_int(self):
        KSP.set_compiled(True)
        x = kParIntVar(1, CONTROL_PAR_POS_X, kInt, set_control_par,
                       get_control_par)
        with self.assertRaises(kParVarGetError):
            x.val
        x <<= 2
        with self.assertRaises(IndexError):
            opop()
        self.assertEqual(x._get_runtime(), 2)
        self.assertEqual(x._get_compiled(), 2)

        x <<= 5
        self.assertEqual(opop(),
                         'set_control_par(1, $CONTROL_PAR_POS_X, 5)')
        ret = int()
        ret <<= x
        self.assertEqual(ret, 5)
        self.assertEqual(opop(),
                         'get_control_par(1, $CONTROL_PAR_POS_X)')
        val = kInt(10, 'val')
        x <<= val
        self.assertEqual(opop(),
                         'set_control_par(1, $CONTROL_PAR_POS_X, $val)')
        ret <<= x
        self.assertEqual(ret, '$val')
        self.assertEqual(opop(),
                         'get_control_par(1, $CONTROL_PAR_POS_X)')

        y = kParIntVar(2, CONTROL_PAR_POS_Y, 15)
        with self.assertRaises(IndexError):
            opop()
        self.assertEqual(y._get_runtime(), 15)
        self.assertEqual(y._get_compiled(), 15)
        y <<= 5
        self.assertEqual(opop(),
                         'set_control_par(2, $CONTROL_PAR_POS_Y, 5)')

    # @t.skip
    def test_str(self):
        KSP.set_compiled(True)
        x = kParStrVar(1, CONTROL_PAR_TEXT)
        with self.assertRaises(kParVarGetError):
            x.val
        x <<= 2
        with self.assertRaises(IndexError):
            opop()
        self.assertEqual(x._get_runtime(), 2)
        self.assertEqual(x._get_compiled(), 2)

        x <<= 5
        self.assertEqual(opop(),
                         'set_control_par(1, $CONTROL_PAR_POS_X, 5)')
        ret = int()
        ret <<= x
        self.assertEqual(ret, 5)
        self.assertEqual(opop(),
                         'get_control_par(1, $CONTROL_PAR_POS_X)')
        val = kInt(10, 'val')
        x <<= val
        self.assertEqual(opop(),
                         'set_control_par(1, $CONTROL_PAR_POS_X, $val)')
        ret <<= x
        self.assertEqual(ret, '$val')
        self.assertEqual(opop(),
                         'get_control_par(1, $CONTROL_PAR_POS_X)')

        y = kParIntVar(2, CONTROL_PAR_POS_Y, 15)
        with self.assertRaises(IndexError):
            opop()
        self.assertEqual(y._get_runtime(), 15)
        self.assertEqual(y._get_compiled(), 15)
        y <<= 5
        self.assertEqual(opop(),
                         'set_control_par(2, $CONTROL_PAR_POS_Y, 5)')


controls_loop =\
    '''inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 2)
set_control_par(%controls[%_for_loop_idx[$_for_loop_curr_idx]], \
$CONTROL_PAR_POS_X, 50)
inc(%_for_loop_idx[$_for_loop_curr_idx])
end while
dec($_for_loop_curr_idx)'''

# @t.skip


# @t.skip
class TestKspNativeControl(DevTest):

    class Child(KspNativeControl):

        pass

    # @t.skip
    def test_basic(self):
        KSP.set_compiled(True)
        control = KspNativeControl()
        self.assertEqual(control._id_lines,
                         ['%_all_ui_ids[0] := get_ui_id($control0)',
                          '%_KspNativeControl_ids[0] := %_all_ui_ids[0]'])
        self.assertEqual(control.id.val, '%_all_ui_ids[0]')
        self.assertEqual(control.id._get_runtime(), 0)
        self.assertIs(ControlId.get_by_id(0), control)
        with self.assertRaises(kParVarGetError):
            control.x.val
        with self.assertRaises(TypeError):
            control.x <<= 's'
        with self.assertRaises(kParVarGetError):
            control.x = 3
        control.x <<= 5
        self.assertEqual(control.x, 5)
        self.assertEqual(oget(), [])
        control.x <<= 50
        self.assertEqual(control.x, 50)
        self.assertEqual(opop(),
                         f'set_control_par({control.id.val}, ' +
                         '$CONTROL_PAR_POS_X, 50)')
        param = kInt(3)
        with self.assertRaises(RuntimeError):
            control.x = param
        control.x <<= param
        self.assertEqual(opop(),
                         f'set_control_par({control.id.val},' +
                         f' $CONTROL_PAR_POS_X, {param.val})')
        self.assertEqual(control.x, param._get_runtime())
        # print(control.x)
        self.assertEqual(control.x.val,
                         'get_control_par(%_all_ui_ids[0],' +
                         ' $CONTROL_PAR_POS_X)')
        self.assertEqual(control.x._get_runtime(), 3)

        native_2 = KspNativeControl(name='native_2', x=15)
        self.assertEqual(native_2._id_lines, [
                         '%_all_ui_ids[1] := get_ui_id($native_2)',
                         '%_KspNativeControl_ids[1] := %_all_ui_ids[1]'])
        self.assertEqual(control.id._get_runtime(), 0)
        self.assertEqual(control.id.val, '%_all_ui_ids[0]')
        self.assertEqual(native_2.id.val, '%_all_ui_ids[1]')
        self.assertEqual(native_2.id._get_runtime(), 1)
        self.assertIs(ControlId.get_by_id(1), native_2)
        self.assertEqual(native_2.x._get_runtime(), 15)
        self.assertEqual(oget(), [])

        Output().refresh()
        # KSP.set_compiled(False)
        controls = kArrInt([control.id, native_2.id], size=2,
                           name='controls')
        with For(arr=controls) as seq:
            for ctrl in seq:
                set_control_par(ctrl, 'x', 50)
        self.assertEqual(native_2.x._get_runtime(), 50)
        self.assertEqual(control.x._get_runtime(), 50)
        self.assertEqual(olines(), controls_loop)

    # @t.skip
    def test_child(self):
        KSP.set_compiled(True)
        # Output().refresh()
        child = self.Child()
        self.assertEqual(child._id_lines,
                         ['%_all_ui_ids[0] := get_ui_id($control0)',
                          '%_Child_ids[0] := %_all_ui_ids[0]'])
        self.assertEqual(child.id.val, f'%_all_ui_ids[0]')
        self.assertEqual(child.id._get_runtime(), 0)
        self.assertIs(ControlId.get_by_id(0), child)
        with self.assertRaises(kParVarGetError):
            child.x.val
        with self.assertRaises(TypeError):
            child.x <<= 's'
        with self.assertRaises(kParVarGetError):
            child.x = 3
        child.x <<= 5
        self.assertEqual(child.x, 5)
        self.assertEqual(oget(), [])
        child.x += 50
        self.assertEqual(child.x._get_runtime(), 55)
        set_control_par(child, CONTROL_PAR_POS_X, 10)
        self.assertEqual(child.x._get_runtime(), 10)
        self.assertEqual(opop(),
                         'set_control_par(%_all_ui_ids[0],' +
                         ' $CONTROL_PAR_POS_X, 10)')
        val = get_control_par(child, CONTROL_PAR_POS_X)._get_runtime()
        self.assertEqual(val, 10)
        self.assertEqual(opop(),
                         'get_control_par(%_all_ui_ids[0],' +
                         ' $CONTROL_PAR_POS_X)')

        child.help <<= 'my_help_line'
        # self.assertEqual(child.help.val, 'my_help_line')
        self.assertEqual(get_control_par_str(child, 'help').val,
                         'get_control_par_str(%_all_ui_ids[0], ' +
                         '$CONTROL_PAR_HELP)')
        child.hide <<= HIDE_PART_BG
        self.assertEqual(opop(),
                         'set_control_par(%_all_ui_ids[0], ' +
                         '$CONTROL_PAR_HIDE, $HIDE_PART_BG)')
        self.assertEqual(child.hide._get_runtime(), HIDE_PART_BG.id)

        button = kButton(name='my_button', persist=True)
        self.assertEqual(button.var._generate_init(),
                         ['declare ui_button $my_button ',
                          'make_persistent($my_button)',
                          '%_all_ui_ids[1] := get_ui_id($my_button)',
                          '%_kButton_ids[0] := %_all_ui_ids[1]'])
        self.assertEqual(button.var._get_runtime(), 0)
        button.value <<= 3
        self.assertEqual(button.var._get_runtime(), 3)
        button.var <<= 5
        self.assertEqual(button.value._get_runtime(), 5)

        switch = kSwitch()
        switch.read()
        self.assertEqual(switch.var._generate_init(),
                         ['declare ui_switch $control2 ',
                          'make_persistent($control2)',
                          'read_persistent_var($control2)',
                          '%_all_ui_ids[2] := get_ui_id($control2)',
                          '%_kSwitch_ids[0] := %_all_ui_ids[2]'])
        knob = kKnob(1, 5, 1)
        self.assertEqual(knob.var._generate_init(),
                         ['declare ui_knob $control3 (1, 5, 1)',
                          '%_all_ui_ids[3] := get_ui_id($control3)',
                          '%_kKnob_ids[0] := %_all_ui_ids[3]'])
        with self.assertRaises(RuntimeError):
            knob.var <<= 6
        knob.var <<= 5
        self.assertEqual(opop(), '$control3 := 5')
        knob.unit <<= KNOB_UNIT_DB
        self.assertEqual(opop(),
                         'set_control_par(%_all_ui_ids[3], ' +
                         '$CONTROL_PAR_UNIT, $KNOB_UNIT_DB)')
        self.assertEqual(knob.unit._get_runtime(), KNOB_UNIT_DB.id)

        x = kStr(name='x')
        y = kInt(name='y')

        fs = kFileSelector(name='fs')
        x <<= fs.get_file_name(2)
        self.assertEqual(opop(),
                         '@x := fs_get_filename(%_all_ui_ids[4],2)')
        fs.navigate(1)
        self.assertEqual(opop(),
                         'fs_navigate(%_all_ui_ids[4],1)')
        fs.base_path('my_path')
        self.assertEqual(opop(),
                         'set_control_par_str(%_all_ui_ids[4], ' +
                         '$CONTROL_PAR_BASEPATH, "my_path")')
        fs.column_width(50)
        self.assertEqual(opop(),
                         'set_control_par_str(%_all_ui_ids[4], ' +
                         '$CONTROL_PAR_COLUMN_WIDTH, 50)')
        fs.file_type(NI_FILE_TYPE_AUDIO)
        self.assertEqual(opop(),
                         'set_control_par_str(%_all_ui_ids[4], ' +
                         '$CONTROL_PAR_FILE_TYPE, $NI_FILE_TYPE_AUDIO)')

        label = kLabel()
        self.assertEqual(label.var._generate_init(),
                         ['declare ui_label $control5 (1, 1)',
                          '%_all_ui_ids[5] := get_ui_id($control5)',
                          '%_kLabel_ids[0] := %_all_ui_ids[5]'])

        lm = kLevelMeter()
        self.assertEqual(lm.var._generate_init(),
                         ['declare ui_level_meter $control6 ',
                          '%_all_ui_ids[6] := get_ui_id($control6)',
                          '%_kLevelMeter_ids[0] := %_all_ui_ids[6]'])
        lm.attach(1, 3 + NI_BUS_OFFSET)
        self.assertEqual(opop(),
                         'attach_level_meter(%_all_ui_ids[6], -1, -1,' +
                         ' 1, 3 + $NI_BUS_OFFSET)')

        menu = kMenu()
        self.assertEqual(menu.var._generate_init(),
                         ['declare ui_menu $control7 ',
                          '%_all_ui_ids[7] := get_ui_id($control7)',
                          '%_kMenu_ids[0] := %_all_ui_ids[7]'])
        menu.add_item('item one', 3)
        x <<= menu.get_item_str(0)
        self.assertEqual(opop(),
                         '@x := get_menu_item_str(%_all_ui_ids[7], 0)')
        self.assertEqual(x._get_runtime(), 'item one')
        y <<= menu.get_item_value(0)
        self.assertEqual(opop(),
                         '$y := get_menu_item_value(%_all_ui_ids[7], 0)')
        self.assertEqual(y._get_runtime(), 3)
        self.assertEqual(menu.get_item_visibility(0)._get_runtime(), 1)
        self.assertEqual(opop(),
                         'get_menu_item_visibility(%_all_ui_ids[7], 0)')
        menu.set_item_str(0, x)
        self.assertEqual(opop(),
                         'set_menu_item_str(%_all_ui_ids[7], 0, @x)')
        menu.set_item_value(0, y)
        self.assertEqual(opop(),
                         'set_menu_item_value(%_all_ui_ids[7], 0, $y)')
        menu.set_item_visibility(0, 1)
        self.assertEqual(opop(),
                         'set_menu_item_visibility(%_all_ui_ids[7], 0, 1)')

        slider = kSlider(0, 127)
        self.assertEqual(slider._generate_init(),
                         ['declare ui_slider $control8 (0, 127)',
                          '%_all_ui_ids[8] := get_ui_id($control8)',
                          '%_kSlider_ids[0] := %_all_ui_ids[8]'])

        text_edit = kTextEdit()
        self.assertEqual(text_edit._generate_init(),
                         ['declare ui_text_edit @control9 ',
                          '%_all_ui_ids[9] := get_ui_id(@control9)',
                          '%_kTextEdit_ids[0] := %_all_ui_ids[9]'])

        value_edit = kValueEdit(1, 4, VALUE_EDIT_MODE_NOTE_NAMES)
        self.assertEqual(value_edit._generate_init(),
                         ['declare ui_value_edit $control10 ' +
                          '(1, 4, $VALUE_EDIT_MODE_NOTE_NAMES)',
                          '%_all_ui_ids[10] := get_ui_id($control10)',
                          '%_kValueEdit_ids[0] := %_all_ui_ids[10]'])

        wf = kWaveForm()
        self.assertEqual(wf._generate_init(),
                         ['declare ui_waveform $control11 (1, 1)',
                          '%_all_ui_ids[11] := get_ui_id($control11)',
                          '%_kWaveForm_ids[0] := %_all_ui_ids[11]'])

        with self.assertRaises(RuntimeError):
            wf.set_property(UI_WF_PROP_PLAY_CURSOR, 1, 7)

        wf.attach_zone(3, UI_WAVEFORM_USE_SLICES | UI_WAVEFORM_USE_TABLE)
        self.assertEqual(opop(),
                         'attach_zone($control11, 3, $UI_WAVEFORM' +
                         '_USE_SLICES .or. $UI_WAVEFORM_USE_TABLE)')

        set_ui_wf_property(wf, UI_WF_PROP_PLAY_CURSOR, 2, 5)
        y <<= get_ui_wf_property(wf, UI_WF_PROP_PLAY_CURSOR, 2)
        self.assertEqual(opop(),
                         '$y := get_ui_wf_property($control11,' +
                         ' $UI_WF_PROP_PLAY_CURSOR, 2)')
        self.assertEqual(y._get_runtime(), 5)

        wf.set_property(UI_WF_PROP_PLAY_CURSOR, 1, 7)
        y <<= wf.get_property(UI_WF_PROP_PLAY_CURSOR, 1)
        self.assertEqual(opop(),
                         '$y := get_ui_wf_property($control11,' +
                         ' $UI_WF_PROP_PLAY_CURSOR, 1)')
        self.assertEqual(y._get_runtime(), 7)

        y <<= 2

        table = kTable(3, -5)
        self.assertEqual(table._generate_init(),
                         ['declare ui_table %control12 (1, 1, -5)',
                          '%_all_ui_ids[12] := get_ui_id(%control12)',
                          '%_kTable_ids[0] := %_all_ui_ids[12]'])
        self.assertEqual(table.var[2].val,
                         '%control12[2]')
        self.assertEqual(table.var[2]._get_runtime(),
                         0)
        self.assertEqual(len(table.var),
                         3)
        table.value[2] <<= 2
        self.assertEqual(table.var[2]._get_runtime(), 2)
        table.value[2] <<= 4
        self.assertEqual(opop(),
                         'set_control_par_arr(%_all_ui_ids[12], ' +
                         '$CONTROL_PAR_VALUE, 4, 2)')
        self.assertEqual(table.var[2]._get_runtime(),
                         4)
        self.assertEqual(table.value[2]._get_runtime(),
                         4)
        table2 = kTable(2, 10)
        table2.value[1] <<= 2
        self.assertEqual(table2.var[1]._get_runtime(), 2)

        with self.assertRaises(TypeError):
            kXy(3)
        xy = kXy(4)
        xy.var[0] <<= 1.1
        self.assertEqual(xy.var._get_runtime(),
                         [1.1, None, None, None])
        xy.cursor_picture[0] <<= 'pic'
        self.assertEqual(opop(),
                         'set_control_par_str_arr(%_all_ui_ids[14],' +
                         ' $CONTROL_PAR_CURSOR_PICTURE, "pic", 0)')
        xy.hide_arr[0] <<= HIDE_PART_CURSOR
        self.assertEqual(opop(),
                         'set_control_par_arr(%_all_ui_ids[14],' +
                         ' $CONTROL_PAR_HIDE, $HIDE_PART_CURSOR, 0)')

        self.val = 2
        button = kButton(name='b_with_callback')
        button.bound_callback(
            lambda control: self.callback(control, 3))
        self.assertEqual(button.text._get_runtime(), '5')

    # @t.skip
    def callback(self, control, value):
        control.text <<= str(self.val + value)

    # @t.skip
    def test_generation(self):
        KSP.set_compiled(True)
        # self.maxDiff = None
        current = list()
        Output().set(current)
        button1 = kButton(name='button1')
        self.assertIsInstance(button1.var, KspVar)
        button1.x <<= 100
        button1.y <<= 20
        button1.width <<= 10
        button1.height <<= 40
        button2 = kButton(name='button2')
        button2.x <<= 200
        button2.y <<= 6
        button2.width <<= 40
        button2.height <<= 10
        button2.text <<= 'simple text'

        switch = kSwitch(name='switch')
        switch.y <<= 9
        button2.x <<= 10
        Output().release()
        init = list()
        init.append('on init')
        init.extend(KspObject.generate_all_inits())
        init.extend(KspNativeControlMeta.generate_init_code())
        init.extend(current)
        init.append('end on')
        self.assertEqual(unpack_lines(init), init_lines)


init_lines = '''on init
declare %_kButton_ids[2]
declare %_all_ui_ids[3]
declare ui_button $button1 
%_all_ui_ids[0] := get_ui_id($button1)
%_kButton_ids[0] := %_all_ui_ids[0]
declare ui_button $button2 
%_all_ui_ids[1] := get_ui_id($button2)
%_kButton_ids[1] := %_all_ui_ids[1]
declare %_kSwitch_ids[1]
declare ui_switch $switch 
%_all_ui_ids[2] := get_ui_id($switch)
%_kSwitch_ids[0] := %_all_ui_ids[2]
declare %_all_x_params[3] := (100, 200, -1)
declare %_all_y_params[3] := (20, 6, 9)
declare %_all_width_params[3] := (10, 40, -1)
declare %_all_height_params[3] := (40, 10, -1)
declare $_for_loop_curr_idx := -1
declare %_for_loop_idx[20]
inc($_for_loop_curr_idx)
%_for_loop_idx[$_for_loop_curr_idx] := 0
while(%_for_loop_idx[$_for_loop_curr_idx] < 3)
if(%_all_x_params[%_for_loop_idx[$_for_loop_curr_idx]] # -1)
set_control_par(%_all_ui_ids[%_for_loop_idx[$_for_loop_curr_idx]], \
$CONTROL_PAR_POS_X, %_all_x_params[%_for_loop_idx[$_for_loop_curr_idx]])
end if
if(%_all_y_params[%_for_loop_idx[$_for_loop_curr_idx]] # -1)
set_control_par(%_all_ui_ids[%_for_loop_idx[$_for_loop_curr_idx]], \
$CONTROL_PAR_POS_Y, %_all_y_params[%_for_loop_idx[$_for_loop_curr_idx]])
end if
if(%_all_width_params[%_for_loop_idx[$_for_loop_curr_idx]] # -1)
set_control_par(%_all_ui_ids[%_for_loop_idx[$_for_loop_curr_idx]], \
$CONTROL_PAR_WIDTH, %_all_width_params[%_for_loop_idx[\
$_for_loop_curr_idx]])
end if
if(%_all_height_params[%_for_loop_idx[$_for_loop_curr_idx]] # -1)
set_control_par(%_all_ui_ids[%_for_loop_idx[$_for_loop_curr_idx]], \
$CONTROL_PAR_HEIGHT, %_all_height_params[%_for_loop_idx[\
$_for_loop_curr_idx]])
end if
%_for_loop_idx[$_for_loop_curr_idx] := %_for_loop_idx[\
$_for_loop_curr_idx] + 1
end while
dec($_for_loop_curr_idx)
set_control_par_str(%_all_ui_ids[1], $CONTROL_PAR_TEXT, "simple text")
set_control_par(%_all_ui_ids[1], $CONTROL_PAR_POS_X, 10)
end on'''


if __name__ == '__main__':
    t.main()
