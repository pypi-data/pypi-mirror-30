def phantom(eng, size=256.0):
  from .engine import call_matlab_api
  return call_matlab_api(lambda e: e.phantom(size))