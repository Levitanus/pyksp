from typing import Optional
from typing import Type
from typing import Union
from typing import Iterable
from typing import Any
from typing import Callable

from collections import OrderedDict

from functools import wraps

from abc import abstractmethod
from abc import ABCMeta

from abstract import KSP
from abstract import Output

from base_types import KspVar
from base_types import KspIntVar
from base_types import KspStrVar
from base_types import KspRealVar
from base_types import AstBase

from k_built_ins import BuiltInFunc
from k_built_ins import BuiltInFuncInt
from k_built_ins import BuiltInFuncStr
from k_built_ins import BuiltInIntVar
from k_built_ins import ListenerCallback
from k_built_ins import UiControlCallback
from k_built_ins import get_runtime_val
from k_built_ins import all_callbacks

from native_types import kInt
from native_types import kStr
from native_types import kReal
from native_types import kArrInt
from native_types import kArrStr
from native_types import kArrReal
from native_types import kNone

from base_types import KspArray

from dev_tools import WrapProp

# from gui_system import WidgetMeta


# from conditions_loops import For
# from conditions_loops import If
# from conditions_loops import check

# from gui_system import kWidget
# from gui_system import kMainWindow


class kParVarGetError(Exception):

    def __init__(self, name):
        super().__init__(f'par {name} is not set')


class kMainWindow(KSP):
    '''can be used as parent of widgets,
    sets ui_height_px and ui_width_px.
    Within icon being set to None – hides it'''

    def __init__(self, width: int=633, height: int=100,
                 wallpaper: str=None, icon: str=None,
                 skin_offset: int=None):
        if width < 633:
            raise AttributeError('width can be not less than 633 px')
        self._width = width
        self._height = height
        if wallpaper:
            Output().put(
                'set_control_par_str($INST_WALLPAPER_ID,' +
                f'$CONTROL_PAR_PICTURE,{wallpaper})')
        if icon:
            Output().put(
                'set_control_par_str($INST_ICON_ID,' +
                f'$CONTROL_PAR_PICTURE,{icon})')
        else:
            Output().put(
                'set_control_par($INST_ICON_ID,' +
                '$CONTROL_PAR_HIDE,$HIDE_WHOLE_CONTROL)')
        self._skin_offset = 0
        if skin_offset is not None:
            self._skin_offset = skin_offset
            Output().put(f'set_skin_offset({skin_offset})')
        Output().put(f'set_ui_width_px({width})')
        Output().put(f'set_ui_height_px({height})')
        self._childs = list()

    @property
    def skin_offset(self):
        return self._skin_offset

    @property
    def x(self):
        return 0

    @property
    def y(self):
        return 0

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class WidgetPar(kInt):
    '''WidgetPar doc'''

    def __init__(self, name: str, value: Optional[int]=None):
        super().__init__(value=None, is_local=True)
        self._name = name
        self._val = value

    def _set_compiled(self, val):
        self._val = val

    def _set_runtime(self, val):
        self._val = val

    def _get_compiled(self):
        if self._val is None:
            raise kParVarGetError(self._name)
        val = self._val
        if hasattr(val, '_get_compiled'):
            val = val._get_compiled()
        if hasattr(val, 'expand'):
            val = val.expand()
        return self._val

    def _get_runtime(self):
        if self._val is None:
            raise kParVarGetError(self._name)
        return get_runtime_val(self._val)

    # def __truediv__(self, other)


class WidgetGrid(KSP):
    '''stores ceils x, y, width, height
    returns them by get_ceil(column, row)'''

    def __init__(self, obj, columns: int=1, rows: int=1,
                 top_offset: int=0, bottom_offset: int=0,
                 left_offset: int=0, right_offset: int=0):
        self._obj = obj
        self._columns_am = columns
        self._rows_am = rows
        # print(obj.x, left_offset)
        self._x = obj.x + left_offset
        self._y = obj.y + top_offset
        self._w = obj.width - left_offset - right_offset
        self._h = obj.height - top_offset - bottom_offset
        self._ceil_w = self._w / columns
        self._ceil_h = self._h / rows
        self._ceils = self._make_ceils(columns, rows)

    def _make_ceils(self, columns, rows):
        '''returns list of dicts size colums*rows with keys "x", "y"'''
        out = [None] * columns * rows
        c_w = self._ceil_w
        c_h = self._ceil_h
        for h_i in range(rows):
            for w_i in range(columns):
                ceil = dict()
                ceil['x'] = self._x + (w_i * c_w)
                ceil['y'] = self._y + (h_i * c_h)
                idx = self._get_idx_from_matrix(w_i, h_i)
                out[idx] = ceil
        return out

    def _get_idx_from_matrix(self, column, row):
        return (row * self._columns_am) + column

    def get_ceil(self, column, row):
        '''returns pixels of left, right, top, bottom sides of ceil'''
        idx = self._get_idx_from_matrix(column, row)
        c = self._ceils[idx]
        left, top, right, bottom = c['x'], c['y'], \
            c['x'] + self._ceil_w, c['y'] + self._ceil_h
        return left, top, right, bottom


class WidgetMeta(ABCMeta):

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        if obj._parent:
            obj._parent._childs.append(obj)
        return obj


class kWidget(metaclass=WidgetMeta):
    '''base class for all KSP widgets, including built-ins like
    kButton or kLabel (ui_button & ui_label). Behaves like tkinter Frame.
    Can be parented by kMainWindow or another kWidget instances'''

    def __init__(self, parent: object=None, x: int=None, y: int=None,
                 width: int=None, height: int=None):
        if not isinstance(parent, (kWidget, kMainWindow)) and\
                parent is not None:
            raise TypeError('parent can be only instance of types' +
                            f'{(kWidget, kMainWindow)}')
        self._parent = parent
        self._childs = list()
        self._grid = None
        if isinstance(self, KspNativeControl):
            return
        self.x = WidgetPar('x', x)
        self.y = WidgetPar('y', y)
        self.width = WidgetPar('width', width)
        self.height = WidgetPar('height', height)

    @property
    def childs(self):
        return self._childs

    def pack(self, sticky: str=''):
        '''puts widget in the borders of parent.
        sticky can cosists of 'nswe'.
        with one side selected places border of widget to the side.
        with 'ne', 'nw', 'se', 'sw' places widget to the corner
        with 'ns', 'we', 'nswe', and similar combinations stretches
            widget to borders of parent'''
        if not self._parent:
            raise RuntimeError('has to be set to parent')

        p_x = self._parent.x
        p_y = self._parent.y
        p_w = self._parent.width
        p_h = self._parent.height

        def get_self_par(par, def_par):
            out = par
            try:
                par.val
            except kParVarGetError as e:
                if hasattr(self, def_par):
                    out = getattr(self, def_par)
                    par <<= out
                else:
                    raise e
            except AttributeError:
                return out
            return out

        def s_w():
            return get_self_par(self.width, '_def_width')

        def s_h():
            return get_self_par(self.height, '_def_height')

        def center_w():
            out = ((p_x + p_w) / 2) - (s_w() / 2)
            if isinstance(out, float):
                out = int(out)
            return out

        def center_h():
            out = ((p_y + p_h) / 2) - (s_h() / 2)
            if isinstance(out, float):
                out = int(out)
            return out

        if 'e' in sticky:
            if 'w' in sticky:
                self.width <<= p_w
            else:
                self.x <<= p_x + p_w - s_w()
        if 's' in sticky:
            if 'n' in sticky:
                self.height <<= p_h
            else:
                self.y <<= p_y + p_h - s_h()
        if 'w' in sticky:
            self.x <<= p_x
        if 'n' in sticky:
            self.y <<= p_y
        if 's' not in sticky and 'n' not in sticky:
            self.y <<= center_h()
        if 'e' not in sticky and 'w' not in sticky:
            self.x <<= center_w()

    def add_grid(self, columns: int=1, rows: int=1,
                 top_offset: int=0, bottom_offset: int=0,
                 left_offset: int=0, right_offset: int=0):
        '''add grid to the widget'''
        if not KSP.in_init():
            raise RuntimeError('can be used only in init')
        self._grid = WidgetGrid(self, columns, rows,
                                top_offset, bottom_offset,
                                left_offset, right_offset)

    def grid(self, column: int, row: int,
             columnspan: int=1, rowspan: int=1,
             top_offset: int=0, bottom_offset: int=0,
             left_offset: int=0, right_offset: int=0):
        '''similar to tkinter grid method:
        places object to the grid ceil (zerobased) or ceils if
        columnspan or rowspan are used'''
        if not self._parent:
            raise RuntimeError('has to be set to parent')
        l, t, r, b = [int(i) for i in self._parent._grid.get_ceil(
            column, row)]

        self.x <<= l + left_offset
        self.y <<= t + top_offset
        self.width <<= ((r - l) * columnspan) - left_offset - right_offset
        self.height <<= ((b - t) * rowspan) - top_offset - bottom_offset

    def place(self, x: int=None, y: int=0,
              width: int=None, height: int=None,
              x_pct: int=None, y_pct: int=0,
              width_pct: int=None, height_pct: int=None):
        '''place widget depends on parent position
        x, y, width, height are counted in pixels
        x_pct, y_pct, width_pct, height_pct – in percents
        '''
        if not self._parent:
            raise RuntimeError('has to be set to parent')
        if x and x_pct:
            raise AttributeError(
                'can assign only "x" or "x_pct"')
        if y and y_pct:
            raise AttributeError(
                'can assign only "y" or "y_pct"')
        if width and width_pct:
            raise AttributeError(
                'can assign only "width" or "width_pct"')
        if height and height_pct:
            raise AttributeError(
                'can assign only "height" or "height_pct"')

        if x:
            self.x <<= self._parent.x + x
        if y:
            self.y <<= self._parent.y + y
        if width:
            self.width <<= width
        if height:
            self.height <<= height

        if x_pct:
            if x_pct < 0 or x_pct > 100:
                raise AttributeError(
                    'x_pct has to be between 0 and 100')
            self.x <<= int(self._parent.x +
                           (self._parent.width * x_pct / 100))
        if y_pct:
            if y_pct < 0 or y_pct > 100:
                raise AttributeError(
                    'y_pct has to be between 0 and 100')
            self.y <<= int(self._parent.y +
                           (self._parent.height * y_pct / 100))
        if width_pct:
            if width_pct < 0 or width_pct > 100:
                raise AttributeError(
                    'width_pct has to be between 0 and 100')
            self.width <<= int(self._parent.width * width_pct / 100)
        if height_pct:
            if height_pct < 0 or height_pct > 100:
                raise AttributeError(
                    'height_pct has to be between 0 and 100')
            self.height <<= int(self._parent.width * height_pct / 100)

        if self.x + self.width > self._parent.x + self._parent.width:
            raise RuntimeError(
                f'the right side of control ({x + self.width}px) out of ' +
                f'bounds of parent {self._parent.x + self._parent.width}')
        if self.y + self.height > self._parent.y + self._parent.height:
            raise RuntimeError(
                f'the right side of control {y + self.height} out of ' +
                f'bounds of parent {self._parent.y + self._parent.height}')

    def place_pct(self, x: int=None, y: int=None,
                  width: int=None, height: int=None):
        '''the same as place(), but all arguments are in percents'''
        self.place(x_pct=x, y_pct=y,
                   width_pct=width, height_pct=height)


class bControlParVar(BuiltInIntVar):

    def __init__(self, name: str, short: str,
                 callbacks=all_callbacks):
        super().__init__(name, callbacks=callbacks)
        self._attr = short


class bControlParIntVar(bControlParVar, BuiltInIntVar):
    pass


class bControlParStrVar(bControlParVar, BuiltInIntVar):
    pass


class bControlParConst(BuiltInIntVar):

    def __init__(self, name, callbacks=all_callbacks):
        super().__init__(name, callbacks=all_callbacks)
        self._value = self._id


class bKnobUnitConst(bControlParConst):
    pass


