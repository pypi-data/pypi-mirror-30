+++++++++++++++++++++++++++++++++++++
backports.range class from Python 3.3
+++++++++++++++++++++++++++++++++++++

|travis| |codecov|

|pypi| |pypistatus| |pypiversions| |pypiimplementations|

Backports the Python 3.7 ``range`` class as a replacement for python 2.X ``range``
functions (and the Python pre-3.7 ``range`` class).
The ``range`` class is similar to ``xrange`` in that its values are computed on demand -
however, the ``range`` class is also a lazy sequence:
it supports indexing, membership testing and other sequence features.

Thus, it can be used to replace both ``range`` and ``xrange``.


.. |travis| image:: https://travis-ci.org/maxfischer2781/backports.range.svg?branch=master
    :target: https://travis-ci.org/maxfischer2781/backports.range
    :alt: Unit Tests

.. |pypi| image:: https://img.shields.io/pypi/v/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Package

.. |pypistatus| image:: https://img.shields.io/pypi/status/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Status

.. |pypiversions| image:: https://img.shields.io/pypi/pyversions/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Versions

.. |pypiimplementations| image:: https://img.shields.io/pypi/implementation/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Implementations

.. |codecov| image:: https://codecov.io/gh/maxfischer2781/backports.range/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/maxfischer2781/backports.range
  :alt: Code Coverage

.. contents:: **Table of Contents**
    :depth: 2

Features
--------

This implementation provides all features introduced and documented in
python 3.6, and implements the ``collections.abc.Sequence`` interface of Python 3.5 [#seq35]_ and later.
The ``range`` class is available as ``backports.range.range`` -
you can import it to a separate name or replace the builtin ``range`` and/or ``xrange``.

.. code::

    # import for explicit usage
    from backports.range import range as range3
    values = range3(499, 501)
    # as a lazy, reusable iterable
    print(', '.join(values), 'and', ', '.join(values))
    # as a lazy sequence
    print(500 in values, 501 in values)
    print(values[2], len(values))

All objects are available by default in a pure python implementation.
In addition, an optional, optimized implementation is available using `Cython`_.

Performance
^^^^^^^^^^^

The ``backports.range`` is adequate in performance for most applications.
It is comparable in iteration speed to builtins when using `PyPy`_ or `Cython`_.
For small ranges of less than 1000 elements, there is some small overhead.
This should not be noticeable in all but the most high-performance applications.

When using CPython (aka plain ``python``), pure python mode is considerably slower than the builtins.
Again, this should not matter for most applications, but the use of `Cython`_ is **strongly** advised.

Benchmark for ``[a for a in range(...)]``
.........................................

=============== ================= ==================
Interpreter     vs Builtin range  vs Builtin xrange
=============== ================= ==================
Py2                      50 - 100            20 - 50
Py3                       25 - 30                ---
Py2 + Cython                3 - 6            1.0 - 3
Py3 + Cython            1.0 - 1.2                ---
PyPy2                   1.4 - 1.6          1.6 - 2.3
PyPy3                   1.0 - 1.1                ---
=============== ================= ==================

Cython Optimizations
^^^^^^^^^^^^^^^^^^^^

The backport features a `Cython`_ implementation.
It is transparently used when creating a ``range`` class.
It optimises operations which are purely in the C ``long long`` range. [#clonglong]_

All `Cython`_ optimizations are optional.
They are automatically made available if `Cython`_ is installed.

Compatibility
-------------

- Features are tested against the Python 3.6 unittests for ``range``.

- The following python versions are tested explicitly:

  - CPython (aka python): ``2.6``, ``2.7``, ``3.2``, ``3.3``, ``3.4``, ``3.5``, ``3.6``, ``3.7-dev``

  - `Cython`_: All versions supported by cpython

  - `PyPy`_: pypy2, pypy3

- Some additional features are available for compatibility:

  - Instances of ``backports.range.range`` compare equal to equivalent ``builtin.range`` instances (new in Python 3.3)

  - The ``index`` method is compliant with the Python 3.5+ specification of ``collections.abc.Sequence``. [#seq35]_

- Some features depending on language features or other modules may not be
  available or work differently:

  - Comparing ``range`` against other types does not throw ``TypeError`` in python 2.X.

  - Python implementations use custom optimisations at compile time when provably encountering a *builtin* range.
    These *cannot* be replicated by the backport.
    Note that this is only noticeable in highly optimised code, which should be hand-optimised anyway.

Status and Contributing
-----------------------

For all practical purposes, the backport is complete.
The ``range`` class satisfies all unittest of Python 3.7, as well as several tests for compatibility.
It is a fully featured replacement suitable even for recent versions of Python.

Performance should be more than adequate for any use case.
The backport is comparable or even equal in performance to builtins.

If you encounter any problems, please head over to the `issue tracker`_.
Feel free to submit a pull request if you think the codebase can be improved.

Notice
------

    This packages includes parts of the python documentation (http://www.python.org)
    Copyright (C) 2001-2016 Python Software Foundation.
    Licensed under the Python Software Foundation License.

.. [#seq35] As of Python 3.6, the builtin ``range`` class is not compliant
            with the Python 3.5 specification of ``collections.abc.Sequence``.
            See `Issue 28197 <http://bugs.python.org/issue28197>`_

.. [#clonglong] The ``long long`` type should fill any current CPU architecture (read 64bit).
                Since Python cannot parallelize instructions,
                this should provide maximum range with optimal performance for small values.

.. _Cython: http://cython.org

.. _PyPy: http://pypy.org

.. _issue tracker: https://github.com/maxfischer2781/backports.range/issues
