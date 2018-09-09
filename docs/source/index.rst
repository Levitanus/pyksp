.. pyksp documentation master file, created by
   sphinx-quickstart on Sun Sep  9 07:55:25 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to pyksp's documentation!
=================================

what is pyksp
-------------

It provides API for generating code from python source to NI Kontakt language: KSP.
This version of documentation asserts users familiar with KSP and Nills SublimeKSP compiler. This new compiler is made in endevour of continuing the Nills work, so I tried to take the best from "parent", improve it a bit, and give the freedom of architecture to the end-coder.

The key features of pyksp are:

* support of unit tests
* support of gui tests
* no language restrictions and much more bad-syntax architecture safety (still SublimeKSP is parse source and interprets every line, pyksp responds only for the "real KSP" part, the rest You cad do, whatever Python allows)
* intelligent compilation (while SublimeKSP can expand source to 200-300K or MUCH more lines of code, before optimize it, pyksp compiles exactly what it needs)
* pretty amount of functions are well-documented and coder has to look into the KSP reference a little bit more rarely
* gui programming becomes a little bit funnier :)
  
Full list of SublimeKSP vs pyksp (I like SublimeKSP) You can find in the respective section.

installation
------------

since release version 0.1 pyksp will be available via PyPi, but till now:

* clone repository to the local folder
* move to it in console or terminal
* print ``pip install -e pyksp``

.. hint:: I suppose, all we like SublimeText, so for the full experience i recommend to install **Anaconda** from package control. Someone can like MagicPython also.

.. caution:: do not use pyksp on big long-maintainable projects until it gets to release of version 0.1. Some syntax can be changed, some complicated bugs can ruin your work. Since 0.1 I'll assume compiler is quite ready, and will work on other parts of package

.. _helloworld:

a simple hello world:
---------------------

.. code-block:: python

    from pyksp.compiler import *
    from pyksp.compiler.classic_builtins import *


    @on.note
    def note_cb():
        message(EVENT_NOTE)


    @on.init
    def null_msg():
        message('')


    @func
    def switch(ids: kArg(int, 6), on_id: int):
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


    script = kScript(kScript.clipboard, 'hello world',
                     compact=False,
                     max_line_length=70)


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
            switch(kButton.ids, control.id)
            message(control.id)
        for idx, b in enumerate(buttons):
            b.grid(idx % 3, idx // 3)
            b.bound_callback(b_callback)
        with For(arr=kButton.ids) as seq:
            for item in seq:
                set_control_par_str(item, 'text', 'mybutton')


    script.main = foo
    script.compile()


.. important:: why ``from pyksp.compiler``? – because compiller is planned as part of an bigger package
.. important:: why ``classic_builtins``? – because when I stop to be lazy, and type a bit, there will be categorized built-ins module. And I don't know which You like the most


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   features_table.rst
   datatypes.rst
   callbacks_functions.rst
   condition_loops.rst
   built_ins.rst
   gui_system.rst
   logging_compilation.rst
   deprecated.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
