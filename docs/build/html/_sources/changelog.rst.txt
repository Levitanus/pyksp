*********
Changelog
*********

V 0.09 alpha
============

fixed
-----

* removed brackets of non-bracket function (like exit)
* fade_in and fade_out generation
* some built_ins bodies
* missed ``set_ui_color(color: int)`` returned

added
-----

* kScript now supports indents. parameter acceps int value of indentation level
* new function ``comment(comment: str)``, allows to place comments to the exported code
* new decorator ``@docstring`` places the docstring of wrapped function to the generated code every time it's invocated
* both of them are sensitive to the kScript param docs
  
changed
-------

* kScript parameter ``docstrings`` now is ``docs``