KNOB_UNIT_NONE = bKnobUnitConst('KNOB_UNIT_NONE')
KNOB_UNIT_DB = bKnobUnitConst('KNOB_UNIT_DB')
KNOB_UNIT_HZ = bKnobUnitConst('KNOB_UNIT_HZ')
KNOB_UNIT_PERCENT = bKnobUnitConst('KNOB_UNIT_PERCENT')
KNOB_UNIT_MS = bKnobUnitConst('KNOB_UNIT_MS')
KNOB_UNIT_ST = bKnobUnitConst('KNOB_UNIT_ST')
KNOB_UNIT_OCT = bKnobUnitConst('KNOB_UNIT_OCT')


CONTROL_PAR_NONE =\
    bControlParIntVar('CONTROL_PAR_NONE', 'none')
CONTROL_PAR_HELP =\
    bControlParStrVar('CONTROL_PAR_HELP', 'help')
CONTROL_PAR_POS_X =\
    bControlParIntVar('CONTROL_PAR_POS_X', 'x')
CONTROL_PAR_POS_Y =\
    bControlParIntVar('CONTROL_PAR_POS_Y', 'y')
CONTROL_PAR_GRID_X =\
    bControlParIntVar('CONTROL_PAR_GRID_X', 'grid_x')
CONTROL_PAR_GRID_Y =\
    bControlParIntVar('CONTROL_PAR_GRID_Y', 'grid_y')
CONTROL_PAR_WIDTH =\
    bControlParIntVar('CONTROL_PAR_WIDTH', 'width')
CONTROL_PAR_HEIGHT =\
    bControlParIntVar('CONTROL_PAR_HEIGHT', 'height')
CONTROL_PAR_GRID_WIDTH =\
    bControlParIntVar('CONTROL_PAR_GRID_WIDTH', 'grid_width')
CONTROL_PAR_GRID_HEIGHT =\
    bControlParIntVar('CONTROL_PAR_GRID_HEIGHT', 'grid_height')
CONTROL_PAR_HIDE =\
    bControlParIntVar('CONTROL_PAR_HIDE', 'hide')
CONTROL_PAR_BG_COLOR =\
    bControlParIntVar('CONTROL_PAR_BG_COLOR', 'bg_color')


class bControlHideConst(bControlParConst):
    pass


HIDE_PART_BG = bControlHideConst('HIDE_PART_BG')
HIDE_PART_VALUE = bControlHideConst('HIDE_PART_VALUE')
HIDE_PART_TITLE = bControlHideConst('HIDE_PART_TITLE')
HIDE_PART_MOD_LIGHT = bControlHideConst('HIDE_PART_MOD_LIGHT')
HIDE_PART_NOTHING = bControlHideConst('HIDE_PART_NOTHING')
HIDE_WHOLE_CONTROL = bControlHideConst('HIDE_WHOLE_CONTROL')
HIDE_PART_CURSOR = bControlHideConst('HIDE_PART_CURSOR')

CONTROL_PAR_PICTURE = bControlParStrVar('CONTROL_PAR_PICTURE',
                                        'picture')
CONTROL_PAR_PICTURE_STATE = bControlParIntVar('CONTROL_PAR_PICTURE_STATE',
                                              'picture_state')
CONTROL_PAR_Z_LAYER = bControlParIntVar('CONTROL_PAR_Z_LAYER',
                                        'z_layer')
CONTROL_PAR_VALUE = bControlParIntVar('CONTROL_PAR_VALUE',
                                      'value')
CONTROL_PAR_DEFAULT_VALUE = bControlParIntVar(
    'CONTROL_PAR_DEFAULT_VALUE', 'default')
CONTROL_PAR_TEXT = bControlParStrVar('CONTROL_PAR_TEXT',
                                     'text')
CONTROL_PAR_TEXTLINE = bControlParStrVar('CONTROL_PAR_TEXTLINE',
                                         'textline')
CONTROL_PAR_LABEL = bControlParStrVar('CONTROL_PAR_LABEL',
                                      'label')
CONTROL_PAR_UNIT = bControlParStrVar('CONTROL_PAR_UNIT',
                                     'unit')


class bKnobUnitConst(bControlParConst):
    pass


KNOB_UNIT_NONE = bKnobUnitConst('KNOB_UNIT_NONE')
KNOB_UNIT_DB = bKnobUnitConst('KNOB_UNIT_DB')
KNOB_UNIT_HZ = bKnobUnitConst('KNOB_UNIT_HZ')
KNOB_UNIT_PERCENT = bKnobUnitConst('KNOB_UNIT_PERCENT')
KNOB_UNIT_MS = bKnobUnitConst('KNOB_UNIT_MS')
KNOB_UNIT_OCT = bKnobUnitConst('KNOB_UNIT_OCT')
KNOB_UNIT_ST = bKnobUnitConst('KNOB_UNIT_ST')
CONTROL_PAR_FONT_TYPE = bControlParIntVar(
    'CONTROL_PAR_FONT_TYPE', 'font')


class font:
    white_small_tiny = 0
    white_big_bold = 1
    black_big_tiny = 2
    gray_light_medium_tiny = 3
    orange_small = 4
    orange_big_bold = 5
    red_small_tiny = 6
    ref_big_bold = 7
    gray_dark_medium_tiny = 8
    black_medium_normal = 9
    gray_light_medium_normal = 10
    gray_dark_small_normal = 11
    black_medium_normal = 12
    gray_medium_bold = 13
    gray_dark_medium_normal = 14
    gray_dark_medium_bold = 15
    black_big_bold = 16
    white_big_bold_2 = 17
    white_medium_bold = 18
    black_big_bold_2 = 19
    gray_dark_big_bold = 20
    gray_dark_big_bold_2 = 21
    black_medium_bold = 22
    gray_light_medium_bold = 23
    white_medium_bold_2 = 24


CONTROL_PAR_TEXTPOS_Y = bControlParIntVar(
    'CONTROL_PAR_TEXTPOS_Y', 'textpos_y')
CONTROL_PAR_TEXT_ALIGNMENT = bControlParIntVar(
    'CONTROL_PAR_TEXT_ALIGNMENT', 'text_alignment')


class text_alignment:
    left = 0
    center = 1
    right = 2


CONTROL_PAR_AUTOMATION_NAME = bControlParStrVar(
    'CONTROL_PAR_AUTOMATION_NAME', 'automation_name')
CONTROL_PAR_ALLOW_AUTOMATION = bControlParIntVar(
    'CONTROL_PAR_ALLOW_AUTOMATION', 'allow_automation')
CONTROL_PAR_AUTOMATION_ID = bControlParIntVar(
    'CONTROL_PAR_AUTOMATION_ID', 'automation_id')
NI_CONTROL_PAR_IDX = bControlParIntVar('NI_CONTROL_PAR_IDX', 'idx',
                                       callbacks=(UiControlCallback,))


class bKontrolKeyVars(bControlParIntVar):
    pass


CONTROL_PAR_KEY_SHIFT = bKontrolKeyVars(
    'CONTROL_PAR_KEY_SHIFT', 'key_shift')
CONTROL_PAR_KEY_ALT = bKontrolKeyVars('CONTROL_PAR_KEY_ALT', 'key_alt')
CONTROL_PAR_KEY_CONTROL = bKontrolKeyVars(
    'CONTROL_PAR_KEY_CONTROL', 'key_control')


class bControlTableVar(bControlParIntVar):
    pass


class bControlWaveFormVar(bControlParIntVar):
    pass


class bControlTableWaveFormVar(bControlTableVar, bControlWaveFormVar):
    pass


CONTROL_PAR_BAR_COLOR = bControlWaveFormVar(
    'CONTROL_PAR_BAR_COLOR', 'bar_color')
CONTROL_PAR_ZERO_LINE_COLOR = bControlWaveFormVar(
    'CONTROL_PAR_ZERO_LINE_COLOR', 'zero_line_color')


class bControlMenuVar(bControlParIntVar):
    '''works only with get_control_par'''
    pass


CONTROL_PAR_NUM_ITEMS = bControlMenuVar(
    'CONTROL_PAR_NUM_ITEMS', 'num_items')
CONTROL_PAR_SELECTED_ITEM_IDX = bControlMenuVar(
    'CONTROL_PAR_SELECTED_ITEM_IDX', 'selected_item_idx')


class bControlLabelVar(bControlParIntVar):
    pass


CONTROL_PAR_DND_BEHAVIOUR = bControlLabelVar(
    'CONTROL_PAR_DND_BEHAVIOUR', 'dnd_behaviour')


class bControlValueEditVar(bControlParIntVar):
    pass


CONTROL_PAR_SHOW_ARROWS = bControlValueEditVar(
    'CONTROL_PAR_SHOW_ARROWS', 'show_arrows')


class bControlLlvMetVar(bControlParIntVar):
    pass


CONTROL_PAR_OFF_COLOR = bControlLlvMetVar(
    'CONTROL_PAR_OFF_COLOR', 'off_color')
CONTROL_PAR_ON_COLOR = bControlLlvMetVar(
    'CONTROL_PAR_ON_COLOR', 'on_color')
CONTROL_PAR_OVERLOAD_COLOR = bControlLlvMetVar(
    'CONTROL_PAR_OVERLOAD_COLOR', 'overload_color')
CONTROL_PAR_PEAK_COLOR = bControlLlvMetVar(
    'CONTROL_PAR_PEAK_COLOR', 'peak_color')
CONTROL_PAR_VERTICAL = bControlLlvMetVar(
    'CONTROL_PAR_VERTICAL', 'vertical')


class bControlFileBrtVar():
    pass


class bControlFileBrtIntVar(bControlFileBrtVar, bControlParIntVar):
    pass


class bControlFileBrtStrVar(bControlFileBrtVar, bControlParStrVar):
    pass


CONTROL_PAR_BASEPATH = bControlFileBrtStrVar(
    'CONTROL_PAR_BASEPATH', 'basepath')
CONTROL_PAR_FILEPATH = bControlFileBrtStrVar(
    'CONTROL_PAR_FILEPATH', 'filepath')
CONTROL_PAR_COLUMN_WIDTH = bControlFileBrtIntVar(
    'CONTROL_PAR_COLUMN_WIDTH', 'column_width')
CONTROL_PAR_FILE_TYPE = bControlFileBrtIntVar(
    'CONTROL_PAR_FILE_TYPE', 'file_type')


class bControlFileTypeConst(bControlParConst):
    pass


NI_FILE_TYPE_MIDI = bControlFileTypeConst('NI_FILE_TYPE_MIDI')
NI_FILE_TYPE_AUDIO = bControlFileTypeConst('NI_FILE_TYPE_AUDIO')
NI_FILE_TYPE_ARRAY = bControlFileTypeConst('NI_FILE_TYPE_ARRAY')


class bControlValueEditConst(bControlParConst):
    pass


VALUE_EDIT_MODE_NOTE_NAMES = bControlValueEditConst(
    'VALUE_EDIT_MODE_NOTE_NAMES')


class bWaveFormFlagConst(bControlParConst):
    pass


UI_WAVEFORM_USE_SLICES = bWaveFormFlagConst('UI_WAVEFORM_USE_SLICES')
UI_WAVEFORM_USE_TABLE = bWaveFormFlagConst('UI_WAVEFORM_USE_TABLE')
UI_WAVEFORM_TABLE_IS_BIPOLAR = bWaveFormFlagConst(
    'UI_WAVEFORM_TABLE_IS_BIPOLAR')
UI_WAVEFORM_USE_MIDI_DRAG = bWaveFormFlagConst(
    'UI_WAVEFORM_USE_MIDI_DRAG')


class bWaveFormPropConst(bControlParConst):
    pass


UI_WF_PROP_PLAY_CURSOR = bWaveFormPropConst('UI_WF_PROP_PLAY_CURSOR')
UI_WF_PROP_FLAGS = bWaveFormPropConst('UI_WF_PROP_FLAGS')
UI_WF_PROP_TABLE_VAL = bWaveFormPropConst('UI_WF_PROP_TABLE_VAL')
UI_WF_PROP_TABLE_IDX_HIGHLIGHT = bWaveFormPropConst(
    'UI_WF_PROP_TABLE_IDX_HIGHLIGHT')
UI_WF_PROP_MIDI_DRAG_START_NOTE = bWaveFormPropConst(
    'UI_WF_PROP_MIDI_DRAG_START_NOTE')
