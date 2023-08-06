dff_calc
========

.. image:: https://img.shields.io/pypi/v/dff_calc.svg
    :target: https://pypi.python.org/pypi/dff_calc
    :alt: Latest PyPI version

.. image:: https://travis-ci.org.png
   :target: https://travis-ci.org
   :alt: Latest Travis CI build status

Simple dF/F calculation for neural calcium traces

Usage
-----
1. ``from dff_calc.df_f_calculation import DffCalculator``
2. Create an instance with an two-dimensional array, the rows being individual traces. Other parameters are
documented in the code.
3. Call ``.calc()`` on that instance. The returned array contains the calculated dF/F values.

Installation
------------
``pip install dff-calc``

Requirements
^^^^^^^^^^^^
Python 3.6+, numpy, pandas

Licence
-------

MIT

Authors
-------

`dff_calc` was written by `Hagai Har-Gil <hagaihargil@protonmail.com>`_, graduate student in `Dr. Pablo Blinder's Lab. <pblab.tau.ac.il/en>`_
