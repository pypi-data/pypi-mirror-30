import builtins
import collections as _abc
cimport cython
from cpython.number cimport PyNumber_Index as index

from .types cimport range_bound
from .cyrange_iterator cimport llrange_iterator

# default integer __eq__
# python 2 has THREE separate integer type comparisons we need to check
try:
    _int__eq__s = set((int.__eq__, long.__eq__, bool.__eq__))
except NameError:
    _int__eq__s = set((int.__eq__,))

# get the builtin type of range class
if type(builtins.range) == type:
    _builtin_range_class = builtins.range
else:
    _builtin_range_class = None


cdef class range(object):
    """
    Object that produces a sequence of integers from start (inclusive) to
    stop (exclusive) by step.

    The arguments to the range constructor must be integers (either built-in
    :class:`int` or any object that implements the ``__index__`` special
    method).  If the *step* argument is omitted, it defaults to ``1``.
    If the *start* argument is omitted, it defaults to ``0``.
    If *step* is zero, :exc:`ValueError` is raised.

    For a positive *step*, the contents of a range ``r`` are determined by the
    formula ``r[i] = start + step*i`` where ``i >= 0`` and
    ``r[i] < stop``.

    For a negative *step*, the contents of the range are still determined by
    the formula ``r[i] = start + step*i``, but the constraints are ``i >= 0``
    and ``r[i] > stop``.

    A range object will be empty if ``r[0]`` does not meet the value
    constraint. Ranges do support negative indices, but these are interpreted
    as indexing from the end of the sequence determined by the positive
    indices.

    Ranges containing absolute values larger than :data:`sys.maxsize` are
    permitted but some features (such as :func:`len`) may raise
    :exc:`OverflowError`.

    Range examples::

       >>> list(range(10))
       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
       >>> list(range(1, 11))
       [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
       >>> list(range(0, 30, 5))
       [0, 5, 10, 15, 20, 25]
       >>> list(range(0, 10, 3))
       [0, 3, 6, 9]
       >>> list(range(0, -10, -1))
       [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
       >>> list(range(0))
       []
       >>> list(range(1, 0))
       []

    Ranges implement all of the :ref:`common <typesseq-common>` sequence operations
    except concatenation and repetition (due to the fact that range objects can
    only represent sequences that follow a strict pattern and repetition and
    concatenation will usually violate that pattern).

    The advantage of the :class:`range` type over a regular :class:`list` or
    :class:`tuple` is that a :class:`range` object will always take the same
    (small) amount of memory, no matter the size of the range it represents (as it
    only stores the ``start``, ``stop`` and ``step`` values, as well as its length,
    calculating individual items and subranges as needed).

    Range objects implement the :class:`collections.abc.Sequence` ABC, and provide
    features such as containment tests, element index lookup, slicing and
    support for negative indices (see :ref:`typesseq`):

       >>> r = range(0, 20, 2)
       >>> r
       range(0, 20, 2)
       >>> 11 in r
       False
       >>> 10 in r
       True
       >>> r.index(10)
       5
       >>> r[5]
       10
       >>> r[:5]
       range(0, 10, 2)
       >>> r[-1]
       18

    Testing range objects for equality with ``==`` and ``!=`` compares
    them as sequences.  That is, two range objects are considered equal if
    they represent the same sequence of values.  (Note that two range
    objects that compare equal might have different :attr:`~range.start`,
    :attr:`~range.stop` and :attr:`~range.step` attributes, for example
    ``range(0) == range(2, 1, 3)`` or ``range(0, 3, 2) == range(0, 4, 2)``.)

    :note: Instances of :py:class:`~backports.range.range` compare
           based on values even against builtin :py:class:`range` instances.

    .. versionchanged:: 3.7
        Instances of :py:class:`~backports.range.range` always use the
        most recent specifications.

    .. versionchanged:: 3.2
        Implement the Sequence ABC.
        Support slicing and negative indices.
        Test :class:`int` objects for membership in constant time instead of
        iterating through all items.

        :note: Instances of :py:class:`~backports.range.range` test membership
               in constant time for any object inheriting equality (``__eq__``)
               from any of :class:`int`, :class:`long` or :class:`bool`.

    .. versionchanged:: 3.3
        Define '==' and '!=' to compare range objects based on the
        sequence of values they define (instead of comparing based on
        object identity).
    """
    # docstring taken from https://docs.python.org/3/library/stdtypes.html
    def __init__(self, start_stop, stop=None, step=None):
        cdef:
            range_bound _len
            range_bound _start
            range_bound _stop
            range_bound _step
        with cython.overflowcheck(True):  # raises OverflowError if input does not fit
            if stop is None:
                _start = 0
                _stop = index(start_stop)
                _step = 1
            else:
                _start = index(start_stop)
                _stop = index(stop)
                _step = index(step) if step is not None else 1
            if _step == 0:
                raise ValueError('range() arg 3 must not be zero')
            # length depends only on read-only values, so compute it only once
            # practically ALL methods use it, so compute it NOW
            # range is required to handle large ints outside of float precision
            _len = (_stop - _start) // _step
            _len += 1 if (_stop - _start) % _step else 0
            _len = 0 if _len < 0 else _len
        self.start = _start
        self.stop = _stop
        self.step = _step
        self._len = _len
        self._bool = bool(self._len)

    def __nonzero__(self):
        return self._bool

    # NOTE:
    # We repeatedly use self._len instead of len(self)!
    # The len-protocol can cause overflow, since it only expects an int, not
    # py2 long int etc. We circumvent this with the direct lookup.
    def __len__(self):
        return self._len

    def __getitem__(self, item):
        # index) range(1, 10, 2)[3] => 1 + 2 * 3 if < 10
        # slice) range(1, 10, 2)[1:3] => range(3, 7)
        # There are no custom slices allowed, so we can do a fast check
        # see: http://stackoverflow.com/q/39971030/5349916
        if item.__class__ is slice:
            max_len = self._len
            # nothing to slice on
            if not max_len:
                return self.__class__(0, 0)
            try:
                start_idx, stop_idx, slice_stride = item.indices(max_len)
            except OverflowError:
                # We cannot use item.indices since that may overflow in py2.X...
                slice_start, slice_stop, slice_stride, max_len = item.start, item.stop, item.step, self._len
                if slice_start is None:  # slice open to left as in [None:12312]
                    new_start = self.start
                else:
                    start_idx = index(slice_start)
                    if start_idx >= max_len:  # cut off out-of-range
                        new_start = self.stop
                    elif start_idx < -max_len:
                        new_start = self.start
                    else:
                        new_start = self[start_idx]
                if slice_stop is None:  # slice open to right as in [1213:None]
                    new_stop = self.stop
                else:
                    stop_idx = index(slice_stop)
                    if stop_idx >= max_len:
                        new_stop = self.stop
                    elif stop_idx < -max_len:
                        new_stop = self.start
                    else:
                        new_stop = self[stop_idx]
                slice_stride = 1 if slice_stride is None else slice_stride
            else:
                new_start = self.start + self.step * start_idx
                new_stop = self.start + self.step * stop_idx
            return self.__class__(new_start, new_stop, self.step * slice_stride)
        # check type first
        val = index(item)
        if val < 0:
            val += self._len
        if val < 0 or val >= self._len:
            raise IndexError('range object index out of range')
        return self.start + self.step * val

    def __iter__(self):
        # Let's reinvent the wheel again...
        # We *COULD* use xrange here, but that leads to OverflowErrors etc.
        return llrange_iterator(self.start, self.step, self._len)

    def __reversed__(self):
        # this is __iter__ in reverse, *by definition*
        if self._len:
            return llrange_iterator(self[-1], -self.step, self._len)
        else:
            return llrange_iterator(0, 1, 0)

    # Comparison Methods
    # Cython requires the use of __richcmp__ *only* and fails
    # when __eq__ etc. are present.
    # Each __OP__ is defined as __py_OP__ and rebound as required.
    cpdef __py_eq__(self, other):
        cdef:
            range other_range
        if self is other:
            return True
        if isinstance(self, other.__class__):
            other_range = other
            # unequal number of elements
            # check this first to imply some more features
            # NOTE: call other._len to avoid OverflowError
            if self._len != other_range._len:
                return False
            # empty ranges are always equal
            elif not self._bool:
                return True
            # first element must always match
            elif self.start != other_range.start:
                return False
            # just that one element, step does not matter
            elif self._len == 1:
                return True
            # final element is implied by same start, count and step
            else:
                return self.step == other_range.step
        elif _builtin_range_class is not None and isinstance(other, _builtin_range_class):
            # NOTE: we cannot safely check len(other) due to OverflowError
            # for an empty range, specifics do not matter
            if not self._bool:
                return not bool(other)
            # make sure we describe the same range by *effective* start, stop and stride
            return bool(other) and self.start == other.start and self.step == other.step and self[-1] == other[-1]
        # specs assert that range objects may ONLY equal to range objects
        return NotImplemented

    def __richcmp__(self, other, int comp_opcode):  # pragma: no cover
        # Cython:
        # Do not rely on the first parameter of these methods, being "self" or the right type.
        # The types of both operands should be tested before deciding what to do.
        if not isinstance(self, range):
            # if other is not of type(self), we can't compare it anyways
            return NotImplemented
        # Comparison opcodes:
        # < <= == != > >=
        # 0  1  2  3 4  5
        if comp_opcode == 2:
            return self.__py_eq__(other)
        elif comp_opcode == 3:
            eq = self.__py_eq__(other)
            if eq is NotImplemented:
                return NotImplemented
            elif eq:
                return False
            else:
                return True
        else:
            return NotImplemented

    def __contains__(self, item):
        # specs use fast comparison ONLY for pure ints
        # subtypes are not allowed, so that custom __eq__ can be used
        # we use fast comparison only if:
        #   a type does use the default __eq__
        # Note: objects are never coerced into other types for comparison
        if type(item).__eq__ in _int__eq__s:
            return self._contains_int(item)
        else:
            # take the slow path, compare every single item
            return any(self_item == item for self_item in self)

    def _contains_int(self, integer):
        # NOTE: integer is not a C int but a Py long
        if self.step == 1:
            return self.start <= integer < self.stop
        elif self.step > 0:
            return self.stop > integer >= self.start and not (integer - self.start) % self.step
        elif self.step < 0:
            return self.stop < integer <= self.start and not (integer - self.start) % self.step

    def index(self, value, start=None, stop=None):
        """Return first index of ``value``. Raises :py:exc:`ValueError` if ``value`` is not in the range."""
        # Note: objects are never coerced into other types for comparison
        if type(value).__eq__ in _int__eq__s:
            index = (value - self.start) // self.step
            if self._contains_int(value):
                if start is None and stop is None:
                    return index
                else:
                    start = 0 if start is None else start + self._len if start < 0 else start
                    stop = self._len if stop is None else stop + self._len if stop < 0 else stop
                    if start <= index < stop:
                        return index
        else:
            # take the slow path, compare every single item
            for index, self_item in enumerate(self):
                if self_item == value:
                    # get the obvious use case done first
                    if start is None and stop is None:
                        return index
                    # do the uncommon test thoroughly
                    else:
                        start = 0 if start is None else start + self._len if start < 0 else start
                        stop = self._len if stop is None else stop + self._len if stop < 0 else stop
                        if start <= index < stop:
                            return index
        raise ValueError('%r is not in range' % value)

    def count(self, value):
        """Return number of occurrences of ``value``"""
        # Note: objects are never coerced into other types for comparison
        if type(value).__eq__ in _int__eq__s:
            return int(self._contains_int(value))
        # take the slow path, compare every single item
        return sum(1 for self_item in self if self_item == value)

    def __hash__(self):
        # Hash should signify the same sequence of values
        # We hash a tuple of values that define the range.
        # derived from rangeobject.c
        my_len = self._len
        if not my_len:
            return hash((0, None, None))
        elif my_len == 1:
            return hash((1, self.start, None))
        return hash((my_len, self.start, self.step))

    def __repr__(self):
        if self.step != 1:
            return 'range(%d, %d, %d)' % (self.start, self.stop, self.step)
        return 'range(%d, %d)' % (self.start, self.stop)

    # Pickling
    def __reduce__(self):
        # __reduce__ protocol:
        # return: factory, factory_args, state, sequence iterator, mapping iterator
        # unpickle: factory(*(factory_args))
        return type(self), (self.start, self.stop, self.step), None, None, None

# register at ABCs
# do not use decorators to play nice with Cython
_abc.Sequence.register(range)
