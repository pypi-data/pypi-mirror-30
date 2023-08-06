import ctypes


# see also
# https://docs.python.org/3/c-api/buffer.html#buffer-request-types
# $CONDA_PREFIX/include/python3.6m/object.h
PyBUF_SIMPLE   = 0
PyBUF_WRITABLE = 0x0001
PyBUF_FORMAT   = 0x0004
PyBUF_ND       = 0x0008
PyBUF_STRIDES  = 0x0010 | PyBUF_ND

PyBUF_C_CONTIGUOUS   = 0x0020 | PyBUF_STRIDES
PyBUF_F_CONTIGUOUS   = 0x0040 | PyBUF_STRIDES
PyBUF_ANY_CONTIGUOUS = 0x0080 | PyBUF_STRIDES
PyBUF_INDIRECT       = 0x0100 | PyBUF_STRIDES

PyBUF_CONTIG_RO  = PyBUF_ND
PyBUF_CONTIG     = PyBUF_ND | PyBUF_WRITABLE

PyBUF_STRIDED_RO = PyBUF_STRIDES
PyBUF_STRIDED    = PyBUF_STRIDES | PyBUF_WRITABLE

PyBUF_RECORDS_RO = PyBUF_STRIDES | PyBUF_FORMAT
PyBUF_RECORDS    = PyBUF_STRIDES | PyBUF_FORMAT | PyBUF_WRITABLE

PyBUF_FULL_RO = PyBUF_INDIRECT | PyBUF_FORMAT
PyBUF_FULL    = PyBUF_INDIRECT | PyBUF_FORMAT | PyBUF_WRITABLE

Py_ssize_t = ctypes.c_ssize_t
Py_ssize_t_p = ctypes.POINTER(Py_ssize_t)


class PyBuffer(ctypes.Structure):
    """Python Buffer Interface
    See_also:
    https://docs.python.org/3/c-api/buffer.html#buffer-protocol
    $CONDA_PREFIX/include/python3.6m/object.h
    """
    _fields_ = (('buf', ctypes.c_void_p),
                ('obj', ctypes.c_void_p), # owned reference
                ('len', Py_ssize_t),
                ('itemsize', Py_ssize_t),

                ('readonly', ctypes.c_int),
                ('ndim', ctypes.c_int),
                ('format', ctypes.c_char_p),
                ('shape', Py_ssize_t_p),
                ('strides', Py_ssize_t_p),
                ('suboffsets', Py_ssize_t_p),
                ('internal', ctypes.c_void_p))

    def __init__(self, obj, flags=PyBUF_FULL):
        pyapi.PyObject_GetBuffer(obj, ctypes.byref(self), flags)

    def __del__(self):
        pyapi.PyBuffer_Release(ctypes.byref(self))
        ctypes.memset(ctypes.byref(self), 0, ctypes.sizeof(self))


def to_bytes(obj, flags=PyBUF_FULL):
    return memoryview(PyBuffer(obj, flags)).tobytes()


# PyBuffer functions in PythonAPI
pyapi = ctypes.PyDLL("PythonAPI", handle=ctypes.pythonapi._handle)
pyapi.PyObject_GetBuffer.argtypes = (ctypes.py_object,          # obj
                                     ctypes.POINTER(PyBuffer),  # view
                                     ctypes.c_int)              # flags
pyapi.PyBuffer_Release.argtypes = ctypes.POINTER(PyBuffer),     # view
