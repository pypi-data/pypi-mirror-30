from ._bindings import *

class error(Exception):

  _strerror = None

  def __init__(self, code):
    self.code = code

  @property
  def strerror(self):
    strerror = self._strerror
    if strerror is None:
      strerror = self._strerror = getErrorName(-self.code)
    return strerror

  def __str__(self):
    return "[error %s] %s" % (self.code, self.strerror)

from . import _bindings
_bindings.error = error
del _bindings
