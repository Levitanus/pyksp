import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from script import kScript
from bi_ui_controls import kButton
from bi_ui_controls import kSlider
from bi_ui_controls import kLabel
from bi_ui_controls import kLevelMeter
from bi_ui_controls import kWidget
from bi_ui_controls import kMainWindow
from bi_ui_controls import set_control_par_str
from bi_ui_controls import set_control_par

from bi_notes_events import EVENT_NOTE
from bi_misc import kLog
from bi_misc import logpr

from conditions_loops import For

from k_built_ins import message
from callbacks import note
from callbacks import init
from functions import func
from functions import kArg

from dev_tools import print_lines


@note
def note_cb():
    message(EVENT_NOTE)


@init
def null_msg():
    message('')


class TestScript(DevTest):

    @func
    def switch(self, ids: kArg(int, 6), on_id: int):
        with For(arr=ids) as seq:
            for item in seq:
                logpr(item)
                set_control_par(item, 'value', 0)
        set_control_par(on_id, 'value', 1)
        return

    def runTest(self):
        script = kScript('file', 'myscript')
        with self.assertRaises(RuntimeError):
            script._generate_code()

        def foo():
            kLog(kLog.array,
                 path='E:\packages\pyksp\LogFileReader-master/mylog.nka')
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

        print_lines(script._generate_code(), title='THE WHOLE CODE')


if __name__ == '__main__':
    t.main()
