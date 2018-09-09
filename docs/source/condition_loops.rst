********************
Conditions adn Loops
********************

When using conditions or loops take in account what do You expect:

* if it is **preprocessor** logic (e.g. ``if (<condition>)`` : **use** some code); *regular* for, while and if has to be used
* if it is **runtime** logic (e.g. ``with If (<value of var == 1>)`` : **run** some code); *special* classes has to be used

all special classes are context-managers e.g. they are used within folowing syntax:

.. code-block:: python

    with If(<some condition>):
        do some code

If() -> Else()
==============

Example:

.. code-block:: python

    with If((x == y) & (x != 2)):
        check()
        x += 1
    with If(y == 1):
        check()
        x += 1
        with If(y != 2):
            check()
            x += 1
    with Else((x != y) & (x == 1)):
        check()
        x += 1
    with Else():
        check()
        y += 1

* The first line inside the context block has to contain ``check()`` function for proper execution under tests.
* Under tests works as normal if-else(elif) condition. if Else has bool argument it evaluates as elif.
* every single bool expression has to be placed inside ``(round brackets)``
* instead of using ``and`` and ``or`` keywords, use bitwise ``&`` and ``|``

.. note:: outside the If-Else and While ``&`` and ``|`` are just bitwise ``.and.`` and ``.or.``


Select() -> Case()
==================

Example:

.. code-block:: python

    with Select(x):
        with Case(1):
            check()
            y += 1
        with Case(2):
            check()
            y += 2
            with Select(y):
                with Case(2):
                    check()
                    y += 1
                with Case(3):
                    check()
                    CondFalse()


For()
=====

Works as python foreach: ``for val in Iterable`` as well as for-range: ``for val in range(start, [stop, [step]])``

ForEach Example:

.. code-block:: python

    with For(arr: KspNativeArray=array) as seq:
        for val in seq:
            # code

ForRange Example:

.. code-block:: python

    with For(start: int[, stop: int[, step: int]]) as seq:
        for val in seq:
            # code

.. warning:: do not use enumerate and zip not inside, not outside the loop. Inside You'll get constant values as idx or second array; outside You'll probably get an Error.


While()
=======

Example:

.. code-block:: python

    with While() as w:
        while w(lambda x=x, y=y: x != y):
            with If(y != 10):
                check()
                y += 1
            x += 1


Yep, a little bit tricky) But while is much rarely used than for :)

.. warning:: Do not use CondFalse() and Brake() inside while. They'll works in tests, but will not be counted at compilation.


Break(), CondFalse() and check()
================================

Break()
-------

Function to break For() loop. Equal to val = len(seq)

CondFalse
---------

Function works as operator continue in python. For testing purpose, does not translates to KSP.

check()
-------

Function for proper work of conditions under tests. Has to be on the first line of every context block.
