from .types cimport range_bound

cdef class range(object):
    cdef readonly range_bound start
    cdef readonly range_bound stop
    cdef readonly range_bound step
    cdef readonly range_bound _len
    cdef readonly bint _bool

    cpdef __py_eq__(self, other)
