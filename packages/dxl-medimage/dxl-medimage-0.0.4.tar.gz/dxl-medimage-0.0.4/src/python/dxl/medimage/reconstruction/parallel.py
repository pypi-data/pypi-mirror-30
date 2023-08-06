from ..config import config
import logging
from ..image import Image2DSpec
from ..detector.parallel import Parallel2D
from .algorithm import Algorithm
import numpy as np
from contextlib import contextmanager

import enum

# from dxpy.configs import configurable

# def _inputs_verification2d(detector, phantom_spec, sinogram):
#   from ..detector.base import Detector2D
#   from ..exceptions import InputVerifacationError
#   if not isinstance(detector, Detector2D):
#     raise InputVerifacationError("Input detector is not Detector2D, {}.")
#   detector.assert_fit(sinogram)


@contextmanager
def reconstructor2d(detector: Parallel2D, image_spec: Image2DSpec,
                    method: Algorithm):
  if method.backend == 'astra':
    try:
      from ..backend.astra.reconstruction2d import ReconstructorParallel2D
      r = ReconstructorParallel2D(detector, image_spec, method)
      yield r
    except Exception as e:
      raise e
    finally:
      r.clear()
  else:
    raise ValueError("Unknown backend {}.".format(method.backend))


def reconstruction2d_single(sinogram: np.ndarray, detector: Parallel2D,
                            image: Image2DSpec, method: Algorithm):
  with reconstructor2d(detector, image, method) as r:
    return r.reconstruct(sinogram)


def reconstruction2d_batch(sinograms: np.ndarray,
                           detector: Parallel2D,
                           image_spec: Image2DSpec,
                           method: Algorithm,
                           *,
                           tqdm=None):
  nb_images = sinograms.shape[0]
  with reconstructor2d(detector, image_spec, method) as r:
    if tqdm is None:

      def tqdm(x, ascii=None, leave=None):
        return x

    results = [
        r.reconstruct(sinograms[i, ...])
        for i in tqdm(range(nb_images), ascii=True, leave=False)
    ]
  return np.array(results)


# @configurable(config.get('reconstruction'))
def reconstruction2d(sinograms,
                     detector: Parallel2D,
                     image_spec: Image2DSpec,
                     method,
                     *,
                     tqdm=None):
  """
    Args:
      sinogram: one of the following objects:
        1. 2-dimensional ndarray
        2. Sinogram2D object
        3. NDArrayOnFS object

        detector: Detector specifics,
        phantom_spec: phantom specifics
        sinogram: 2-dimensional ndarray.
    """
  if sinograms.ndim in (3, 4):
    logging.debug('Sinogram dimension is {}, use batch mode.'.format(
        sinograms.ndim))
    if sinograms.ndim == 4:
      logging.debug(
          'Last dimension of sinograms will be ignored by sinograms[:, :, :, 0].'.
          format(sinograms.ndim))
      sinograms = sinograms[:, :, :, 0]
    return reconstruction2d_batch(
        sinograms, detector, image_spec, method, tqdm=tqdm)
  else:
    logging.debug('Sinogram dimension is 3, use batch mode.')
    return reconstruction2d_single(sinograms, detector, image_spec, method)


#   _inputs_verification2d(detector, phantom_spec, sinogram)
#   vol_geom = ac.create_vol_geom(phantom_spec.shape)
#   proj_geom = ac.create_proj_geom('parallel', detector.sensor_width,
#                                   detector.nb_sensors, detector.views)
#   proj_id = ac.create_projector('linear', proj_geom, vol_geom)
#   rid, result = ac.create_reconstruction(method, proj_id, sinogram, iterations)
#   astra.data2d.clear()
#   astra.projector.clear()
#   astra.algorithm.clear()
#   return result
