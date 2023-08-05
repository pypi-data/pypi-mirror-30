"""
pyutils_sh
============

An assortment of Python utilities for my personal projects. For example, 
there are functions for aggregating different types of survey data, 
grading scantron exams, calculating various statistics, and other general 
Python helper functions.

Documentation
-------------
Documentation is available via docstrings provided with the code, and an
online API reference found at
`ReadTheDocs <http://pyutils-sh.readthedocs.io>`_.

To view documentation for a function or module, first make sure the package
has been imported:

  >>> import pyutils_sh

Then, use the built-in ``help`` function to view the docstring for any
function or module:

  >>> help(pyutils_sh.exam.grade_scantron)

Modules
-------
exam
    Functions for aggregating different types of data from school exams (e.g. student grades)
gaze
    Functions for analyzing gaze/eye-tracking data
survey
    Tools for aggregating and analyzing data from different surveys
utils
    General utility functions used for general Python programming
"""

import pyutils_sh.exam
import pyutils_sh.gaze
import pyutils_sh.survey
import pyutils_sh.utils
