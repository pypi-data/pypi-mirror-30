import numpy as np


class ImageSpec:
  def __init__(self, shape, dtype=np.float32):
    self._shape = shape
    self._dtype = dtype

  @property
  def shape(self):
    return self._shape

  @property
  def dtype(self):
    return self._dtype


class Image2DSpec(ImageSpec):
  ndim = 2


class Image3DSpec(ImageSpec):
  ndim = 3
