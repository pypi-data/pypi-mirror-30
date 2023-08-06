from .base import Detector2D, Model
from dxl.data.core.asserts import assert_dimension
import numpy as np


class ParallelLinearModel(Model):
  name = 'linear'


class Parallel2D(Detector2D):
  @classmethod
  def create_sensors(cls, nb_sensors, sensor_width=1.0):
    """
    Helper function to create sensors, locating at center of each periods.
    """
    return np.arange(nb_sensors) * sensor_width - \
      ((nb_sensors / 2 - 0.5) * sensor_width)

  @classmethod
  def create_views(cls, nb_views, view_range=None):
    if view_range is None:
      view_range = [0.0, np.pi]
    return np.linspace(view_range[0], view_range[1], nb_views, endpoint=False)

  def __init__(self, sensors=None, views=None, model=None):
    """
    """
    self._sensors = np.array(sensors)
    self._views = np.array(views)
    assert_dimension(self._sensors, 1, 'Detector sensors')
    assert_dimension(self._views, 1, 'Detector views')
    if model is None:
      model = ParallelLinearModel()
    self._model = model

  @property
  def nb_sensors(self):
    return len(self._sensors)

  def sensor_width(self):
    return np.mean(self._sensors[1:] - self._sensors[:-1])

  def sensors(self):
    return np.array(self._sensors)

  @property
  def nb_views(self):
    return len(self._views)

  def views(self):
    return np.array(self._views)

  def model(self):
    return self._model

  def check_data_capability(self, data):
    if isinstance(data, np.ndarray):
      if data.ndim != 2 or self.nb_views != data.shape[0] or self.nb_sensors != data.shape[1]:
        msg = "Shape of sinogram {} is not consisted with detector: nb_sensors: {}, nb_views: {}."
        raise ValueError(
            msg.format(data.shape, self.nb_sensors, self.nb_views))
    else:
      raise TypeError("Unknown data type: {}.".format(type(data)))
