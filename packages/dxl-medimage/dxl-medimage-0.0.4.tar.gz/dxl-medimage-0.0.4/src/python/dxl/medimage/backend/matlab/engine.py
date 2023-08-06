default_engine = None


class MatlabEngine:
  def __init__(self, sub_path='phantom'):
    self.eng = None
    self.pre = None
    self.sub_path = sub_path

  def __enter__(self):
    global default_engine
    import matlab.engine
    import os
    from pathlib import Path
    self.eng = matlab.engine.start_matlab()
    path_dxmat = os.environ.get('PATH_DXL_DXMAT')
    if path_dxmat is not None:
      path_gen = Path(path_dxmat)
      if self.sub_path is not None:
        path_gen = path_gen / self.sub_path
      self.eng.addpath(str(path_gen))
    self.pre = default_engine
    default_engine = self.eng
    return self.eng

  def __exit__(self, type, value, trackback):
    global default_engine
    default_engine = self.pre
    self.eng.quit()

  @staticmethod
  def get_default_engine():
    return default_engine


def call_matlab_api(func):
  """
    Matlab engine will be passed as the first argument to func
    """
  if MatlabEngine.get_default_engine() is None:
    with MatlabEngine() as eng:
      return func(eng)
  else:
    return func(MatlabEngine.get_default_engine())
