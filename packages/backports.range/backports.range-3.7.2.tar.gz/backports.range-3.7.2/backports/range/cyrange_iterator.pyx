import collections as _abc


cdef class llrange_iterator(object):
    def __init__(self, long long start, long long step, long long count, long long current=-1):
        """
        Iterator over a `range`, for internal use only

        Compiled version using C `long long` data type
        """
        self._start = start
        self._step = step
        self._max_idx = count - 1
        self._current = current

    def __iter__(self):
        return self

    def __next__(self):
        if self._current == self._max_idx:
            raise StopIteration
        self._current += 1
        return self._start + self._step * self._current

    def __length_hint__(self):
        # both stop and current are offset by 1 which cancels out here
        return self._max_idx - self._current

    # Pickling
    def __reduce__(self):
        # __reduce__ protocol:
        # return: factory, factory_args, state, sequence iterator, mapping iterator
        # unpickle: factory(*(factory_args))
        # we use the plain python iterator because:
        # - the extension type is NOT a valid type for pickle (because of reasons?)
        # - the extension type may be unavailable
        return type(self), (self._start, self._step, self._max_idx + 1, self._current), None, None, None

# register at ABCs
# do not use decorators to play nice with Cython
_abc.Iterator.register(llrange_iterator)
