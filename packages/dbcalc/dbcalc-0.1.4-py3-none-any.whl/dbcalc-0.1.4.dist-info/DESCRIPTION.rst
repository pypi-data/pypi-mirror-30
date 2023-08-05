dbcalc
======

Conversion tool to do power <-> dB calculations. PARAMS is a list of space-separated values depending
on the mode (``i``, ``o`` or ``d``) selected.

* ``i`` — calculate input power from the PARAMS output power and dB
* ``o`` — calculate output power from the PARAMS input power and dB
* ``d`` — calculate dB from the PARAMS output power and input power

E.g.: to calculate the output power, given 1W of input power and 3dB loss

.. code:: sh

    $ dbcalc o 1 -3
    0.5011872336272722

Notice that the result has a newline character appended.

