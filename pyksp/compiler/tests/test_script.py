import os
import sys
import unittest as t
import time

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from script import kScript
from bi_ui_controls import kButton
from bi_ui_controls import kLabel
from bi_ui_controls import kLevelMeter
from bi_ui_controls import kWidget
from bi_ui_controls import kMainWindow
from bi_ui_controls import set_control_par_str
from bi_ui_controls import set_control_par
from bi_ui_controls import get_control_par

from bi_notes_events import EVENT_NOTE
from bi_misc import kLog
from bi_misc import logpr

from conditions_loops import For
from conditions_loops import If
from conditions_loops import check

from functions import Function

from k_built_ins import message
from callbacks import note
from callbacks import init
from functions import func
from functions import kArg

from dev_tools import unpack_lines


@note
def note_cb():
    message(EVENT_NOTE)


@init
def null_msg():
    message('')


@t.skip('callbacks are generated poor, needs fix to be passed in the' +
        'package test runner. works for file-test')
class TestScript(DevTest):

    @func
    def switch(self, ids: kArg(int, 6), on_id: int):
        with For(arr=ids) as seq:
            for item in seq:
                logpr(item)
                with If((item != on_id) &
                        (get_control_par(on_id, 'value') == 1)):
                    check()
                    set_control_par(item, 'value', 0)
        with If(get_control_par(on_id, 'value') != 1):
            check()
            set_control_par(on_id, 'value', 1)
        return

    def runTest(self):
        script = kScript(r'E:\packages\file.txt',
                         'myscript', max_line_length=70, compact=True)
        with self.assertRaises(RuntimeError):
            script._generate_code()

        def foo():
            kLog(kLog.array,
                 path=r'E:\packages\pyksp\LogFileReader-master/mylog.nka')
            mw = kMainWindow()
            buttons_area = kWidget(parent=mw)
            buttons_area.place_pct(20, 10, 50, 80)
            ba_bg = kLabel(parent=buttons_area)
            ba_bg.pack(sticky='nswe')
            ba_bg.text <<= ''
            lvl = kLevelMeter(parent=ba_bg, width=20)
            lvl.pack(sticky='nse')
            buttons_area.add_grid(3, 2, 20, 20, 20, 20)
            buttons = [kButton(parent=buttons_area) for b in range(3 * 2)]

            def b_callback(control):
                self.switch(kButton.ids, control.id)
                message(control.id)
            for idx, b in enumerate(buttons):
                b.grid(idx % 3, idx // 3)
                b.bound_callback(b_callback)
            with For(arr=kButton.ids) as seq:
                for item in seq:
                    set_control_par_str(item, 'text', 'mybutton')

        script.main = foo
        localtime = time.asctime(time.localtime(time.time()))
        init_line = '{ Compiled on %s }' % localtime
        self.maxDiff = None
        self.assertEqual(unpack_lines(script._generate_code()),
                         generated_code.format(
            init_line=init_line,
            fname=Function.get_func_name(self.switch)))


generated_code = \
    '''{init_line}
on init
set_script_title("myscript")
declare %_stack_functions_int_arr[32000]
declare %_stack_functions_int_idx[100]
declare $_stack_functions_int_pointer := -1
declare !_stack_functions_str_arr[32000]
declare %_stack_functions_str_idx[100]
declare $_stack_functions_str_pointer := -1
declare ?_stack_functions_real_arr[32000]
declare %_stack_functions_real_idx[100]
declare $_stack_functions_real_pointer := -1
declare !yxymb[32768]
declare $pl0vy
declare $ivrko
declare %mt5kw[1]
declare %x1ds3[8]
declare ui_label $z1sjh (1, 1)
%x1ds3[0] := get_ui_id($z1sjh)
%mt5kw[0] := %x1ds3[0]
declare %o4lym[1]
declare ui_level_meter $yzhan
%x1ds3[1] := get_ui_id($yzhan)
%o4lym[0] := %x1ds3[1]
declare %1lv3c[6]
declare ui_button $gxxjf
%x1ds3[2] := get_ui_id($gxxjf)
%1lv3c[0] := %x1ds3[2]
declare ui_button $4z4fx
%x1ds3[3] := get_ui_id($4z4fx)
%1lv3c[1] := %x1ds3[3]
declare ui_button $rl1hr
%x1ds3[4] := get_ui_id($rl1hr)
%1lv3c[2] := %x1ds3[4]
declare ui_button $cterv
%x1ds3[5] := get_ui_id($cterv)
%1lv3c[3] := %x1ds3[5]
declare ui_button $433nn
%x1ds3[6] := get_ui_id($433nn)
%1lv3c[4] := %x1ds3[6]
declare ui_button $bl3fc
%x1ds3[7] := get_ui_id($bl3fc)
%1lv3c[5] := %x1ds3[7]
declare $f03kw := -1
declare %fgbt2[20]
declare %ykjpa[8] := (126, 422, 146, 238, 330, 146, 238, 330)
declare %cyzc1[8] := (10, 10, 30, 30, 30, 50, 50, 50)
declare %jm2mx[8] := (316, 20, 92, 92, 92, 92, 92, 92)
declare %rismq[8] := (80, 80, 20, 20, 20, 20, 20, 20)
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 8)
if(%ykjpa[%fgbt2[$f03kw]] # -1)
set_control_par(%x1ds3[%fgbt2[$f03kw]], $CONTROL_PAR_POS_X,...
    %ykjpa[%fgbt2[$f03kw]])
end if
if(%cyzc1[%fgbt2[$f03kw]] # -1)
set_control_par(%x1ds3[%fgbt2[$f03kw]], $CONTROL_PAR_POS_Y,...
    %cyzc1[%fgbt2[$f03kw]])
end if
if(%jm2mx[%fgbt2[$f03kw]] # -1)
set_control_par(%x1ds3[%fgbt2[$f03kw]], $CONTROL_PAR_WIDTH,...
    %jm2mx[%fgbt2[$f03kw]])
end if
if(%rismq[%fgbt2[$f03kw]] # -1)
set_control_par(%x1ds3[%fgbt2[$f03kw]], $CONTROL_PAR_HEIGHT,...
    %rismq[%fgbt2[$f03kw]])
end if
%fgbt2[$f03kw] := %fgbt2[$f03kw] + 1
end while
dec($f03kw)
set_control_par($INST_ICON_ID,$CONTROL_PAR_HIDE,$HIDE_WHOLE_CONTROL)
set_ui_width_px(633)
set_ui_height_px(100)
set_control_par_str(%x1ds3[0], $CONTROL_PAR_TEXT, "")
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
set_control_par_str(%1lv3c[%fgbt2[$f03kw]], $CONTROL_PAR_TEXT, "mybutton")
inc(%fgbt2[$f03kw])
end while
dec($f03kw)
message("")
end on
function {fname}
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
!yxymb[$pl0vy] := %_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])]
$pl0vy := ($pl0vy + 1) mod 32768
if((%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])] #...
    %_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]]) and...
    (get_control_par(%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]],...
    $CONTROL_PAR_VALUE) = 1))
set_control_par(%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])],...
    $CONTROL_PAR_VALUE, 0)
end if
inc(%fgbt2[$f03kw])
end while
dec($f03kw)
if(get_control_par(%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]],...
    $CONTROL_PAR_VALUE) # 1)
set_control_par(%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]],...
    $CONTROL_PAR_VALUE, 1)
end if
end function

on note
message($EVENT_NOTE)
end on
on persistence_changed
while(1=1)
if($ivrko # $pl0vy)
save_array_str(!yxymb, "E:/packages/pyksp/LogFileReader-master/mylog.nka")
end if
$ivrko := $pl0vy
wait(200000)
end while
end on
on ui_control($gxxjf)
inc($_stack_functions_int_pointer)
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])] :=...
    %1lv3c[%fgbt2[$f03kw]]
%fgbt2[$f03kw] := %fgbt2[$f03kw] + 1
end while
dec($f03kw)
%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]] :=...
    %x1ds3[2]
call {fname}
dec($_stack_functions_int_pointer)
message(%x1ds3[2])
end on
on ui_control($4z4fx)
inc($_stack_functions_int_pointer)
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])] :=...
    %1lv3c[%fgbt2[$f03kw]]
%fgbt2[$f03kw] := %fgbt2[$f03kw] + 1
end while
dec($f03kw)
%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]] :=...
    %x1ds3[3]
call {fname}
dec($_stack_functions_int_pointer)
message(%x1ds3[3])
end on
on ui_control($rl1hr)
inc($_stack_functions_int_pointer)
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])] :=...
    %1lv3c[%fgbt2[$f03kw]]
%fgbt2[$f03kw] := %fgbt2[$f03kw] + 1
end while
dec($f03kw)
%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]] :=...
    %x1ds3[4]
call {fname}
dec($_stack_functions_int_pointer)
message(%x1ds3[4])
end on
on ui_control($cterv)
inc($_stack_functions_int_pointer)
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])] :=...
    %1lv3c[%fgbt2[$f03kw]]
%fgbt2[$f03kw] := %fgbt2[$f03kw] + 1
end while
dec($f03kw)
%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]] :=...
    %x1ds3[5]
call {fname}
dec($_stack_functions_int_pointer)
message(%x1ds3[5])
end on
on ui_control($433nn)
inc($_stack_functions_int_pointer)
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])] :=...
    %1lv3c[%fgbt2[$f03kw]]
%fgbt2[$f03kw] := %fgbt2[$f03kw] + 1
end while
dec($f03kw)
%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]] :=...
    %x1ds3[6]
call {fname}
dec($_stack_functions_int_pointer)
message(%x1ds3[6])
end on
on ui_control($bl3fc)
inc($_stack_functions_int_pointer)
inc($f03kw)
%fgbt2[$f03kw] := 0
while(%fgbt2[$f03kw] < 6)
%_stack_functions_int_arr[%fgbt2[$f03kw] + (0 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer])] :=...
    %1lv3c[%fgbt2[$f03kw]]
%fgbt2[$f03kw] := %fgbt2[$f03kw] + 1
end while
dec($f03kw)
%_stack_functions_int_arr[6 +...
    %_stack_functions_int_idx[$_stack_functions_int_pointer]] :=...
    %x1ds3[7]
call {fname}
dec($_stack_functions_int_pointer)
message(%x1ds3[7])
end on'''

if __name__ == '__main__':
    t.main()
