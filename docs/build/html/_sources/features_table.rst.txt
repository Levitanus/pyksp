***************************
Features (or SKSP vs pyksp)
***************************

The thing has to be counted is that pyksp is not a compiler. If You just type code and compile it, it will not make any key difference of what SKSP does.
But even now and even on compilation it counts something more:
for example it raises exceptions if id passed to the ``set_control_par`` is not a valid id of ui control. Or it knows exactly the length of every array, and runs every for-loop entirely, so exception will be raised at the wrong index.

On the current stage, if You pass code to the SKSP You can be sure about 95% that it's static semantic is right (i mean, that Kontakt will not reject your code at pressing the apply button). Pyksp can not give that warrancy yet, it's very early alpha release. But when we sure it's built-ins API is correct, within pasting the code (even without unit-tests inside python) we can be calm about many runtime things, we can not be calm within just static analyses.

The second advantage is that every object (even built-ins like EVENT_NOTE) is alive object. So it can be tested inside python. A huge amount of code can be written without pasting to Kontakt. And every time tests can be batch-checked.

The third adventage is Python. Many types of pre-calculations and many ways of keeping the project data can be applied. Only restriction is pyksp is still a preprocessor, but the power of this preprocessing is restricted only by Your imagination. 

.. note:: Still knowing of how code will be generated and what is good KSP practice and what is bad is required.



now the blitz comparisson table
===============================

+---------------------------------------------------------+-------------------+---------------------------+
| feature                                                 | pyksp             | SublimeKSP                |
+=========================================================+===================+===========================+
| full KSP backvard-copability                            | not               | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| improved functions                                      | yes               | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| variable amount of functions arguments                  | yes               | no                        |
+---------------------------------------------------------+-------------------+---------------------------+
| returns from functions                                  | yes               | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| multi-typed functions                                   | every of 6        | only in inlined functions |
+---------------------------------------------------------+-------------------+---------------------------+
| undefined type at declaration                           | yes               | buggy                     |
+---------------------------------------------------------+-------------------+---------------------------+
| 'lists': undefined size of arrays and appending in init | yes               | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| constant as size of arrays                              | every array       | only lists and constants  |
+---------------------------------------------------------+-------------------+---------------------------+
| arrays concatination                                    | not yet           | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| shorten control pars                                    | yes               | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| iterative pre-processing                                | yes               | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| logging                                                 | improved          | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| advanced layout and custom 'widgets'                    | yes               | not                       |
+---------------------------------------------------------+-------------------+---------------------------+
| structs                                                 | classes?          | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| families                                                | subclasses?       | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| ui-arrays                                               | see 'hello world' | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| constant blocks                                         | not as syntax     | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| persisten shorthand                                     | yes               | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| multidimentional arrays                                 | needs to think    | yes                       |
+---------------------------------------------------------+-------------------+---------------------------+
| preprocessor variables are mutable                      | yep               | nope                      |
+---------------------------------------------------------+-------------------+---------------------------+
