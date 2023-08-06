# cython: c_string_encoding=utf8

from cpython cimport (PyObject, PY_LONG_LONG,
    PyBytes_FromStringAndSize as _PyBytes_FromStringAndSize,
    PyBytes_AS_STRING as _PyBytes_AS_STRING)

cdef extern from "Python.h":
    # Although the following are in cpython, we want `PyObject*` instead of
    # `object` type for correct reference counting with _PyBytes_Resize
    # (all this because Cython refuses to "take address of Python variable").
    void Py_DECREF(PyObject *o)
    PyObject *PyBytes_FromStringAndSize(char *v, Py_ssize_t len) except NULL
    int _PyBytes_Resize(PyObject **string, Py_ssize_t newsize) except -1
    char *PyBytes_AS_STRING(PyObject *string) nogil

cdef extern from "zstd.h":
    # To simplify implementation, we use signed types (and detect errors with
    # negative values). Anyway, that's what `bytes` uses for its length.
    ssize_t      ZSTD_compressBound(ssize_t srcSize)
    const char * ZSTD_getErrorName(ssize_t code)
    int          ZSTD_maxCLevel()
    PY_LONG_LONG ZSTD_getFrameContentSize(const void *src, ssize_t srcSize)
    ssize_t      ZSTD_compress(void *dst, ssize_t dstCapacity,
                               const void *src, ssize_t srcSize,
                               int compressionLevel) nogil
    ssize_t      ZSTD_decompress(void *dst, ssize_t dstCapacity,
                                 const void *src, ssize_t compressedSize) nogil

def maxCLevel():
    return ZSTD_maxCLevel()

cdef PY_LONG_LONG _getFrameContentSize(const void *src, ssize_t srcSize) except -1:
    cdef PY_LONG_LONG size = ZSTD_getFrameContentSize(src, srcSize)
    if size < 0:
        raise RuntimeError("ZSTD_getFrameContentSize returned %s" % size)
    return size

def getFrameContentSize(bytes string not None):
    return _getFrameContentSize(_PyBytes_AS_STRING(string), len(string))

def getErrorName(code):
    return <str>ZSTD_getErrorName(code)

global error

def compress(bytes string not None, int level=0):
    cdef:
        int x
        ssize_t srcSize = len(string)
        ssize_t dstCapacity = ZSTD_compressBound(srcSize)
        PyObject *dst = PyBytes_FromStringAndSize(NULL, dstCapacity)
    with nogil:
        x = ZSTD_compress(PyBytes_AS_STRING(dst), dstCapacity,
                          PyBytes_AS_STRING(<PyObject*>string), srcSize,
                          level)
    if x < 0:
        Py_DECREF(dst)
        raise error(-x)
    _PyBytes_Resize(&dst, x)
    r = <object>dst
    Py_DECREF(<PyObject*>r) # revert the unwanted incref on the previous line
    return r

def decompress(bytes string not None):
    cdef:
        int x
        ssize_t compressedSize = len(string)
        void *src = _PyBytes_AS_STRING(string)
        PY_LONG_LONG dstCapacity = _getFrameContentSize(src, compressedSize)
    dst = _PyBytes_FromStringAndSize(NULL, dstCapacity)
    with nogil:
        x = ZSTD_decompress(PyBytes_AS_STRING(<PyObject*>dst), dstCapacity,
                            src, compressedSize)
    if x < 0:
        raise error(-x)
    return dst