CONTROL_PAR_WAVE_COLOR = bControlWaveFormVar(
    'CONTROL_PAR_WAVE_COLOR', 'wave_color')
CONTROL_PAR_WAVE_CURSOR_COLOR = bControlWaveFormVar(
    'CONTROL_PAR_WAVE_CURSOR_COLOR', 'cursor_color')
CONTROL_PAR_SLICEMARKERS_COLOR = bControlWaveFormVar(
    'CONTROL_PAR_SLICEMARKERS_COLOR', 'slicemarkers_color')
CONTROL_PAR_BG_ALPHA = bControlWaveFormVar(
    'CONTROL_PAR_BG_ALPHA', 'bg_alpha')


class bControlSliderVar(bControlParIntVar):
    pass


CONTROL_PAR_MOUSE_BEHAVIOUR = bControlParIntVar(
    'CONTROL_PAR_MOUSE_BEHAVIOUR', 'mouse_behaviour')


class bXyPadVar():
    pass


class bControlXyIntVar(bControlParIntVar):
    pass


class bControlXyStrVar(bControlParStrVar):
    pass


CONTROL_PAR_MOUSE_BEHAVIOUR_X = bControlXyIntVar(
    'CONTROL_PAR_MOUSE_BEHAVIOUR_X', 'mouse_behaviour_x')
CONTROL_PAR_MOUSE_BEHAVIOUR_Y = bControlXyIntVar(
    'CONTROL_PAR_MOUSE_BEHAVIOUR_Y', 'mouse_behaviour_y')
CONTROL_PAR_MOUSE_MODE = bControlXyIntVar(
    'CONTROL_PAR_MOUSE_MODE', 'mouse_mode')
CONTROL_PAR_ACTIVE_INDEX = bControlXyIntVar(
    'CONTROL_PAR_ACTIVE_INDEX', 'active_index')
CONTROL_PAR_CURSOR_PICTURE = bControlXyStrVar(
    'CONTROL_PAR_CURSOR_PICTURE', 'cursor_picture')


class ControlParFunc:
    def _resolve_parameter(self, ctrl, parameter):
        ctrl = self._get_contrl_obj(ctrl)
        if isinstance(parameter, str):
            if hasattr(ctrl, parameter):
                parameter = getattr(ctrl.__class__, parameter)._par
            else:
                raise kParVarGetError(parameter)
        return parameter

    def _get_contrl_obj(self,
                        control_or_id: Union[
                            'KspNativeControl',
                            int])-> 'KspNativeControl':
        if isinstance(control_or_id, KspNativeControl):
            return control_or_id
        return ControlId.get_by_id(control_or_id)

    def _add_ksp_control_to_ref(self):
        self._args['control_or_id'] = \
            (*self._args['control_or_id'], KspNativeControl)

    def _get_line_c_id(self,
                       control_or_id: Union['KspNativeControl', int]):

        if isinstance(control_or_id, KspNativeControl):
            return control_or_id.id
        return control_or_id


class kParVar(KSP):

    def __init__(self, control: 'KspNativeControl',
                 control_par: bControlParVar, var_type: Type[KspVar],
                 value: Optional[Union[int, KspIntVar, AstBase]]=None):
        if not isinstance(control_par, bControlParVar):
            raise TypeError(
                f'control_par has to be of type {bControlParVar}')
        if not issubclass(var_type, KspVar):
            raise TypeError(
                f'control has to be subclass of {KspVar}')

        self._var = var_type(kNone(), name='name',
                             is_local=True)
        self._parameter = control_par
        self._par_name = control_par._get_compiled()
        self._control = control
        self._is_set = int()
        self._ref_type = self._var.ref_type
        self._bounded_var = None

        if value:
            if self.is_compiled():
                self._set_compiled(value)
            else:
                self._set_runtime(value)
        self._var._get_compiled = lambda: self._raise_get_compiled()

    @abstractmethod
    def _set_func_invoke(self, val):
        pass

    @abstractmethod
    def _set_func_put_line(self, val):
        pass

    @abstractmethod
    def _get_func_invoke(self):
        pass

    def _raise_get_compiled(self):
        raise RuntimeError(
            'can not get var val, use orig obj param instead')

    def _get_compiled(self):
        if not self._is_set:
            raise kParVarGetError(self._par_name)
        if self._is_set == 1:
            return self._get_runtime()
        return self._get_func_invoke()

    def _set_compiled(self, val: Union[KspIntVar, AstBase, int]):
        if not self._set_runtime(val):
            return
        self._set_func_put_line(val)

    def _get_runtime(self):
        if not self._is_set:
            raise kParVarGetError(self._par_name)
        if self._bounded_var:
            self._var._set_runtime(self._bounded_var._get_runtime())
        return self._var._get_runtime()

    def _set_runtime(self, val: Union[KspIntVar, AstBase, int]):
        if self._bounded_var:
            self._bounded_var._set_runtime(val)
        if isinstance(val, int):
            if self._is_set == 0:
                self._var._set_runtime(val)
                self._is_set += 1
                return
        self._is_set += 1
        self._var._set_runtime(val)
        return True

    def bound_var(self, var: KspVar):
        self._bounded_var = var

    @property
    def val(self):
        if self.is_compiled():
            return self._get_compiled()
        return self._get_runtime()


class kParIntVar(kParVar, kInt):
    def __init__(self, control: 'KspNativeControl',
                 control_par: bControlParVar,
                 value: Optional[Union[int, KspIntVar, AstBase]]=None):
        if value and not isinstance(value, (int, KspIntVar, AstBase)):
            raise TypeError(
                'control_var has to be of type ' +
                f'{int, KspIntVar, AstBase}')
        super().__init__(control=control,
                         control_par=control_par, var_type=kInt,
                         value=value)

    def _get_func_invoke(self):
        return get_control_par(
            self._control, self._parameter)._get_compiled()

    def _set_func_invoke(self, val):
        set_control_par(self._control, self._parameter, val)

    def _set_func_put_line(self, val):
        set_control_par._put_line(self._control, self._parameter, val)


class kParStrVar(kParVar, kStr):
    def __init__(self, control: 'KspNativeControl',
                 control_par: bControlParVar,
                 value: Optional[Union[str, KspStrVar, AstBase]]=None):
        if value and not isinstance(value, (str, KspStrVar, AstBase)):
            raise TypeError(
                'control_var has to be of type ' +
                f'{str, KspStrVar, AstBase}')
        super().__init__(control=control,
                         control_par=control_par, var_type=kStr,
                         value=value)

    def _get_func_invoke(self):
        return get_control_par_str(
            self._control, self._parameter)._get_compiled()

    def _set_func_invoke(self, val):
        set_control_par_str(self._control, self._parameter, val)

    def _set_func_put_line(self, val):
        set_control_par_str._put_line(self._control, self._parameter, val)


class kParArrIntVar(kParVar, kInt):
    def __init__(self, control: 'KspNativeControl',
                 control_par: bControlParVar,
                 value: Optional[Union[int, KspIntVar, AstBase]]=None):
        if value and not isinstance(value, (int, KspIntVar, AstBase)):
            raise TypeError(
                'control_var has to be of type ' +
                f'{int, KspIntVar, AstBase}')
        super().__init__(control=control,
                         control_par=control_par, var_type=kInt,
                         value=value)
        self._idx = None

    def update_idx(self, idx):
        if hasattr(idx, '_get_compiled'):
            idx = idx._get_compiled()
        if hasattr(idx, 'expand'):
            idx = idx.expand()
        self.idx = idx

    def _get_func_invoke(self):
        return get_control_par_arr(
            self._control, self._parameter, self.idx)._get_compiled()

    def _set_func_invoke(self, val):
        set_control_par_arr(self._control, self._parameter, val,
                            self.idx)

    def _set_func_put_line(self, val):
        set_control_par_arr._put_line(self._control, self._parameter, val,
                                      self.idx)


class kParArrStrVar(kParVar, kStr):
    def __init__(self, control: 'KspNativeControl',
                 control_par: bControlParVar,
                 value: Optional[Union[str, KspStrVar, AstBase]]=None):
        if value and not isinstance(value, (str, KspStrVar, AstBase)):
            raise TypeError(
                'control_var has to be of type ' +
                f'{str, KspStrVar, AstBase}')
        super().__init__(control=control,
                         control_par=control_par, var_type=kStr,
                         value=value)
        self._idx = None

    def update_idx(self, idx):
        if hasattr(idx, '_get_compiled'):
            idx = idx._get_compiled()
        if hasattr(idx, 'expand'):
            idx = idx.expand()
        self.idx = idx

    def _get_func_invoke(self):
        return get_control_par_str_arr(
            self._control, self._parameter, self.idx)._get_compiled()

    def _set_func_invoke(self, val):
        set_control_par_str_arr(self._control, self._parameter, val,
                                self.idx)

    def _set_func_put_line(self, val):
        set_control_par_str_arr._put_line(self._control,
                                          self._parameter, val,
                                          self.idx)


class kParVarArrInt(kArrInt):

    def __init__(self, seq):
        self._vars = seq
        super().__init__(size=len(seq), is_local=True)

    def __getitem__(self, idx):
        rt_idx = get_runtime_val(idx)
        var = self._vars[rt_idx]
        var.update_idx(idx)
        # print(var)
        return var

    def __setitem__(self, idx, val):
        return self


class kParVarArrStr(kArrStr):

    def __init__(self, seq):
        self._vars = seq
        super().__init__(size=len(seq), is_local=True)

    def __getitem__(self, idx):
        rt_idx = get_runtime_val(idx)
        var = self._vars[rt_idx]
        var.update_idx(idx)
        # print(var)
        return var

    def __setitem__(self, idx, val):
        return self

# DEPRECATED UNTIL ADDING REAL PARAMETERS IN KSP API
# class kParRealVar(kParVar, kReal):
#     def __init__(self, control: 'KspNativeControl',
#                  control_par: bControlParVar,
#                  value: Optional[Union[
# float, KspRealVar, AstBase]]=None):
#         if value and not isinstance(value,
# (float, KspRealVar, AstBase)):
#             raise TypeError(
#                 'control_var has to be of type ' +
#                 f'{float, KspRealVar, AstBase}')
#         super().__init__(control=control,
#                          control_par=control_par, var_type=kStr,
#                          value=value)

#     def _get_func_invoke(self):
#         return get_control_par_str(
#             self._control, self._parameter)._get_compiled()

#     def _set_func_invoke(self, val):
#         set_control_par_str(self._control, self._parameter, val)

#     def _set_func_put_line(self, val):
#         set_control_par_str._put_line(self._control,
        # self._parameter, val)


class ControlParControls:
    '''KspNativeControl objects handler for indexing control params'''

    def __init__(self):
        self._keys = dict()
        self._ids = list()

    def append(self, control_obj: 'KspNativeControl'):
        '''add control object'''
        assert isinstance(control_obj, KspNativeControl)
        # assert isinstance(control_id, ControlId)
        key = self._get_key_from_control(control_obj)
        self._keys[key] = control_obj
        self._ids.append(control_obj)
        self._id = control_obj.id

    def __getitem__(self, idx: Union[int, 'KspNativeControl']):
        if isinstance(idx, KspNativeControl):
            idx = self._get_key_from_control(idx)
            return self._keys[idx]
            idx = get_runtime_val(idx)
        return self._ids[idx]

    def _get_key_from_control(self, control_obj: 'KspNativeControl'):
        '''return hash for self._keys'''
        return repr(control_obj)


