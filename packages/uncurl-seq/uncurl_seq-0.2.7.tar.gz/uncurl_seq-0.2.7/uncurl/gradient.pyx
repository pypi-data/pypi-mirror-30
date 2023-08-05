# objectives/gradients for NB, ZIP?

import cython
cimport cython


import numpy as np
cimport numpy as np
DTYPE = np.double
ctypedef np.double_t DTYPE_t

cdef double eps = 1e-10

def sparse_nb_w_obj(np.ndarray[DTYPE_t, ndim=2] W,
         X,
        np.ndarray[DTYPE_t, ndim=2] M,
        np.ndarray[DTYPE_t, ndim=1] Xsum,
        np.ndarray[DTYPE_t, ndim=1] Msum,
        int disp=False):
    """
    Returns the objective and gradient for W, given sparse X and M...
    """
    cdef int cells = X.shape[1]
    cdef int genes = X.shape[0]
    cdef int k = W.shape[0]
    cdef double[:,:] M_view = M
    cdef double[:,:] W_view = W
    cdef double[:,:] Wnew_view = np.empty((k, cells), dtype=np.double)
    cdef Py_ssize_t i, g, j, k2, start_ind, end_ind
    X_csc = sparse.csc_matrix(X)
    cdef int[:] indices = X_csc.indices
    cdef int[:] indptr = X_csc.indptr
    cdef double[:] data_ = X_csc.data


