import os
import sys
import unittest as t

path = os.path.abspath(os.path.dirname(__file__)) + '/..'
sys.path.append(path)
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from mytests import DevTest

from abstract import Output

from dev_tools import unpack_lines

from bi_ui_controls import *
# from pyksp.compiler2.bi_ui_controls import CONTROL_PAR_POS_X

null_lines = \
    '''set_control_par($INST_ICON_ID,$CONTROL_PAR_HIDE,\
$HIDE_WHOLE_CONTROL)
set_ui_width_px(633)
set_ui_height_px(100)'''

packed_lines = \
    '''set_control_par_str($INST_WALLPAPER_ID,\
$CONTROL_PAR_PICTURE,wallpaper)
set_control_par_str($INST_ICON_ID,$CONTROL_PAR_PICTURE,icon)
set_ui_width_px(800)
set_ui_height_px(300)'''


class TestMainWindow(DevTest):

    def runTest(self):
        kMainWindow()
        self.assertEqual(unpack_lines(Output().get()), null_lines)
        Output().refresh()
        w = kMainWindow(width=800, height=300,
                        wallpaper='wallpaper', icon='icon')
        self.assertEqual(unpack_lines(Output().get()), packed_lines)
        self.assertEqual(w.x, 0)
        self.assertEqual(w.y, 0)
        self.assertEqual(w.width, 800)
        self.assertEqual(w.height, 300)
        with self.assertRaises(AttributeError):
            kMainWindow(width=630)


# @t.skip
class TestWidgetGrid(DevTest):

    def runTest(self):
        w = kMainWindow()
        simple = WidgetGrid(w, 2, 3)
        ceil_0_0 = simple.get_ceil(0, 0)
        self.assertEqual(ceil_0_0[0], 0)
        self.assertEqual(ceil_0_0[1], 0)
        self.assertEqual(ceil_0_0[2], 633 / 2)
        self.assertEqual(ceil_0_0[3], 100 / 3)
        ceil_1_0 = simple.get_ceil(1, 0)
        self.assertEqual(ceil_1_0[0], 633 / 2)
        self.assertEqual(ceil_1_0[1], 0)
        self.assertEqual(ceil_1_0[2], 633)
        self.assertEqual(ceil_1_0[3], 100 / 3)
        ceil_1_1 = simple.get_ceil(1, 1)
        self.assertEqual(ceil_1_1[0], 633 / 2)
        self.assertEqual(ceil_1_1[1], 100 / 3)
        self.assertEqual(ceil_1_1[2], 633)
        self.assertEqual(ceil_1_1[3], 100 / 3 * 2)

        offset = WidgetGrid(w, 2, 3, 5, 5, 5, 5)
        ceil_0_0 = offset.get_ceil(0, 0)
        self.assertEqual(ceil_0_0[0], 5)
        self.assertEqual(ceil_0_0[1], 5)
        self.assertEqual(ceil_0_0[2], 623 / 2 + 5)
        self.assertEqual(ceil_0_0[3], 90 / 3 + 5)
        ceil_1_1 = offset.get_ceil(1, 1)
        self.assertEqual(ceil_1_1[0], 623 / 2 + 5)
        self.assertEqual(ceil_1_1[1], 90 / 3 + 5)
        self.assertEqual(ceil_1_1[2], 623 + 5)
        self.assertEqual(ceil_1_1[3], 90 / 3 * 2 + 5)