class ControlPar():

    def __init__(self, name: str, cls: Type['KspNativeControl'],
                 arr_type: Type[KspArray],
                 var_type: Type[kParVar],
                 ref_type: Union[Type[int], Type[str], Type[float]],
                 size: int,
                 set_func: Type[ControlParFunc],
                 get_func: Type[ControlParFunc],
                 parameter: bControlParVar):
        self._cls = cls
        self._name = name
        self._var_type = var_type
        self._controls = dict()
        self._obj_count = int()
        self._set_func = set_func
        self._get_func = get_func
        self._arr_type = arr_type
        self._values = list([list()] * size)
        self._vars = list()
        self._size = size
        self._ref_type = self._get_ref_from_basic(ref_type)
        self._par = parameter

    def __call__(self, func: Callable):
        '''returns self, and updates self docstring'''
        if not isinstance(func, Callable):
            raise TypeError('can only be used as decorator')
        self.__doc__ = func.__doc__
        return self

    def _get_key_from_control(self, control_obj: 'KspNativeControl'):
        '''return hash for self._keys'''
        return repr(control_obj)

    def _get_ref_from_basic(self, ref_type: Union[Type[int], Type[str],
                                                  Type[float]]):
        if ref_type is int:
            return (KspIntVar, int)
        if ref_type is str:
            return (KspStrVar, str)
        if ref_type is float:
            return (KspRealVar, float)

    def _get(self, control_or_id: Union['KspNativeControl', int],
             idx: int):
        c_id, c_obj, idx, idx_runtime = \
            self._get_args(control_or_id, idx)
        c_id = self._controls[self._get_key_from_control(c_obj)]
        # print(self._values, idx_runtime, c_id)
        return self._values[idx_runtime][c_id]

    def _get_args(self, control_or_id: Union['KspNativeControl', int],
                  idx: int):
        if isinstance(control_or_id, KspNativeControl):
            c_obj = control_or_id
            c_id = c_obj.id._get_runtime()
        else:
            c_id = get_runtime_val(control_or_id)
            c_obj = ControlId.get_by_id(c_id)
        idx_runtime = get_runtime_val(idx)
        return c_id, c_obj, idx, idx_runtime

    def _check_val(self, value: Any, c_obj: 'KspNativeControl'):
        if not isinstance(value, self._ref_type):
            raise TypeError(
                ('parameter "{n}" of control "{c}"' +
                 ' has to be instance of {t}').format(
                    n=self._name, c=c_obj._name, t=self._ref_type))
        return get_runtime_val(value)

    def _init_control(self, control_obj: 'KspNativeControl',
                      value: Optional[Any],
                      bounded_var: Optional[KspVar]=None):
        if value and not isinstance(value, self._ref_type):
            raise TypeError(
                'parameter "{n}" has to be {t}'.format(
                    n=self._name, t=self._ref_type))

        if not isinstance(control_obj, KspNativeControl):
            raise TypeError(
                'control_obj has to be instance of ' +
                '{ref}, pasted {pst}'.format(
                    ref=KspNativeControl,
                    pst=type(control_obj)))

        if bounded_var:
            if not isinstance(bounded_var, KspVar):
                raise TypeError(
                    'parameter "{n}" bounded_var has to be {t}'.format(
                        n=self._name, t=KspVar))
            self._vars.append(bounded_var)
            if hasattr(bounded_var, '__len__'):
                if len(bounded_var) > self._size:
                    self._values.extend([list([None] * self._obj_count)] *
                                        (len(bounded_var) - self._size))
                    self._size = len(bounded_var)
        else:
            self._vars.append(None)

        # self._controls.append(control_obj)
        key = self._get_key_from_control(control_obj)
        self._controls[key] = self._obj_count
        self._obj_count += 1

        if isinstance(value, Iterable):
            seq = zip(self._values, value)
        else:
            seq = zip(self._values, [value] * len(self._values))

        for item, val in seq:
            obj = self._var_type(control_obj.id, self._par, val)
            item.append(obj)

    def __get__(self, obj: 'KspNativeControl',
                cls: Type['KspNativeControl']):
        if not obj:
            return self
        bound_var = self._vars[self._controls[
            self._get_key_from_control(obj)]]
        if self._size == 1:
            par_var = self._get(obj, 0)
            if bound_var:
                par_var._set_runtime(bound_var._get_runtime())
            return par_var
        seq = list()
        for idx in range(self._size):
            var = self._get(obj, idx)
            try:
                bound_item = bound_var[idx]
            except IndexError:
                seq.append(var)
                continue
            var.bound_var(bound_item)
            seq.append(var)
        return kParVarArrInt(seq)

    def __set__(self, obj: 'KspNativeControl', val: Any):
        if get_runtime_val(val) == self._get(obj, 0)._get_runtime():
            bound_var = self._vars[self._controls[
                self._get_key_from_control(obj)]]
            if bound_var:
                bound_var._set_runtime(get_runtime_val(val))
            return
        raise RuntimeError('use <<= operator instead')


class SetControlPar(BuiltInFuncInt, ControlParFunc):

    def __init__(self):
        super().__init__('set_control_par',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int),
                             parameter=bControlParVar, value=(int)),
                         def_ret=kNone())

    def __call__(self, control_or_id: Union['KspNativeControl', int],
                 parameter: bControlParVar, value: Union[KspIntVar, int]):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        self._set_runtime(control_or_id, parameter, value)
        super().__call__(l_c_id, parameter, value)

    def _set_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: Union[bControlParVar, str], value: int):
        ctrl = self._get_contrl_obj(control_or_id)
        attr = getattr(ctrl, parameter._attr)
        attr._set_runtime(value)

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar, value: int):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        BuiltInFuncInt.__call__(self, l_c_id, parameter, value)


set_control_par = SetControlPar()


class GetControlPar(BuiltInFuncInt, ControlParFunc):

    def __init__(self):
        super().__init__('get_control_par',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int),
                             parameter=bControlParVar))

    def __call__(self, control_or_id: Union['KspNativeControl', int],
                 parameter: bControlParVar):
        self._args['control_or_id'] = \
            (*self._args['control_or_id'], KspNativeControl)
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        return super().__call__(l_c_id, parameter)

    def calculate(self, control_or_id, parameter):
        val = self._get_runtime(control_or_id, parameter)
        return val

    def _get_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: bControlParVar):
        if isinstance(control_or_id, KspNativeControl):
            idx = control_or_id.id._get_runtime()
            ctrl = control_or_id
        else:
            idx = get_runtime_val(control_or_id)
            ctrl = ControlId.get_by_id(idx)
        attr = getattr(ctrl, parameter._attr)
        return attr._get_runtime()

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar):
        l_c_id = self._get_line_c_id(control_or_id)
        temp_calc = self.calculate
        self.calculate = lambda a, b: a + b
        BuiltInFuncInt.__call__(self, l_c_id, parameter)
        self.calculate = temp_calc


get_control_par = GetControlPar()


class SetControlParStr(BuiltInFuncInt, ControlParFunc):

    def __init__(self):
        super().__init__('set_control_par_str',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int),
                             parameter=bControlParVar, value=(str)),
                         def_ret=kNone())

    def __call__(self, control_or_id: Union['KspNativeControl', int],
                 parameter: bControlParVar, value: Union[KspStrVar, str]):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        self._set_runtime(control_or_id, parameter, value)
        super().__call__(l_c_id, parameter, value)

    def _set_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: bControlParVar, value: str):
        ctrl = self._get_contrl_obj(control_or_id)
        attr = getattr(ctrl, parameter._attr)
        attr._set_runtime(value)

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar, value: str):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        BuiltInFuncInt.__call__(self, l_c_id, parameter, value)


set_control_par_str = SetControlParStr()


class GetControlParStr(BuiltInFuncStr, ControlParFunc):

    def __init__(self):
        super().__init__('get_control_par_str',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int),
                             parameter=bControlParVar))

    def __call__(self, control_or_id: Union['KspNativeControl', int],
                 parameter: bControlParVar):
        self._args['control_or_id'] = \
            (*self._args['control_or_id'], KspNativeControl)
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        return super().__call__(l_c_id, parameter)

    def calculate(self, control_or_id, parameter):
        val = self._get_runtime(control_or_id, parameter)
        return val

    def _get_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: bControlParVar):
        if isinstance(control_or_id, KspNativeControl):
            idx = control_or_id.id._get_runtime()
            ctrl = control_or_id
        else:
            idx = get_runtime_val(control_or_id)
            ctrl = ControlId.get_by_id(idx)
        attr = getattr(ctrl, parameter._attr)
        return attr._get_runtime()

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar):
        l_c_id = self._get_line_c_id(control_or_id)
        temp_calc = self.calculate
        self.calculate = lambda a, b: a + b
        BuiltInFuncInt.__call__(self, l_c_id, parameter)
        self.calculate = temp_calc


get_control_par_str = GetControlParStr()


class SetControlParArr(BuiltInFuncInt, ControlParFunc):

    def __init__(self):
        super().__init__('set_control_par_arr',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int, AstBase),
                             parameter=bControlParVar,
                             value=(KspIntVar, int, AstBase),
                             idx=(KspIntVar, int, AstBase)),
                         def_ret=kNone())

    def __call__(self,
                 control_or_id: Union['KspNativeControl', int, AstBase],
                 parameter: bControlParVar,
                 value: Union[KspIntVar, int, AstBase],
                 idx: Union[KspIntVar, int, AstBase]):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        self._set_runtime(control_or_id, parameter, value)
        super().__call__(l_c_id, parameter, value, idx)

    def _set_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: Union[bControlParVar, str], value: int,
                     idx: int):
        ctrl = self._get_contrl_obj(control_or_id)
        attr = getattr(ctrl, parameter._attr)
        idx = get_runtime_val(idx)
        attr[idx]._set_runtime(value)

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar, value: int, idx: int):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        BuiltInFuncInt.__call__(self, l_c_id, parameter, value, idx)


set_control_par_arr = SetControlParArr()


class GetControlParArr(BuiltInFuncInt, ControlParFunc):

    def __init__(self):
        super().__init__('get_control_par_arr',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int, AstBase),
                             parameter=bControlParVar,
                             idx=(KspIntVar, int, AstBase)))

    def __call__(self, control_or_id: Union['KspNativeControl', int],
                 parameter: bControlParVar, idx: int):
        self._args['control_or_id'] = \
            (*self._args['control_or_id'], KspNativeControl)
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        return super().__call__(l_c_id, parameter, idx)

    def calculate(self, control_or_id, parameter, idx):
        val = self._get_runtime(control_or_id, parameter, idx)
        return val

    def _get_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: bControlParVar, idx: int):
        if isinstance(control_or_id, KspNativeControl):
            c_idx = control_or_id.id._get_runtime()
            ctrl = control_or_id
        else:
            c_idx = get_runtime_val(control_or_id)
            ctrl = ControlId.get_by_id(c_idx)
        idx = get_runtime_val(idx)
        attr = getattr(ctrl, parameter._attr)
        return attr[idx]._get_runtime()

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar, idx: int):
        l_c_id = self._get_line_c_id(control_or_id)
        temp_calc = self.calculate
        self.calculate = lambda a, b: a + b
        BuiltInFuncInt.__call__(self, l_c_id, parameter, idx)
        self.calculate = temp_calc


get_control_par_arr = GetControlParArr()


class SetControlParStrArr(BuiltInFuncInt, ControlParFunc):

    def __init__(self):
        super().__init__('set_control_par_str_arr',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int, AstBase),
                             parameter=bControlParVar,
                             value=(KspStrVar, str, AstBase),
                             idx=(KspIntVar, int, AstBase)),
                         def_ret=kNone())

    def __call__(self,
                 control_or_id: Union['KspNativeControl', int, AstBase],
                 parameter: bControlParVar,
                 value: Union[KspStrVar, str, AstBase],
                 idx: Union[KspIntVar, int, AstBase]):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        self._set_runtime(control_or_id, parameter, value)
        super().__call__(l_c_id, parameter, value, idx)

    def _set_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: Union[bControlParVar, str], value: str,
                     idx: int):
        ctrl = self._get_contrl_obj(control_or_id)
        attr = getattr(ctrl, parameter._attr)
        idx = get_runtime_val(idx)
        attr[idx]._set_runtime(value)

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar, value: str, idx: int):
        self._add_ksp_control_to_ref()
        l_c_id = self._get_line_c_id(control_or_id)
        BuiltInFuncInt.__call__(self, l_c_id, parameter, value, idx)


set_control_par_str_arr = SetControlParStrArr()


