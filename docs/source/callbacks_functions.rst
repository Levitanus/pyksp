***********************
callbacks and functions
***********************

callbacks
=========

.. warning:: callbacks usage API can be changed. Now they are blocking useful features

by default import ``from pyksp.compiler import *`` callbacks decorators are imported within namespace ``on``.

So two mechanics can be used:


.. code-block:: python

    @on.release
    def release_cb():
        some code



or if it more flexible at some points (I'm thinking of rejecting decorators at all, and leave only this one)


.. code-block:: python

    def release_cb():
        some code

    release_cb = on.release(release_cb)


I'm still thinking of how test them properly, and, hope, in the closest update callbacks question will be solved.

init callback
-------------

generally, everything not placed inside callback or function is init callback.
But if something is put in decorated function, it will be placed at the very end of init.

NI_CALLBACK_ID and NI_CALLBACK_TYPE
-----------------------------------

works in offline. So every callback execution new id will be recieved. NI_CALLBACK_TYPE will also be checked respective to their constants.
So, generally, this constant can be used in regular Python ``if``, not in ``If()`` at some cases. But this has not been tested in real project.


functions
=========

Let's remember how functions works in **SublimeKSP**:

* there is native ksp function within keyword ``function`` and without arguments
* there is ``clever`` function, which can not be called, but always will work as some sort of macro
* there is ``taskfunc``, which can be called, and can recieve args, but can not be inlined

so the last time i put them together was something like this:
::

    on ui_control (menu_working_regime)
        render_pad_area
    end on

    taskfunc render_pad_area override
        for i := 1 to PADS_ROWS_AMOUNT
            render_pad_area_line (i)
        end for
    end taskfunc
    function render_pad_area.func override
        for i := 1 to PADS_ROWS_AMOUNT
            render_pad_area_line.func (i)
        end for
    end function

    taskfunc render_pad_area_line (line) override
        render_pad_area_line.macro (line)
        render_pads_line (line, track)
    end taskfunc
    function render_pad_area_line.func (line) override
        render_pad_area_line.macro (line)
        render_pads_line.func (line, track)
    end function


Within **pyksp** things are also not as simple, as walk in the park, but much maintainable:

prototyping
-----------

Still the function in state of prototyping I recommend to start from the simple Python function, add or not add arguments to it, use or not use return values, use as many locals as You wish.

.. warning:: avoid of passing function objects as args. pyksp can't pass them through. It is still possible to invoke callables in place on the arguments places.

.. code-block:: python

    def myfunc(label, ui_ids, someint):
        local_str = 'some_text'
        ret_value = label.x
        # some ids job
        return ret_value

When logic is ready, it's time to think if Function has to be called somewhere. If has,
place decorator, and do some refactor for matching specification:

.. code-block:: python
    
    @func
    def myfunc(label_id: int, 
                ui_ids: kArg(int, 15), 
                someint: int, 
                local_str=kLoc(str), 
                ret_value=kOut(int, 2)):
        ret_value <<= get_control_par(label_id, 'x')
        # some ids job
        return None

what do we have now?
--------------------

* Now by default everywhere function is used, it will be called, within it's args being put to ``stack``
* If it invoked inside init it will be inlined with saving true local args
* for inlining it's code somewhere at some reason additional keyword-only argument ``inline=True`` has to be passed

.. warning:: if you're familiar with how taskfunc works, theese ``@func`` s work just the same. But can accept not only ``int``, but also ``str`` and ``float`` arguments, as well as all types of Ksp arrays. You can imagine how much code will take to put many args to func, be careful.

.. warning:: if function is inlined, args still will be put to stack for purpose of maintaining variable args amount without parsing the body code. I'll think if this mechanic can be improved.

specification
-------------

* All arguments (except of self, if method is being wrapped) has to be annotated with types of expecting arguments, as it expected by mypy.
* Annotations can be as simple: int, str, float as well as objects of special classes ``kArg``, ``kLoc``, ``kOut`` reccomended to use ``kArg`` instead of (``int``, ``str``, ``float``)
* ``kArg`` used as annotation. the first argument has to be (``int``, ``str`` or ``float``) and the second argument tells that KspArray with the specified size is expected
* ``kLoc`` used as default value of an argument. As ``kArg``, *type* is requeired and *size* is optional. inside the function attribute can be used as native KspArray or KspVar
* ``kOut`` used as defaul argument and has the same notation as ``kLoc`` and ``kArg``, but it can not accept basic ``int``, ``str`` or ``float`` objects. returns the last assigned value to the passed KspVar instead

.. note:: You can use return statement, but it will not be counted during code generation

.. hint:: You can pass a const argument instead of self, and name it self :D. It just has came to my mind, I'll think about constant args

.. tip:: If You want fake-local arg, You can specify ``KspVar`` (and ``KspArray`` ) object as default value of argument. **But be careful!** If function is defined outside of script.main function (for example, it is class method), things will go very bad. I'll think of checking if it happens.