# @t.skip
class TestWidget(DevTest):

    def setUp(self):
        super().setUp()
        self.mw = kMainWindow()
        mw = self.mw
        self.root = kWidget(mw, mw.x, mw.y, mw.width, mw.height)
        self.root.add_grid(2, 3, 5, 5, 5, 5)

    def test_widgets(self):
        w = kWidget()
        with self.assertRaises(kParVarGetError):
            w.x.val
        with self.assertRaises(kParVarGetError):
            w.y.val
        with self.assertRaises(kParVarGetError):
            w.width.val
        with self.assertRaises(kParVarGetError):
            w.height.val
        with self.assertRaises(RuntimeError):
            w.pack()
        with self.assertRaises(RuntimeError):
            w.grid(0, 0)
        with self.assertRaises(RuntimeError):
            w.place()
        with self.assertRaises(kParVarGetError):
            w.add_grid()

        y_sh = 5
        w.x <<= 0
        w.y <<= y_sh
        w.width <<= 100
        w.height <<= 100

        w.add_grid(10, y_sh)

        ch_packed = kWidget(w)
        ch_packed.pack('nswe')
        self.assertEqual(ch_packed.x, 0)
        self.assertEqual(ch_packed.y, y_sh)
        self.assertEqual(ch_packed.width, 100)
        self.assertEqual(ch_packed.height, 100)

        ch_packed.width, ch_packed.height = 50, 50
        ch_packed.pack('ne')
        self.assertEqual(ch_packed.x, 50)
        self.assertEqual(ch_packed.y, y_sh)
        self.assertEqual(ch_packed.width, 50)
        self.assertEqual(ch_packed.height, 50)

        ch_grid = kWidget(w)
        ch_grid.grid(0, 0)
        self.assertEqual(ch_grid.x, 0)
        self.assertEqual(ch_grid.y, y_sh)
        self.assertEqual(ch_grid.width, 10)
        self.assertEqual(ch_grid.height, 20)
        ch_grid.grid(2, 3)
        self.assertEqual(ch_grid.x, 20)
        self.assertEqual(ch_grid.y, 60 + y_sh)
        self.assertEqual(ch_grid.width, 10)
        self.assertEqual(ch_grid.height, 20)

        ch_grid.grid(2, 1, 2, 1, 1, 2, 3, 4)
        self.assertEqual(ch_grid.x, 23)
        self.assertEqual(ch_grid.y, 21 + y_sh)
        self.assertEqual(ch_grid.width, 13)
        self.assertEqual(ch_grid.height, 17)

        w.x, w.y, w.width, w.height = 0, y_sh, 200, 200

        ch_placed = kWidget(w)
        ch_placed.place(5, 10, 15, 20)
        self.assertEqual(ch_placed.x, 5)
        self.assertEqual(ch_placed.y, 10 + y_sh)
        self.assertEqual(ch_placed.width, 15)
        self.assertEqual(ch_placed.height, 20)

        ch_placed.place(5, 10, width_pct=50, height_pct=25)
        self.assertEqual(ch_placed.x, 5)
        self.assertEqual(ch_placed.y, 10 + y_sh)
        self.assertEqual(ch_placed.width, 100)
        self.assertEqual(ch_placed.height, 50)

        ch_placed.place(x_pct=5, y_pct=10, width=50, height=25)
        self.assertEqual(ch_placed.x, 10)
        self.assertEqual(ch_placed.y, 20 + y_sh)
        self.assertEqual(ch_placed.width, 50)
        self.assertEqual(ch_placed.height, 25)

        with self.assertRaises(RuntimeError):
            ch_placed.place(100, 0, 101, 10)
        with self.assertRaises(RuntimeError):
            ch_placed.place(0, 100, 10, 101)
        with self.assertRaises(AttributeError):
            ch_placed.place(1, 1, 1, 1, 1)

        ch_placed.place_pct(5, 10, 50, 25)
        self.assertEqual(ch_placed.x, 10)
        self.assertEqual(ch_placed.y, 20 + y_sh)
        self.assertEqual(ch_placed.width, 100)
        self.assertEqual(ch_placed.height, 50)

        button = kButton(parent=ch_placed)
        button.pack(sticky='ns')
        self.assertEqual(button.x.val, 12)
        self.assertEqual(button.y.val, 25)
        self.assertEqual(button.width.val, 85)
        self.assertEqual(button.height.val, 50)


if __name__ == '__main__':
    t.main()
