# stochastic gradient descent updates for poisson state estimation

import cython
cimport cython


import numpy as np
cimport numpy as np
DTYPE = np.double
ctypedef np.double_t DTYPE_t

cdef double eps = 1e-10

def sgd_update_w(np.ndarray[DTYPE_t, ndim=1] X, np.ndarray[DTYPE_t, ndim=2] M, np.ndarray[DTYPE_t, ndim=2] W, np.ndarray[DTYPE_t, ndim=1] Xsum, int disp=False):
    """
    Updates a single cell???
    """
