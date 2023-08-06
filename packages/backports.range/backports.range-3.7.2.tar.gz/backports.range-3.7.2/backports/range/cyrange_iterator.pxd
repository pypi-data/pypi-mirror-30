from .types cimport range_bound

cdef class llrange_iterator(object):
    cdef range_bound _start
    cdef range_bound _step
    cdef range_bound _max_idx
    cdef range_bound _current
