from abstract import KSP
from abstract import Output


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
        if skin_offset is not None:
            Output().put(f'set_skin_offset({skin_offset})')
        Output().put(f'set_ui_width_px({width})')
        Output().put(f'set_ui_height_px({height})')
        self._x = 0
        self._y = 0

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class WidgetGrid(KSP):
    '''stores ceils x, y, width, height
    returns them by get_ceil(column, row)'''

    def __init__(self, obj, columns: int=1, rows: int=1,
                 top_offset: int=0, bottom_offset: int=0,
                 left_offset: int=0, right_offset: int=0):
        self._obj = obj
        self._columns_am = columns
        self._rows_am = rows
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


class kWidget(KSP):
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
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._grid = None

    def _get_x(self):
        '''x pos of widget in pixels'''
        if self._x is None:
            raise AttributeError('x position is not set')
        return self._x

    def _set_x(self, value: int):
        '''x pos of widget in pixels'''
        self._x = value

    x = property(fget=_get_x, fset=_set_x,
                 doc='x pos of widget in pixels')

    def _get_y(self):
        '''y pos of widget in pixels'''
        if self._y is None:
            raise AttributeError('y position is not set')
        return self._y

    def _set_y(self, value: int):
        self._y = value

    y = property(fget=_get_y, fset=_set_y,
                 doc='y pos of widget in pixels')

    def _get_width(self):
        '''width of widget in pixels'''
        if not self._width:
            raise AttributeError('width is not set')
        return self._width

    def _set_width(self, value: int):
        '''width of widget in pixels'''
        self._width = value

    width = property(fget=_get_width, fset=_set_width,
                     doc='width of widget in pixels')

    def _get_height(self):
        '''height of widget in pixels'''
        if not self._height:
            raise AttributeError('height is not set')
        return self._height

    def _set_height(self, value: int):
        '''height of widget in pixels'''
        self._height = value

    height = property(fget=_get_height, fset=_set_height,
                      doc='height of widget in pixels')

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

        def center_w():
            return ((p_x + p_w) / 2) - (self.width / 2)

        def center_h():
            return ((p_y + p_h) / 2) - (self.height / 2)

        if 'e' in sticky:
            if 'w' in sticky:
                self.width = p_w
            else:
                self.x = p_x + p_w - self.width
        if 's' in sticky:
            if 'n' in sticky:
                self.height = p_h
            else:
                self.y = p_y + p_h - self.height
        if 'w' in sticky:
            self.x = p_x
        if 'n' in sticky:
            self.y = p_y
        if 's' not in sticky and 'n' not in sticky:
            self.y = center_h()
        if 'e' not in sticky and 'w' not in sticky:
            self.x = center_w()

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

        self.x = l + left_offset
        self.y = t + top_offset
        self.width = ((r - l) * columnspan) - left_offset - right_offset
        self.height = ((b - t) * rowspan) - top_offset - bottom_offset

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
            self.x = self._parent.x + x
        if y:
            self.y = self._parent.y + y
        if width:
            self.width = width
        if height:
            self.height = height

        if x_pct:
            if x_pct < 0 or x_pct > 100:
                raise AttributeError(
                    'x_pct has to be between 0 and 100')
            self.x = int(self._parent.x +
                         (self._parent.width * x_pct / 100))
        if y_pct:
            if y_pct < 0 or y_pct > 100:
                raise AttributeError(
                    'y_pct has to be between 0 and 100')
            self.y = int(self._parent.y +
                         (self._parent.height * y_pct / 100))
        if width_pct:
            if width_pct < 0 or width_pct > 100:
                raise AttributeError(
                    'width_pct has to be between 0 and 100')
            self.width = int(self._parent.width * width_pct / 100)
        if height_pct:
            if height_pct < 0 or height_pct > 100:
                raise AttributeError(
                    'height_pct has to be between 0 and 100')
            self.height = int(self._parent.width * height_pct / 100)

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
