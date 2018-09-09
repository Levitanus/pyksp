***********************
Compilation and logging
***********************

logging
=======

``message`` function has been updated to accept many arguments, and keyword arg ``sep: str=' '``.
It doesn't mean it has to be used for debug :)

SublimeKSP logger was copied as one behaviour of ``kLog`` object.

``kLog`` can be initialized only once, within positional arg ``type`` and optional ``path`` (later – ``label``)
strings are put to log by ``logpr(*args, sep=' ')`` function.

.. note:: if kLog() is not initialized, logpr is doing nothing

+------------+--------------------+------------------------------------------------------------+
| type arg   | path arg           | behaviour of logpr()                                       |
+============+====================+============================================================+
| kLog.array | None               | similar to SKSP print(), array is saved to the data folder |
+------------+--------------------+------------------------------------------------------------+
| kLog.array | local or full path | similar to SKSP print()                                    |
+------------+--------------------+------------------------------------------------------------+
| kLog.pgs   | None               | puts lines to pgs_str_key                                  |
+------------+--------------------+------------------------------------------------------------+

for using pgs – place this code to the one of script slots:
::

    on init
      set_script_title("log_viever")
      declare ui_label $log_label(6, 4)
      set_control_par_str(get_ui_id($log_label),$CONTROL_PAR_TEXT,...\
      "log started")
    end on

    on pgs_changed
      if (pgs_get_key_val(_log_flag,0)=1)
        pgs_set_key_val(_log_flag,0,0)
        set_control_par_str(get_ui_id($log_label),$CONTROL_PAR_TEXTLINE...\
        ,pgs_get_str_key_val(_log_msg))
      end if
      if (pgs_get_key_val(_log_flag,0)=2)
        pgs_set_key_val(_log_flag,0,0)
        set_control_par_str(get_ui_id($log_label),$CONTROL_PAR_TEXT,...\
        "log started")
      end if
    end on


Compilation
===========

``kScript()`` Is used for generating code of all API calls used in project.

.. warning:: All KSP objects, attempted to appear in code has to be placed inside script main method.

**args:**

.. code-block:: python

    kScript(self, out_file: str, title: str=None,
                compact=False, max_line_length=79,
                indents=False,
                docstrings=False) -> None:

* out_file can be as str filename with .txt ending as well as ``Kscript.clipboard``
    * if filename is not full path, the __main__.__file__ path will be used.
    * if out_file is ``Kscript.clipboard``, compiled code will be copied to the exchange buffer
* title is script title to be set via set_script_title() func
* if compact is True, all variable names will be hashed
* with max_line_length being not None, lines with length > max_line_length will be wrapped to fit it. currently, lines with "quoted strings" are not wrapped
* indents and docstrings are out of work

**Example:**

.. code-block:: python

    script = kScript(r'C:/file.txt',
                         'myscript', max_line_length=70, compact=True)
    def foo():
        mw = kMainWindow()
        buttons_area = kWidget(parent=mw)
        buttons_area.place_pct(20, 10, 50, 80)
        ba_bg = kLabel(parent=buttons_area)
        ba_bg.pack(sticky='nswe')
        ba_bg.text <<= ''
    script.main = foo
    script.compile()
