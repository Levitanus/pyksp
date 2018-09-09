**********
GUI system
**********

.. epigraph::

    *"It's personal painful corn. So GUI has been done at the first quele."*

The folowing widgets can be used as simple old ui_controls:

* kButton
* kSlider(min: int, max: int)
* kSwitch
* kKnob(min: int, max: int, display_ratio)
* kMenu
* kLabel
* kLevelMeter
* kTable(size: int, val_range: int)
* kValueEdit(min_val: int, max_val: int, display_ratio: int)
* kTextEdit
* kWaveForm
* kXy(size: int)
* kFileSelector
  
But much more fun can be taken, within using of ``kWidget`` class.

kWidget
=======

.. note:: native controls are subclasses of kWidget, so they has the same methods


Is a base class for all controls, as native, as well as future complex ``preprocessor`` controls.

It's pretty like tkInter Frame or qt QWidget.

.. code-block:: python

    class kWidget(metaclass=WidgetMeta):
        '''base class for all KSP widgets, including built-ins like
        kButton or kLabel (ui_button & ui_label). Behaves like tkinter Frame.
        Can be parented by kMainWindow or another kWidget instances'''

        def __init__(self, parent: object=None, x: int=None, y: int=None,
                     width: int=None, height: int=None) -> None:

add_grid()
----------

makes 'ceils' in borders of widget. Childs can be placed inside them.
offsets mean pixels from **widget's** sides to the sides of the grid

.. code-block:: python

    add_grid(self, columns: int=1, rows: int=1,
                 top_offset: int=0, bottom_offset: int=0,
                 left_offset: int=0, right_offset: int=0):


**Within parent specified, several methods becomes available:**

pack()
------
puts widget in the borders of parent. Sticky can cosists of 'nswe'.

* with one side selected places border of widget to the side.
* with 'ne', 'nw', 'se', 'sw' places widget to the corner
* with 'ns', 'we', 'nswe', and similar combinations stretches widget to borders of parent

.. code-block:: python

    def pack(self, sticky: str=''):

grid()
------
places object to the grid ceil (zerobased) or ceils if columnspan or rowspan are used.
offsets are pixels from the **ceil** sides to the control sides.

.. code-block:: python

    grid(self, column: int, row: int,
             columnspan: int=1, rowspan: int=1,
             top_offset: int=0, bottom_offset: int=0,
             left_offset: int=0, right_offset: int=0):

place()
-------
place widget depends on parent position.

* x, y, width, height are counted in pixels 
* x_pct, y_pct, width_pct, height_pct – in percents

.. code-block:: python

    def place(self, x: Optional[int]=None, y: Optional[int]=0,
              width: Optional[int]=None, height: Optional[int]=None,
              x_pct: Optional[int]=None, y_pct: Optional[int]=0,
              width_pct: Optional[int]=None,
              height_pct: Optional[int]=None):

place_pct()
-----------

the same as ``place()``, but all arguments are in percents

.. code-block:: python

    def place_pct(self, x: Optional[int]=None, y: Optional[int]=None,
                  width: Optional[int]=None, height: Optional[int]=None):

childs
------

universal property, returns list of all childs objects *(!not ids)* (including preprocessor widgets)

Native controls
===============

Some changes has been made to native controls:

.. warning:: look carefully at the code below:

.. code-block:: python

    button = kButton() # != declare ui_button $button
    x <<= button # Error! 
    x <<= button.var # ok!
    x <<= button.value # ok!

* Opposite to KSP, returned object is not an valuable variable, it's KspNativeControl instance. So if You need to access the variable, represents ui_control, use control.var attribute. 
* But there is no situation, var is really needed, because all native functions, that accept control variables now are methods of specific control object. For example,  there is no built_in function ``add_menu_item(menu, string, value)``, there is method ``menu.add_item(string, value)``.
* Also, control par value is bounded to the control var.
* Id of control can be retrieved within control.id attribute. Id is the same variable object as other KSP variables, so if You want to print it's value, use control.id.val
* Also, id is item of array %_all_ui_ids, which is made automatically.
* Also, every subclass of KspNativeControl has it's own array of ids, can be retrieved by cls.ids. It can be useful to subclass desired control for not using additional array for getting id's of particular controls group.
* Also in testing purpose (do not use it in production) ``compiler.bi_ui_controls.ControlId`` class can be imported. it has static method to retrieve control object from it's id.
* parameters x, y, width, height can be assigned as constant for a first time in the init callback. Even with assigning within KSP variable, they will be applied without additional lines, in global for-loop, sets all them to controls. If the first assignment is done by set_control_par() func, line will be added.
  
.. warning:: if control par has not been set, spetial error will be raised. Even at compilation (shoudnt it?)

.. note:: x, y, width and height parameters are unique, because they are assigned almost everytime. If other params (especcially strings) are made this way, there will not be economy. I'm still thinking if can be done something better, than invocation os set_control_par() in For loop on the cls.ids array.

.. tip:: functions set_control_par, get_control_par etc. can accept shorhand of CONTROL_PAR, placed as ``'string'``. For example: ``set_control_par(control.id, 'text', 'my control')``.

.. caution:: there is no syntax, shorter the listed above for assigning parameter to id (like it is in SublimeKSP: id -> param)


default (see special at the top of page) arguments per native control object initialisation:

.. code-block:: python 

    def __init__(self, name: Optional[str]=None,
                 persist: bool=False, preserve: bool=False,
                 parent: object=None, x: int=None, y: int=None,
                 width: int=None, height: int=None):

Subclassing Widgets
===================

I reccomended this approach, but it hasn't been tested at all yet.

The problems appears in the fact of contructing controls via metaclasses (also within ``__call__`` method). So, something can be unavalable imside the __init__ of control. The best way – is to subclass the both: metaclass of particular control class, and the class itself. But it's.... *durty*.

So, till this section is not changed my recomendation for subclassing is just subclassing, withoud doing anything in init, or, at least without changing the __init__ signature. And via calling the super().__init__() of course.

.. note:: about the signature: it definitely can be longer than original, but not shorter %)
