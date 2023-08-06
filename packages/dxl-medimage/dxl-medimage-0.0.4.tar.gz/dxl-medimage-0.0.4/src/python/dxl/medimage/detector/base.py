class Detector:
  def check_data_capability(self, data):
    """
    Check if data is output of this detecotr, mainly checking shape, content, etc.
    Returns: 
      None
    Raises:
      ValueError, TypeError
    """
    pass


class Detector3D(Detector):
  ndim = 3


class Detector2D(Detector):
  ndim = 2


class Model:
  name = None
