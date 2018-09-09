*************
KSP built-ins
*************

.. note:: built-ins are not included in the __init__.py of compiler, they has to be imported separately via ``from pyksp.compiler.classic_builtins impoprt *``


From the one side, everything is prosaic: arguments types are checked, lines are put to the compiled code; if function can return something meaningfull – it will, if not – kNone() will be returned.

*But things became interesting when values are passed to them.*

1. Every built-in's value can be assigned via ``BI_VAR.set_value()`` function, and it can be retrieved later. 
2. Behind several built-in functions are classes, that maintain them [1]_
3. array and math functions, of course, works (except of save and load array, but they produces their ``NI_ASYNC_ID``)
4. Also, every built-in variable or constant has unique ``id``. It is not useful as part of result code, but can be compared to the returned constant

.. code-block:: python

    self.assertTrue(get_key_color(0) == KEY_COLOR_NONE.id)
    set_key_color(0, KEY_COLOR_BLUE)
    self.assertFalse(get_key_color(0) == KEY_COLOR_NONE.id)
    self.assertTrue(get_key_color(0) == KEY_COLOR_BLUE.id)
    set_key_type(3, NI_KEY_TYPE_DEFAULT)
    self.assertEqual(get_key_type(3), NI_KEY_TYPE_DEFAULT.id)

.. note:: hope, to the release of 0.1 version, all built-ins will be able to be tested. Midifile object is almost ready, the note events are next. Probably within additional API.

.. [1] For example, pgs functions can store values and check keys; keyboard keys function sets 'real' keys properties, control_pars is separate long subject.
