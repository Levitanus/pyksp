**********************
Datatypes and "syntax"
**********************

As KSP, pyksp has 6 basic datatypes:

+------------+----------+-------------------------+
| KSP        | API      | Python (reference-type) |
+============+==========+=========================+
| int var    | kInt     | int                     |
+------------+----------+-------------------------+
| str var    | kStr     | str                     |
+------------+----------+-------------------------+
| real var   | kReal    | float                   |
+------------+----------+-------------------------+
| int array  | kArrInt  | a bit more complicated  |
+------------+----------+                         |
| str array  | kArrReal |                         |
+------------+----------+                         |
| real array | kArrStr  |                         |
+------------+----------+-------------------------+

Folowing init arguments are valid:

.. code-block:: python

    var(value: reference_type=<default>,
        name: str, 
        preserve: bool=False, 
        is_local: bool=False, 
        persist: bool=False)

defaults for types:

+------+-----+
| int  | 0   |
+------+-----+
| str  | ''  |
+------+-----+
| real | 0.0 |
+------+-----+

.. danger:: Argument ``is_local`` has not to be ever used. It exsists just for internal compiler mechanics. It doesn't mean that variable will be local, it means variable will not be declared at all.

.. note:: for arrays ``value`` argument replaced by ``sequence`` argument (if they are used as positional there is no difference). It accepts only lists, and (for the purpose of speed) checks the type of first element in it. So be careful with multi-typed lists, exception can be raised faar away.

.. hint:: You can start within empty arguments, and add them at architecture and testing needs. For example, if no name is specified, variables are named automatically as kInt0, kInt1 etc.

But the most cases You don't need to use thees types, just preprocess values You need and paste them (or simple type the directly) to the ``kVar`` constructor:

.. code-block:: python

    kVar(value=None,
        name=None, 
        size=None,
        preserve=False,
        persist=False)

``kVar`` can be initialized by ``None`` arguments, or by ``None`` value, and it will return valid object at the first value assignement

+----------------+-----------------+
| pasted value   | resulted object |
+----------------+-----------------+
| int, kInt      | kInt            |
+----------------+-----------------+
| str, kStr      | kStr            |
+----------------+-----------------+
| float, kReal   | kReal           |
+----------------+-----------------+
| list of ints   | kArrInt         |
+----------------+-----------------+
| list of strs   | kArrStr         |
+----------------+-----------------+
| list of floats | kArrReal        |
+----------------+-----------------+

``kNone()`` is spetial singleton subclass of kInt. Still is doing nothing more, but returns ``-1``. But can be used in expressions like ``var is kNone()``

.. note:: functionality of ``kNone()`` will be extended to pass and react of built-in function properly. Also may be included additional mechanics of initializing variables within kNone(). Also kBool is expected to appear.



Syntax
======

still ``=`` symbol is not an oerator in Python, but, let's say, keyword of assigning object to name, it is bad idea to use it on the pyksp objects.
as assignement operator i've chosen ``<<=``, which works quite fine.
In case of other operators – all **arithmetic**, **comparisson** and **logical** operators works fine. If You are doing something wrong I hope You'll recieve understandable excetion.

+------------------------------+-------------------------------------------+
| variables methods            | resulted action                           |
+==============================+===========================================+
| ``var <<= value``            | assign value to var                       |
+------------------------------+-------------------------------------------+
| ``value <<= var``            | assign var.val to value                   |
+------------------------------+-------------------------------------------+
| ``var.val``                  | get value of var                          |
+------------------------------+-------------------------------------------+
| ``var.read()``               | place ``read_persisten_var(var)`` line[1] |
+------------------------------+-------------------------------------------+
| **kInt additional methods**  |                                           |
+------------------------------+-------------------------------------------+
| ``invar.inc()``              | call native KSP ``inc(var)`` funciton     |
+------------------------------+-------------------------------------------+
| ``invar.dec()``              | call native KSP ``dec(var)`` funciton     |
+------------------------------+-------------------------------------------+
| **arrays methods**           |                                           |
+------------------------------+-------------------------------------------+
| ``arr <<= val``              | error                                     |
+------------------------------+-------------------------------------------+
| ``arr[idx]``                 | get variable at array index[2]            |
+------------------------------+-------------------------------------------+
| ``arr.append(value)``        | append value to the end of array[3]       |
+------------------------------+-------------------------------------------+
| ``arr.extend(list[values])`` | the same, but for sequences               |
+------------------------------+-------------------------------------------+
| ``len(arr)``                 | constant current size of an array         |
+------------------------------+-------------------------------------------+

.. [1] if not ``persisten`` argument passed on construction, it will be added near the declaration line

.. [2] if idx > current length, and size is not specified, and is still init callback (basically, not a function or another callback) – size will be increased to the idx value, and future append methods will increase it on

.. [3] if called outside of callbacks or functions increases size of array and puts value into it. raises IndexError is called from callback or array with fixed size is full.