class GetControlParStrArr(BuiltInFuncStr, ControlParFunc):

    def __init__(self):
        super().__init__('get_control_par_str_arr',
                         args=OrderedDict(
                             control_or_id=(KspIntVar, int, AstBase),
                             parameter=bControlParVar,
                             idx=(KspIntVar, int, AstBase)))

    def __call__(self, control_or_id: Union['KspNativeControl', int],
                 parameter: bControlParVar, idx: int):
        self._args['control_or_id'] = \
            (*self._args['control_or_id'], KspNativeControl)
        l_c_id = self._get_line_c_id(control_or_id)
        parameter = self._resolve_parameter(control_or_id, parameter)
        return super().__call__(l_c_id, parameter, idx)

    def calculate(self, control_or_id, parameter, idx):
        val = self._get_runtime(control_or_id, parameter, idx)
        return val

    def _get_runtime(self, control_or_id: Union['KspNativeControl', int],
                     parameter: bControlParVar, idx: int):
        if isinstance(control_or_id, KspNativeControl):
            c_idx = control_or_id.id._get_runtime()
            ctrl = control_or_id
        else:
            c_idx = get_runtime_val(control_or_id)
            ctrl = ControlId.get_by_id(c_idx)
        idx = get_runtime_val(idx)
        attr = getattr(ctrl, parameter._attr)
        return attr[idx]._get_runtime()

    def _put_line(self, control_or_id: Union['KspNativeControl', int],
                  parameter: bControlParVar, idx: int):
        l_c_id = self._get_line_c_id(control_or_id)
        temp_calc = self.calculate
        self.calculate = lambda a, b: a + b
        BuiltInFuncInt.__call__(self, l_c_id, parameter, idx)
        self.calculate = temp_calc


get_control_par_str_arr = GetControlParStrArr()


def refresh():
    '''resets constants of all classes to defaults'''
    ControlId._controls_arr = None
    ControlId._controls = list()
    ControlId._controls_ids = dict()
    ControlId._id_count = int()
    KspNativeControlMeta.objects_count = int()
    KspNativeControlMeta.objects = list()


class ControlId(kInt):
    _controls_arr = None
    _controls = list()
    _controls_ids = dict()
    _id_count = int()

    def __init__(self, control_obj: 'KspNativeControl'):
        if ControlId._controls_arr is None:
            ControlId._controls_arr = kArrInt(name='_all_ui_ids')
        self._control = control_obj
        self._id = ControlId._id_count
        ControlId._controls.append(control_obj)
        id_var = kInt(self._id, is_local=True)
        id_var.name = lambda: f'get_ui_id({control_obj.var.name()})'
        ControlId._controls_arr.append(id_var)
        ControlId._id_count += 1

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return ControlId._controls_arr[obj._id]

    @staticmethod
    def get_by_id(control_id: int):
        control_id = get_runtime_val(control_id)
        return ControlId._controls[control_id]


class KspNativeControlMeta(WidgetMeta):
    objects_count = int()
    objects = list()

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls.ids = kArrInt(name=f'_{name}_ids')
        cls._decl_name = name
        cls._def_width = 85
        cls._def_height = 18

        cls.x = ControlPar('x', cls, kArrInt, kParIntVar, int, 1,
                           set_control_par, get_control_par,
                           CONTROL_PAR_POS_X)
        cls.x.__doc__ = 'x position in pixels'
        cls.y = ControlPar('y', cls, kArrInt, kParIntVar, int, 1,
                           set_control_par, get_control_par,
                           CONTROL_PAR_POS_Y)
        cls.width = ControlPar('width', cls, kArrInt, kParIntVar,
                               int, 1,
                               set_control_par, get_control_par,
                               CONTROL_PAR_WIDTH)
        cls.height = ControlPar('height', cls, kArrInt, kParIntVar,
                                int, 1,
                                set_control_par, get_control_par,
                                CONTROL_PAR_HEIGHT)
        cls.help = ControlPar('help', cls, kArrStr, kParStrVar, str, 1,
                              set_control_par_str, get_control_par_str,
                              CONTROL_PAR_HELP)

        cls.grid_x = ControlPar('grid_x', cls, kArrInt, kParIntVar,
                                int, 1,
                                set_control_par, get_control_par,
                                CONTROL_PAR_GRID_X)
        cls.grid_y = ControlPar('grid_y', cls, kArrInt, kParIntVar,
                                int, 1,
                                set_control_par, get_control_par,
                                CONTROL_PAR_GRID_Y)
        cls.grid_width = ControlPar('grid_width', cls, kArrInt,
                                    kParIntVar, int, 1,
                                    set_control_par, get_control_par,
                                    CONTROL_PAR_GRID_WIDTH)
        cls.grid_height = ControlPar('grid_height', cls, kArrInt,
                                     kParIntVar, int, 1,
                                     set_control_par, get_control_par,
                                     CONTROL_PAR_GRID_HEIGHT)
        cls.help = ControlPar('help', cls, kArrStr, kParStrVar, str, 1,
                              set_control_par_str, get_control_par_str,
                              CONTROL_PAR_HELP)
        cls.hide = ControlPar('hide', cls, kArrInt,
                              kParIntVar, bControlHideConst, 1,
                              set_control_par, get_control_par,
                              CONTROL_PAR_HIDE)
        cls.z_layer = ControlPar('z_layer', cls, kArrInt,
                                 kParIntVar, int, 1,
                                 set_control_par, get_control_par,
                                 CONTROL_PAR_Z_LAYER)
        cls.key_control = ControlPar('key_control', cls, kArrInt,
                                     kParIntVar, int, 1,
                                     set_control_par, get_control_par,
                                     CONTROL_PAR_KEY_CONTROL)
        cls.key_alt = ControlPar('key_alt', cls, kArrInt,
                                 kParIntVar, int, 1,
                                 set_control_par, get_control_par,
                                 CONTROL_PAR_KEY_SHIFT)
        cls.key_shift = ControlPar('key_shift', cls, kArrInt,
                                   kParIntVar, int, 1,
                                   set_control_par, get_control_par,
                                   CONTROL_PAR_KEY_ALT)

        return cls

    ParentTuple = Optional[Union[kWidget, kMainWindow]]

    def __call__(cls, *args, name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: ParentTuple=None,
                 x: Optional[int]=None, y: Optional[int]=None,
                 width: Optional[int]=None,
                 height: Optional[int]=None, size: Optional[int]=None,
                 **kwargs):
        obj = super().__call__(*args, persist=persist,
                               parent=parent,
                               x=x, y=y,
                               width=width,
                               height=height, **kwargs)

        obj._id = KspNativeControlMeta.objects_count
        if name is None:
            name = f'control{obj._id}'
        obj._name = name
        KspNativeControlMeta.objects.append(obj)
        KspNativeControlMeta.objects_count += 1
        try:
            if size:
                obj.var = cls._var_type(name=name, preserve=preserve,
                                        persist=persist, size=size)
            else:
                obj.var = cls._var_type(name=name, preserve=preserve,
                                        persist=persist)
        except AttributeError:
            raise AttributeError(
                'class has to contain attribute "_var_type" which is' +
                f'subclass of {KspVar}')

        obj.var._generate_init = obj._generate_init
        obj._decl_postfix = ''

        cls.id = ControlId(obj)
        obj._id_lines = ''
        if KSP.is_compiled():
            obj._id_lines = [Output().pop()]
        cls.ids.append(obj.id)
        if KSP.is_compiled():
            obj._id_lines.append(Output().pop())
        # print(obj._id_lines)

        cls.x._init_control(obj, x)
        cls.y._init_control(obj, y)
        cls.width._init_control(obj, width)
        cls.height._init_control(obj, height)

        cls.grid_x._init_control(obj, None)
        cls.grid_y._init_control(obj, None)
        cls.grid_width._init_control(obj, None)
        cls.grid_height._init_control(obj, None)

        cls.help._init_control(obj, None)
        cls.hide._init_control(obj, None)
        cls.z_layer._init_control(obj, None)
        cls.key_alt._init_control(obj, None)
        cls.key_control._init_control(obj, None)
        cls.key_shift._init_control(obj, None)
        return obj


def init_value(cls):
    return ControlPar('value', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_VALUE)


def init_default(cls):
    return ControlPar('default', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_VALUE)


def init_picture(cls):
    return ControlPar('picture', cls, kArrStr,
                      kParStrVar, str, 1,
                      set_control_par_str, get_control_par_str,
                      CONTROL_PAR_PICTURE)


def init_picture_state(cls):
    return ControlPar('picture_state', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_PICTURE_STATE)


def init_text(cls):
    return ControlPar('text', cls, kArrStr,
                      kParStrVar, str, 1,
                      set_control_par_str, get_control_par_str,
                      CONTROL_PAR_TEXT)


def init_textline(cls):
    return ControlPar('textline', cls, kArrStr,
                      kParStrVar, str, 1,
                      set_control_par_str, get_control_par_str,
                      CONTROL_PAR_TEXTLINE)


def init_label(cls):
    return ControlPar('label', cls, kArrStr,
                      kParStrVar, str, 1,
                      set_control_par_str, get_control_par_str,
                      CONTROL_PAR_LABEL)


def init_font_type(cls):
    return ControlPar('font_type', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_FONT_TYPE)


def init_textpos_y(cls):
    return ControlPar('textpos_y', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_TEXTPOS_Y)


def init_text_alignment(cls):
    return ControlPar('text_alignment', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_TEXT_ALIGNMENT)


def init_automation_name(cls):
    return ControlPar('automation_name', cls, kArrStr,
                      kParStrVar, str, 1,
                      set_control_par_str, get_control_par_str,
                      CONTROL_PAR_AUTOMATION_NAME)


def init_allow_automation(cls):
    return ControlPar('allow_automation', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_ALLOW_AUTOMATION)


def init_automation_id(cls):
    return ControlPar('automation_id', cls, kArrInt,
                      kParIntVar, int, 1,
                      set_control_par, get_control_par,
                      CONTROL_PAR_AUTOMATION_ID)


class KspNativeControl(kWidget, metaclass=KspNativeControlMeta):
    _var_type = kInt

    def __init__(self, name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: object=None, x: int=None, y: int=None,
                 width: int=None, height: int=None):
        super().__init__(parent=parent, x=x, y=y,
                         width=width, height=height)
        self._persist = persist
        self._read = False

    def read(self):
        self._persist = True
        self._read = True

    def _generate_init(self):
        # return self.__class__._generate_init(self)
        name = self.__class__._decl_name
        out = [f'declare ui_{name} {self.var.name()} ' +
               f'{self._decl_postfix}']
        if self._persist:
            out.append(f'make_persistent({self.var.name()})')
        if self._read:
            out.append(f'read_persistent_var({self.var.name()})')
        out.extend(self._id_lines)
        return out

    def bound_callback(self, function):
        UiControlCallback.open(self.var)
        function(control=self)
        UiControlCallback.close()


def value_min_max(obj: KspNativeControl, min_val: int, max_val: int):
    '''adds obj._min and obj._max attributes
    wraps obj.var._set_runtime method for raising RuntimeError
    if input value is out of bounds'''
    if not isinstance(min_val, int):
        raise TypeError(f'min_val has to be of type {int}')
    if not isinstance(max_val, int):
        raise TypeError(f'max_val has to be of type {int}')
    obj._min = min_val
    obj._max = max_val
    f = obj.var._set_runtime

    @wraps(f)
    def wrapper(val):
        val_rt = get_runtime_val(val)
        if val_rt < obj._min or val > obj._max:
            raise RuntimeError('value is out of bounds. has to be ' +
                               f'between {obj._min} and {obj._max}')
        return f(val)
    obj.var._set_runtime = wrapper


class kButtonMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'button'

        cls.value = init_value(cls)
        cls.picture = init_picture(cls)
        cls.picture_state = init_picture_state(cls)
        cls.text = init_text(cls)
        cls.font_type = init_font_type(cls)
        cls.textpos_y = init_textpos_y(cls)
        cls.text_alignment = init_text_alignment(cls)

        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(*args, **kwargs)
        obj._decl_postfix = ''

        cls.value._init_control(obj, None, obj.var)
        cls.picture._init_control(obj, None)
        cls.picture_state._init_control(obj, None)
        cls.text._init_control(obj, None)
        cls.font_type._init_control(obj, None)
        cls.textpos_y._init_control(obj, None)
        cls.text_alignment._init_control(obj, None)
        return obj


