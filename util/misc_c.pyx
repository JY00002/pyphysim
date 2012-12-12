#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
cimport numpy as np

"""This module reimplements functions in the util.misc module, but using
Cython for speeding up calculations."""

# Because we are using cdef, this function won't be available in python
cdef int _count_bits_single_element(int n):
    """Count the number of bits that are set in an interger number.

    Parameters
    ----------
    n : int
        The interger number.

    Returns
    -------
    Number of bits that are equal to 1 in the bit representation of the
    number `n`.

    """
    cdef int count = 0
    while n > 0:
        if n & 1 == 1:
            count += 1
        n >>= 1
    return count


def count_bits(np.ndarray[np.int_t, ndim=1] n):
    """Count the number of bits that are set.

    Parameters
    ----------
    n : int or numpy array of ints
        An integer number or a numpy array of integer numbers.

    Returns
    -------
    num_bits : int or numpy array of ints
        Number of bits that are set in `n`. If `n` is a numpy array then
        `num_bits` will also be a numpy array with the number of bits that
        are set for each element in `n`
    """
    assert n.dtype == np.int

    cdef int num_el = len(n)
    cdef Py_ssize_t index  # Since we will use index for indexing 'n', then
                           # using Py_ssize_t as the type for index give
                           # faster results then using a simple int.
    cdef np.ndarray[np.int_t, ndim=1] num_bits = np.empty(num_el, dtype=np.int)
    for index in range(num_el):
        num_bits[index] = _count_bits_single_element(n[index])

    return num_bits


# np.import_array()

# def prod2(a, b):
#     #generate a new output array of the correct shape by broadcasting input arrays together
#     out = np.empty(np.broadcast(a, b).shape, np.float)

#     #generate the iterator over the input and output arrays, does the same thing as
#     # PyArray_MultiIterNew

#     cdef np.broadcast it = np.broadcast(a, b, out)

#     while np.PyArray_MultiIter_NOTDONE(it):

#             #PyArray_MultiIter_DATA is used to access the pointers the iterator points to
#             aval = (<double*>np.PyArray_MultiIter_DATA(it, 0))[0]
#             bval = (<double*>np.PyArray_MultiIter_DATA(it, 1))[0]

#             (<double*>np.PyArray_MultiIter_DATA(it, 2))[0] = aval * bval

#             #PyArray_MultiIter_NEXT is used to advance the iterator
#             np.PyArray_MultiIter_NEXT(it)

#     return out