import numpy as np
from .spec import Image2DSpec


class Image:
  def __init__(self, shape, dtype=None):
    if dtype is None:
      dtype = np.float32
    self._shape = shape
    self._dtype = dtype

  @property
  def shape(self):
    return self._shape

  @property
  def dtype(self):
    return self._dtype


class Image2D(Image):
  def __init__(self, shape, dtype=None):
    if isinstance(shape, Image2DSpec):
      shape = shape.shape
      dtype = shape.dtype
    else:
      if len(shape) != 2:
        raise ValueError("Invalid shape {} for Image2D.".format(shape))
    super().__init__(shape, dtype)