class kButton(KspNativeControl, metaclass=kButtonMeta):
    '''Simple button.
    Remarks
    • a button (i.e. its callback) is triggered when releasing the mouse
    (aka mouse-up)
    • a button cannot be automated'''
    pass


class kSwitchMeta(kButtonMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'switch'

        cls.automation_name = init_automation_name(cls)
        cls.allow_automation = init_allow_automation(cls)
        cls.automation_id = init_automation_id(cls)
        cls.label = init_label(cls)
        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(*args, **kwargs)
        obj._decl_postfix = ''

        cls.automation_name._init_control(obj, None)
        cls.allow_automation._init_control(obj, None)
        cls.automation_id._init_control(obj, None)
        cls.label._init_control(obj, None)
        return obj


class kSwitch(KspNativeControl, metaclass=kSwitchMeta):
    '''Switch, e.g. automatable button
    Remarks
    • a switch (i.e. its callback) is triggered when clicking the mouse
    (aka mouse-down)
    • a switch can be automated'''
    pass


class kKnobMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'knob'
        cls._def_width = 85
        cls._def_height = 40

        cls.value = init_value(cls)
        cls.default = init_default(cls)
        cls.automation_name = init_automation_name(cls)
        cls.automation_id = init_automation_id(cls)
        cls.allow_automation = init_allow_automation(cls)
        cls.text = init_text(cls)
        cls.label = init_label(cls)
        cls.font_type = init_font_type(cls)
        cls.textpos_y = init_textpos_y(cls)
        cls.text_alignment = init_text_alignment(cls)
        cls.unit = ControlPar('unit', cls, kArrInt,
                              kParIntVar, bKnobUnitConst, 1,
                              set_control_par, get_control_par,
                              CONTROL_PAR_UNIT)

        return cls

    def __call__(cls, min_val: int, max_val: int, display_ratio: int,
                 *args, **kwargs):

        obj = super().__call__(*args, min_val=min_val, max_val=max_val,
                               display_ratio=display_ratio,
                               **kwargs)

        value_min_max(obj, min_val, max_val)
        obj._decl_postfix = f'({min_val}, {max_val}, {display_ratio})'

        cls.value._init_control(obj, None, obj.var)
        cls.default._init_control(obj, None)
        cls.automation_name._init_control(obj, None)
        cls.automation_id._init_control(obj, None)
        cls.allow_automation._init_control(obj, None)
        cls.text._init_control(obj, None)
        cls.label._init_control(obj, None)
        cls.font_type._init_control(obj, None)
        cls.textpos_y._init_control(obj, None)
        cls.text_alignment._init_control(obj, None)
        cls.unit._init_control(obj, None)

        return obj


class kKnob(KspNativeControl, metaclass=kKnobMeta):
    '''create a user interface knob
    <min>
    the minimum value of the knob
    <max>
    the maximum value of the knob
    <display-ratio>
    the knob value is divided by <display-ratio> for display purposes
    '''

    def __init__(self, min_val, max_val, display_ratio,
                 name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: object=None, x: int=None, y: int=None,
                 width: int=None, height: int=None):
        super().__init__(name=name, persist=persist, preserve=preserve,
                         parent=parent, x=x, y=y,
                         width=width, height=height)


class kFileSelectorMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'file_selector'

        cls.filepath = ControlPar('filath', cls, kArrStr, kParStrVar,
                                  str, 1,
                                  set_control_par_str,
                                  get_control_par_str,
                                  CONTROL_PAR_FILEPATH)

        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(*args, **kwargs)

        cls.filepath._init_control(obj, None)


class kFileSelector(KspNativeControl, metaclass=KspNativeControlMeta):
    '''create a file selector
    Remarks
    Only one file selector can be applied per script slot.'''

    def get_file_name(self,
                      return_format: Union[int, KspIntVar, AstBase]):
        '''return the filename of the last selected file in the
        UI file browser.
        <return_format>
        0: returns the filename without extension
        1: returns the filename with extension
        2: returns the whole path'''
        rf = get_runtime_val(return_format)
        if not isinstance(rf, int):
            raise TypeError(
                'return_format has to be of type ' +
                '{t}, passed {p}'.format(t=(int, KspIntVar, AstBase),
                                         p=type(return_format)))
        if hasattr(return_format, '_get_compiled'):
            return_format = return_format._get_compiled()
        if hasattr(return_format, 'expand'):
            return_format = return_format.expand()
        string = 'fs_get_filename({idx},{rf})'.format(
            idx=self.id._get_compiled(),
            rf=return_format)
        var = kStr(is_local=True)
        var.name = lambda: string
        return var

    def navigate(self,
                 direction: Union[int, KspIntVar, AstBase]):
        '''jump to the next/previous file in an ui file selector and
        trigger its callback.
        <direction>
        0: the previous file (in relation to the currently selected one)
        is selected
        1: the next file (in relation to the currently selected one)
        is selected'''
        rt = get_runtime_val(direction)
        if not isinstance(rt, int):
            raise TypeError(
                'return_format has to be of type ' +
                '{t}, passed {p}'.format(t=(int, KspIntVar, AstBase),
                                         p=type(direction)))
        if hasattr(direction, '_get_compiled'):
            direction = direction._get_compiled()
        if hasattr(direction, 'expand'):
            direction = direction.expand()
        string = 'fs_navigate({idx},{rf})'.format(
            idx=self.id._get_compiled(),
            rf=direction)
        if KSP.is_compiled():
            Output().put(string)

    def base_path(self,
                  path: Union[str, KspStrVar, AstBase]):
        '''sets the basepath of the UI file browser.
        Can only be used in the init callback.
        Be careful with the number of subfolders of the basepath as it
        might take too long to scan the sub file system.
        The scan process takes place every time the NKI is loaded.'''
        if not KSP.in_init():
            raise RuntimeError('has to be used inside init callback')
        rt = get_runtime_val(path)
        if not isinstance(rt, str):
            raise TypeError(
                'return_format has to be of type ' +
                '{t}, passed {p}'.format(t=(str, KspStrVar, AstBase),
                                         p=type(path)))
        if isinstance(path, str):
            path = f'"{path}"'
        if hasattr(path, '_get_compiled'):
            path = path._get_compiled()
        if hasattr(path, 'expand'):
            path = path.expand()
        string = f'set_control_par_str({self.id._get_compiled()}, ' +\
            f'$CONTROL_PAR_BASEPATH, {path})'
        if KSP.is_compiled():
            Output().put(string)

    def column_width(self,
                     width: Union[int, KspIntVar, AstBase]):
        '''sets the width of the browser columns.
        Can only be used in the init callback.'''
        if not KSP.in_init():
            raise RuntimeError('has to be used inside init callback')
        rt = get_runtime_val(width)
        if not isinstance(rt, int):
            raise TypeError(
                'return_format has to be of type ' +
                '{t}, passed {p}'.format(t=(int, KspIntVar, AstBase),
                                         p=type(width)))
        if hasattr(width, '_get_compiled'):
            width = width._get_compiled()
        if hasattr(width, 'expand'):
            width = width.expand()
        string = f'set_control_par_str({self.id._get_compiled()}, ' +\
            f'$CONTROL_PAR_COLUMN_WIDTH, {width})'
        if KSP.is_compiled():
            Output().put(string)

    def file_type(self,
                  file_type: bControlFileTypeConst):
        '''sets the file type for file selector.
        Can only be used in the init callback.
        The following file types are available:
        $NI_FILE_TYPE_MIDI
        $NI_FILE_TYPE_AUDIO
        $NI_FILE_TYPE_ARRAY'''
        if not KSP.in_init():
            raise RuntimeError('has to be used inside init callback')
        if not isinstance(file_type, bControlFileTypeConst):
            raise TypeError(
                'return_format has to be of type ' +
                '{t}, passed {p}'.format(t=bControlFileTypeConst,
                                         p=type(file_type)))
        if hasattr(file_type, '_get_compiled'):
            file_type = file_type._get_compiled()
        if hasattr(file_type, 'expand'):
            file_type = file_type.expand()
        string = f'set_control_par_str({self.id._get_compiled()}, ' +\
            f'$CONTROL_PAR_FILE_TYPE, {file_type})'
        if KSP.is_compiled():
            Output().put(string)


class kLabelMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'label'

        cls.picture = init_picture(cls)
        cls.picture_state = init_picture_state(cls)
        cls.text = init_text(cls)
        cls.text_line = init_textline(cls)
        cls.font_type = init_font_type(cls)
        cls.textpos_y = init_textpos_y(cls)
        cls.text_alignment = init_text_alignment(cls)

        cls.dnd_behaviour = ControlPar('dnd_behaviour', cls, kArrInt,
                                       kParIntVar, int, 1,
                                       set_control_par,
                                       get_control_par,
                                       CONTROL_PAR_DND_BEHAVIOUR)

        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(*args, **kwargs)
        obj._decl_postfix = '(1, 1)'

        cls.picture._init_control(obj, None)
        cls.picture_state._init_control(obj, None)
        cls.text._init_control(obj, None)
        cls.text_line._init_control(obj, None)
        cls.font_type._init_control(obj, None)
        cls.textpos_y._init_control(obj, None)
        cls.text_alignment._init_control(obj, None)
        cls.dnd_behaviour._init_control(obj, None)
        return obj


class kLabel(KspNativeControl, metaclass=kLabelMeta):
    '''text label'''
    pass


class kLevelMeterMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'level_meter'

        cls.bg_color = ControlPar('bg_color', cls, kArrInt, kParIntVar,
                                  int, 1,
                                  set_control_par,
                                  get_control_par,
                                  CONTROL_PAR_BG_COLOR)
        cls.off_color = ControlPar('off_color', cls, kArrInt, kParIntVar,
                                   int, 1,
                                   set_control_par,
                                   get_control_par,
                                   CONTROL_PAR_OFF_COLOR)
        cls.on_color = ControlPar('on_color', cls, kArrInt, kParIntVar,
                                  int, 1,
                                  set_control_par,
                                  get_control_par,
                                  CONTROL_PAR_ON_COLOR)
        cls.overload_color = ControlPar('overload_color', cls,
                                        kArrInt, kParIntVar,
                                        int, 1,
                                        set_control_par,
                                        get_control_par,
                                        CONTROL_PAR_OVERLOAD_COLOR)
        cls.peak_color = ControlPar('peak_color', cls, kArrInt, kParIntVar,
                                    int, 1,
                                    set_control_par,
                                    get_control_par,
                                    CONTROL_PAR_PEAK_COLOR)
        cls.vertical = ControlPar('vertical', cls, kArrInt, kParIntVar,
                                  int, 1,
                                  set_control_par,
                                  get_control_par,
                                  CONTROL_PAR_VERTICAL)

        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(*args, **kwargs)
        obj._decl_postfix = ''

        cls.bg_color._init_control(obj, None)
        cls.off_color._init_control(obj, None)
        cls.on_color._init_control(obj, None)
        cls.overload_color._init_control(obj, None)
        cls.peak_color._init_control(obj, None)
        cls.vertical._init_control(obj, None)

        return obj


class kLevelMeter(KspNativeControl, metaclass=kLevelMeterMeta):
    '''level meter, captures output volume of one channel'''

    def attach(self, channel: int, bus: int):
        ch_rt = get_runtime_val(channel)
        if not isinstance(ch_rt, int):
            raise TypeError('channel has to be int')
        bus_rt = get_runtime_val(bus)
        if not isinstance(bus_rt, int):
            raise TypeError('bus has to be int')
        if hasattr(channel, '_get_compiled'):
            channel = channel._get_compiled()
        if hasattr(channel, 'expand'):
            channel = channel.expand()
        if hasattr(bus, '_get_compiled'):
            bus = bus._get_compiled()
        if hasattr(bus, 'expand'):
            bus = bus.expand()

        string = \
            'attach_level_meter({id}, -1, -1, {ch}, {bs})'.format(
                id=self.id._get_compiled(),
                ch=channel, bs=bus)
        if KSP.is_compiled():
            Output().put(string)


class kMenuMeta(kButtonMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'menu'

        cls.num_items = ControlPar('num_items', cls, kArrInt, kParIntVar,
                                   int, 1,
                                   set_control_par,
                                   get_control_par,
                                   CONTROL_PAR_NUM_ITEMS)
        cls.selected_item_idx = ControlPar('selected_item_idx',
                                           cls, kArrInt, kParIntVar,
                                           int, 1,
                                           set_control_par,
                                           get_control_par,
                                           CONTROL_PAR_SELECTED_ITEM_IDX)

        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(*args, **kwargs)

        cls.num_items._init_control(obj, None)
        cls.selected_item_idx._init_control(obj, None)

        return obj


class MenuItem:

    def __init__(self, text, val, idx):
        self.idx = idx
        self.text = text
        self.value = val
        self.visible = 1


class kMenu(KspNativeControl, metaclass=kMenuMeta):

    def __init__(self, name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: object=None, x: int=None, y: int=None,
                 width: int=None, height: int=None):
        super().__init__(name=name, persist=persist, preserve=preserve,
                         parent=parent, x=x, y=y,
                         width=width, height=height)

        self._items = list()
        self._items_amount = int()

    def _get_value(self, prop_ret):
        return self.var

    def _set_value(self, val, prop_ret):
        self.var <<= val

    def add_item(self, text: str, value: int):
        '''create a menu entry
        <text>
        the text of the menu entry
        <value>
        the value of the menu entry
        Remarks
        • You can create menu entries only in the init callback but you
        can change their text and value afterwards by using
        set_menu_item_str() and set_menu_item_value(). You can add as
        many menu entries as you want and then show or hide them
        dynamically by using set_menu_item_visibility().
        • Using the $CONTROL_PAR_VALUE constant in the get_control_par()
        command will return the menu index and not the value,
        if you want to get the menu value, use the get_menu_item_value()
        command.'''
        if not KSP.in_init():
            raise RuntimeError('has to be inside init callback')
        self._items.append(MenuItem(text, value, self._items_amount))
        self._items_amount += 1

    def get_item_str(self, idx: int):
        '''returns the string value of the menu’s entry.'''
        return get_menu_item_str(self.id, idx)

    def get_item_value(self, idx: int):
        '''returns the value of the menu’s entry.'''
        return get_menu_item_value(self.id, idx)

    def get_item_visibility(self, idx: int):
        '''returns 1 if the menu entry is visible, otherwise 0.'''
        return get_menu_item_visibility(self.id, idx)

    def set_item_str(self, idx: int, val: str):
        '''returns the string value of the menu’s entry.'''
        return set_menu_item_str(self.id, idx, val)

    def set_item_value(self, idx: int, val: int):
        '''sets the value of a menu entry.'''
        return set_menu_item_value(self.id, idx, val)

    def set_item_visibility(self, idx: int, val: int):
        '''set visibility of menu item.
        <val>
        if 0 item will be hided
        if 1 item will be shown'''
        return set_menu_item_visibility(self.id, idx, val)


class GetMenuItemStr(BuiltInFuncStr):

    def __init__(self):
        super().__init__('get_menu_item_str',
                         args=OrderedDict(
                             menu_or_id=(kMenu, int, KspIntVar, AstBase),
                             idx=(int, KspIntVar, AstBase)))

    def __call__(self, menu_or_id: Union[kMenu, int],
                 idx: int):
        '''returns the string value of the menu’s entry.
        <menu_or_id>
        the ID of the menu that you want to modify or kMenu instance
        <index>
        the index of the menu item'''
        if isinstance(menu_or_id, kMenu):
            menu_or_id = menu_or_id.id
        return super().__call__(menu_or_id, idx)

    def calculate(self, menu_id, idx):
        menu = ControlId.get_by_id(menu_id)
        idx = get_runtime_val(idx)
        return menu._items[idx].text


get_menu_item_str = GetMenuItemStr()


class GetMenuItemValue(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_menu_item_value',
                         args=OrderedDict(
                             menu_or_id=(kMenu, int, KspIntVar, AstBase),
                             idx=(int, KspIntVar, AstBase)))

    def __call__(self, menu_or_id: Union[kMenu, int],
                 idx: int):
        '''returns the value of the menu’s entry.
        <menu_or_id>
        the ID of the menu that you want to modify or kMenu instance
        <index>
        the index of the menu item'''
        if isinstance(menu_or_id, kMenu):
            menu_or_id = menu_or_id.id
        return super().__call__(menu_or_id, idx)

    def calculate(self, menu_id, idx):
        menu = ControlId.get_by_id(menu_id)
        idx = get_runtime_val(idx)
        return menu._items[idx].value


get_menu_item_value = GetMenuItemValue()


class GetMenuItemVisibility(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_menu_item_visibility',
                         args=OrderedDict(
                             menu_or_id=(kMenu, int, KspIntVar, AstBase),
                             idx=(int, KspIntVar, AstBase)))

    def __call__(self, menu_or_id: Union[kMenu, int],
                 idx: int):
        '''returns 1 if the menu entry is visible, otherwise 0.
        <menu_or_id>
        the ID of the menu that you want to modify, or kMenu instance
        <index>
        the index of the menu entry'''
        if isinstance(menu_or_id, kMenu):
            menu_or_id = menu_or_id.id
        return super().__call__(menu_or_id, idx)

    def calculate(self, menu_id, idx):
        menu = ControlId.get_by_id(menu_id)
        idx = get_runtime_val(idx)
        return menu._items[idx].visible


get_menu_item_visibility = GetMenuItemVisibility()


class SetMenuItemStr(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_menu_item_str',
                         args=OrderedDict(
                             menu_or_id=(kMenu, int, KspIntVar, AstBase),
                             idx=(int, KspIntVar, AstBase),
                             text=(str, KspStrVar, AstBase)))

    def __call__(self, menu_or_id: Union[kMenu, int],
                 idx: int, text: str):
        '''sets the text of a menu entry.
        <menu_or_id>
        the ID of the menu that you want to modify or kMenu instance
        <index>
        the index of the menu item'''
        if isinstance(menu_or_id, kMenu):
            menu_or_id = menu_or_id.id
        return super().__call__(menu_or_id, idx, text)

    def calculate(self, menu_id, idx, val):
        menu = ControlId.get_by_id(menu_id)
        idx = get_runtime_val(idx)
        val = get_runtime_val(val)
        if not isinstance(idx, int):
            raise TypeError('idx has to be instance of int')
        if not isinstance(val, str):
            raise TypeError('val has to be instance of str')
        menu._items[idx].text = val
        return kNone()


set_menu_item_str = SetMenuItemStr()


class SetMenuItemValue(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_menu_item_value',
                         args=OrderedDict(
                             menu_or_id=(kMenu, int, KspIntVar, AstBase),
                             idx=(int, KspIntVar, AstBase),
                             value=(int, KspIntVar, AstBase)))

    def __call__(self, menu_or_id: Union[kMenu, int],
                 idx: int, value: int):
        '''sets the value of a menu entry.
        <menu_or_id>
        the ID of the menu that you want to modify or kMenu instance
        <index>
        the index of the menu item'''
        if isinstance(menu_or_id, kMenu):
            menu_or_id = menu_or_id.id
        return super().__call__(menu_or_id, idx, value)

    def calculate(self, menu_id, idx, val):
        menu = ControlId.get_by_id(menu_id)
        idx = get_runtime_val(idx)
        val = get_runtime_val(val)
        if not isinstance(idx, int):
            raise TypeError('idx has to be instance of int')
        if not isinstance(val, int):
            raise TypeError('val has to be instance of int')
        menu._items[idx].value = val
        return kNone()


set_menu_item_value = SetMenuItemValue()


class SetMenuItemVisibility(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_menu_item_visibility',
                         args=OrderedDict(
                             menu_or_id=(kMenu, int, KspIntVar, AstBase),
                             idx=(int, KspIntVar, AstBase),
                             value=(int, KspIntVar, AstBase)))

    def __call__(self, menu_or_id: Union[kMenu, int],
                 idx: int, value: int):
        '''sets the visibility of a menu entry.
        <menu_or_id>
        the ID of the menu that you want to modify or kMenu instance
        <index>
        the index of the menu item
        <visibility>
        set to either 0 (invisible) or 1 (visible)'''
        if isinstance(menu_or_id, kMenu):
            menu_or_id = menu_or_id.id
        return super().__call__(menu_or_id, idx, value)

    def calculate(self, menu_id, idx, val):
        menu = ControlId.get_by_id(menu_id)
        idx = get_runtime_val(idx)
        val = get_runtime_val(val)
        if not isinstance(idx, int):
            raise TypeError('idx has to be instance of int')
        if not isinstance(val, int):
            raise TypeError('val has to be instance of int')
        menu._items[idx].visible = val
        return kNone()


set_menu_item_visibility = SetMenuItemVisibility()


class kSliderMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'slider'

        cls.value = init_value(cls)
        cls.default = init_default(cls)
        cls.picture = init_picture(cls)
        cls.automation_name = init_automation_name(cls)
        cls.allow_automation = init_allow_automation(cls)
        cls.automation_id = init_automation_id(cls)
        cls.mouse_behaviour = ControlPar('mouse_behaviour', cls,
                                         kArrInt, kParIntVar,
                                         int, 1,
                                         set_control_par,
                                         get_control_par,
                                         CONTROL_PAR_MOUSE_BEHAVIOUR)

        return cls

    def __call__(cls, min_val: int, max_val: int, *args,
                 **kwargs):

        obj = super().__call__(min_val, max_val, *args, **kwargs)
        value_min_max(obj, min_val, max_val)
        obj._decl_postfix = f'({min_val}, {max_val})'

        cls.value._init_control(obj, None, obj.var)
        cls.default._init_control(obj, None)
        cls.picture._init_control(obj, None)
        cls.automation_name._init_control(obj, None)
        cls.allow_automation._init_control(obj, None)
        cls.automation_id._init_control(obj, None)
        cls.mouse_behaviour._init_control(obj, None)

        return obj


class kSlider(KspNativeControl, metaclass=kSliderMeta):

    def __init__(self, min_val: int, max_val: int,
                 name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: object=None,
                 x: int=None, y: int=None,
                 width: int=None, height: int=None):
        super().__init__(name=name, persist=persist,
                         preserve=preserve,
                         parent=parent,
                         x=x, y=y, width=width,
                         height=height)


class kTextEditMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'text_edit'

        cls.picture = init_picture(cls)
        cls.picture_state = init_picture_state(cls)
        cls.text = init_text(cls)
        cls.font_type = init_font_type(cls)
        cls.textpos_y = init_textpos_y(cls)
        cls.text_alignment = init_text_alignment(cls)

        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(cls, *args, **kwargs)
        obj._decl_postfix = ''

        cls.picture._init_control(obj, None)
        cls.picture_state._init_control(obj, None)
        cls.text._init_control(obj, None)
        cls.font_type._init_control(obj, None)
        cls.textpos_y._init_control(obj, None)
        cls.text_alignment._init_control(obj, None)

        return obj


class kTextEdit(KspNativeControl, metaclass=kTextEditMeta):
    _var_type = kStr


class kValueEditMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'value_edit'

        cls.value = init_value(cls)
        cls.picture = init_picture(cls)
        cls.picture_state = init_picture_state(cls)
        cls.text = init_text(cls)
        cls.font_type = init_font_type(cls)
        cls.textpos_y = init_textpos_y(cls)
        cls.text_alignment = init_text_alignment(cls)
        cls.show_arrows = ControlPar('show_arrows', cls, kArrInt,
                                     kParIntVar, int, 1,
                                     set_control_par,
                                     get_control_par,
                                     CONTROL_PAR_SHOW_ARROWS)

        return cls

    def __call__(cls, min_val: int, max_val: int, display_ratio: int,
                 *args, **kwargs):

        if not isinstance(min_val, int):
            raise TypeError('"min_val" arg has to be instance of int' +
                            f'pasted {type(min_val)}')
        if not isinstance(max_val, int):
            raise TypeError('"max_val" arg has to be instance of int' +
                            f'pasted {type(max_val)}')
        if not isinstance(display_ratio, (int, bControlValueEditConst)):
            raise TypeError('"display_ratio" arg has to be instance' +
                            f' of {(int, bControlValueEditConst)}' +
                            f' pasted {type(display_ratio)}')

        obj = super().__call__(min_val, max_val, display_ratio,
                               *args, **kwargs)
        if isinstance(display_ratio, bControlValueEditConst):
            display_ratio = display_ratio._get_compiled()
        obj._decl_postfix = f'({min_val}, {max_val}, {display_ratio})'
        value_min_max(obj, min_val, max_val)

        cls.value._init_control(obj, None, obj.var)
        cls.picture._init_control(obj, None)
        cls.picture_state._init_control(obj, None)
        cls.text._init_control(obj, None)
        cls.font_type._init_control(obj, None)
        cls.textpos_y._init_control(obj, None)
        cls.text_alignment._init_control(obj, None)
        cls.show_arrows._init_control(obj, None)

        return obj


class kValueEdit(KspNativeControl, metaclass=kValueEditMeta):

    def __init__(self, min_val: int, max_val: int, display_ratio: int,
                 name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: object=None, x: int=None, y: int=None,
                 width: int=None, height: int=None):
        super().__init__(name=name, persist=persist,
                         preserve=preserve, parent=parent,
                         x=x, y=y,
                         width=width, height=height)


class kWaveFormMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'waveform'

        cls.bar_color = ControlPar(
            'bar_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_BAR_COLOR)
        cls.zero_line_color = ControlPar(
            'zero_line_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_ZERO_LINE_COLOR)
        cls.bg_color = ControlPar(
            'bg_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_BG_COLOR)
        cls.wave_color = ControlPar(
            'wave_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_WAVE_COLOR)
        cls.wave_cursor_color = ControlPar(
            'wave_cursor_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_WAVE_CURSOR_COLOR)
        cls.slicemarkers_color = ControlPar(
            'slicemarkers_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_SLICEMARKERS_COLOR)
        cls.bg_alpha = ControlPar('bg_alpha', cls, kInt,
                                  kParIntVar, int, 1,
                                  set_control_par,
                                  get_control_par,
                                  CONTROL_PAR_BG_ALPHA)

        return cls

    def __call__(cls, *args, **kwargs):

        obj = super().__call__(*args, **kwargs)
        obj._decl_postfix = '(1, 1)'

        cls.bar_color._init_control(obj, None)
        cls.zero_line_color._init_control(obj, None)
        cls.bg_color._init_control(obj, None)
        cls.wave_color._init_control(obj, None)
        cls.wave_cursor_color._init_control(obj, None)
        cls.slicemarkers_color._init_control(obj, None)
        cls.bg_alpha._init_control(obj, None)

        return obj


class GetWfProperty(BuiltInFuncInt):

    def __init__(self):
        super().__init__('get_ui_wf_property',
                         args=OrderedDict(
                             waveform='kWaveForm',
                             prop=bWaveFormPropConst,
                             idx=(int, KspIntVar, AstBase)))

    def __call__(self, waveform: 'kWaveForm',
                 prop: bWaveFormPropConst,
                 idx: Union[int, KspIntVar, AstBase]):
        '''returns the value of the waveform’s different properties.
        <waveform>
        kWaveForm instance
        <prop>
        the following properties are available:
        $UI_WF_PROP_PLAY_CURSOR
        $UI_WF_PROP_FLAGS
        $UI_WF_PROP_TABLE_VAL
        $UI_WF_PROP_TABLE_IDX_HIGHLIGHT
        $UI_WF_PROP_MIDI_DRAG_START_NOTE
        <idx>
        the index of the slice'''
        # waveform = waveform.var
        self._args['waveform'] = kInt
        self._wf = waveform
        waveform = waveform.var
        return super().__call__(waveform, prop, idx)

    def calculate(self, waveform, prop, idx):
        idx = get_runtime_val(idx)
        return self._wf._get_property(prop, idx)


get_ui_wf_property = GetWfProperty()


class SetWfProperty(BuiltInFuncInt):

    def __init__(self):
        super().__init__('set_ui_wf_property',
                         args=OrderedDict(
                             waveform='kWaveForm',
                             prop=bWaveFormPropConst,
                             idx=(int, KspIntVar, AstBase),
                             value=(int, KspIntVar, AstBase)))

    def __call__(self, waveform: 'kWaveForm',
                 prop: bWaveFormPropConst,
                 idx: Union[int, KspIntVar, AstBase],
                 value: Union[int, KspIntVar, AstBase]):
        '''sets different properties for the waveform control
        <waveform>
        kWaveForm instance
        <property>
        the following properties are available:
        $UI_WF_PROP_PLAY_CURSOR
        $UI_WF_PROP_FLAGS
        $UI_WF_PROP_TABLE_VAL
        $UI_WF_PROP_TABLE_IDX_HIGHLIGHT
        $UI_WF_PROP_MIDI_DRAG_START_NOTE
        <index>
        the index of the slice
        <value>
        the (integer) value'''
        self._args['waveform'] = kInt
        self._wf = waveform
        waveform = waveform.var
        return super().__call__(waveform, prop, idx, value)

    def calculate(self, waveform, prop, idx, value):
        idx = get_runtime_val(idx)
        self._wf._set_property(prop, idx, value)
        return -1


set_ui_wf_property = SetWfProperty()


class kWaveForm(KspNativeControl, metaclass=kWaveFormMeta):

    def __init__(self, name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: object=None, x: int=None, y: int=None,
                 width: int=None, height: int=None):
        super().__init__(name=name, persist=persist,
                         preserve=preserve, parent=parent,
                         x=x, y=y, width=width, height=height)
        self._zone = None
        self._props = \
            {UI_WF_PROP_PLAY_CURSOR.id: dict(),
             UI_WF_PROP_FLAGS.id: dict(),
             UI_WF_PROP_TABLE_VAL.id: dict(),
             UI_WF_PROP_TABLE_IDX_HIGHLIGHT.id: dict(),
             UI_WF_PROP_MIDI_DRAG_START_NOTE.id: dict()}

    def attach_zone(self, zone_id: int, flags: bWaveFormFlagConst):
        '''connects the corresponding zone to the waveform so that
        it shows up within the display
        <zone_id>
        the ID number of the zone that you want to attach to the
        waveform display
        <flags>
        you can control different settings of the UI waveform via
        its flags. The following flags are available:
        $UI_WAVEFORM_USE_SLICES
        $UI_WAVEFORM_USE_TABLE
        $UI_WAVEFORM_TABLE_IS_BIPOLAR
        $UI_WAVEFORM_USE_MIDI_DRAG
        Remarks
        • Use the bitwise .or. to combine flags.
        • The $UI_WAVEFORM_USE_TABLE and $UI_WAVEFORM_USE_MIDI_DRAG
        flags will only work if $UI_WAVEFORM_USE_SLICES is already set.'''
        zone_rt = get_runtime_val(zone_id)
        if hasattr(zone_id, '_get_compiled'):
            zone_id = zone_id._get_compiled()
        if hasattr(zone_id, 'expand'):
            zone_id = zone_id.expand()
        if hasattr(flags, '_get_compiled'):
            flags = flags._get_compiled()
        if hasattr(flags, 'expand'):
            flags = flags.expand()
        if KSP.is_compiled():
            Output().put(
                f'attach_zone({self.var._get_compiled()}, ' +
                f'{zone_id}, {flags})')
        self._zone = zone_rt

    @property
    def attached_zone(self):
        return self._zone

    def get_property(self, prop: bWaveFormPropConst, index: int):
        return get_ui_wf_property(self, prop, index)

    def set_property(self, prop: bWaveFormPropConst, index: int,
                     value: int):
        return set_ui_wf_property(self, prop, index, value)

    def _get_property(self, prop, idx):
        if not self._zone:
            raise RuntimeError('zone is not attached')
        try:
            out = self._props[prop.id][idx]
        except IndexError:
            out = -1
        return out

    def _set_property(self, prop, idx, value):
        if not self._zone:
            raise RuntimeError('zone is not attached')
        self._props[prop.id][idx] = value


class kTableMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'table'
        cls._def_width = 178
        cls._def_height = 18

        cls.value = ControlPar('value', cls, kArrInt,
                               kParArrIntVar, int, 1,
                               set_control_par_arr,
                               get_control_par_arr,
                               CONTROL_PAR_VALUE)
        cls.bar_color = ControlPar(
            'bar_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_BAR_COLOR)
        cls.zero_line_color = ControlPar(
            'zero_line_color', cls, kInt,
            kParIntVar, int, 1,
            set_control_par,
            get_control_par,
            CONTROL_PAR_ZERO_LINE_COLOR)
        cls.idx = ControlPar('idx', cls, kArrInt,
                             kParArrIntVar, int, 1,
                             set_control_par_arr,
                             get_control_par_arr,
                             NI_CONTROL_PAR_IDX)

        return cls

    def __call__(cls, size: int, val_range: int, *args, **kwargs):

        obj = super().__call__(*args, size=size, **kwargs)
        obj._decl_postfix = f'(1, 1, {val_range})'
        cls.value._init_control(obj, None, obj.var)
        cls.bar_color._init_control(obj, None)
        cls.zero_line_color._init_control(obj, None)
        cls.idx._init_control(obj, None)
        return obj


class kTable(KspNativeControl, metaclass=kTableMeta):
    _var_type = kArrInt


class kXyMeta(KspNativeControlMeta):

    def __new__(self, name, bases, dct):
        cls = super().__new__(self, name, bases, dct)
        cls._decl_name = 'xy'
        cls._def_width = 85
        cls._def_height = 40

        cls.value = ControlPar('value', cls, kArrInt,
                               kParArrIntVar, int, 1,
                               set_control_par_arr,
                               get_control_par_arr,
                               CONTROL_PAR_VALUE)
        cls.mouse_behaviour_x = ControlPar('mouse_behaviour_x',
                                           cls, kArrInt,
                                           kParArrIntVar, int, 1,
                                           set_control_par,
                                           get_control_par,
                                           CONTROL_PAR_MOUSE_BEHAVIOUR_X)
        cls.mouse_behaviour_y = ControlPar('mouse_behaviour_y',
                                           cls, kArrInt,
                                           kParArrIntVar, int, 1,
                                           set_control_par,
                                           get_control_par,
                                           CONTROL_PAR_MOUSE_BEHAVIOUR_Y)
        cls.mouse_mode = ControlPar('mouse_mode',
                                    cls, kArrInt,
                                    kParArrIntVar, int, 1,
                                    set_control_par,
                                    get_control_par,
                                    CONTROL_PAR_MOUSE_MODE)
        cls.cursor_picture = ControlPar('cursor_picture',
                                        cls, kArrStr,
                                        kParArrStrVar, str, 1,
                                        set_control_par_str_arr,
                                        get_control_par_str_arr,
                                        CONTROL_PAR_CURSOR_PICTURE)
        cls.hide_arr = ControlPar('hide_arr',
                                  cls, kArrInt,
                                  kParArrIntVar, int, 1,
                                  set_control_par_arr,
                                  get_control_par_arr,
                                  CONTROL_PAR_HIDE)
        cls.idx = ControlPar('idx', cls, kArrInt,
                             kParArrIntVar, int, 1,
                             set_control_par_arr,
                             get_control_par_arr,
                             NI_CONTROL_PAR_IDX)

        return cls

    def __call__(cls, size: int, *args, **kwargs):
        if size % 2 != 0:
            raise TypeError('size of xy has to be even')

        obj = super().__call__(*args, size=size, **kwargs)
        cls.value._init_control(obj, None, obj.var)
        obj._cursor_pictures = kArrStr(size=size, is_local=True)
        obj._cursor_hide = kArrInt(size=size, is_local=True)

        cls.mouse_behaviour_x._init_control(obj, None)
        cls.mouse_behaviour_y._init_control(obj, None)
        cls.mouse_mode._init_control(obj, None)
        cls.cursor_picture._init_control(obj, None, obj._cursor_pictures)
        cls.hide_arr._init_control(obj, None, obj._cursor_hide)
        cls.idx._init_control(obj, None)

        return obj


class kXy(KspNativeControl, metaclass=kXyMeta):
    _var_type = kArrReal
