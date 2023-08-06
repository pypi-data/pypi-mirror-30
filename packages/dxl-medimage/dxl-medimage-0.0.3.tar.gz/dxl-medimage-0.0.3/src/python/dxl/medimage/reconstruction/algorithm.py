class Algorithm:
  def __init__(self, device, backend):
    self._device = device
    self._backend = backend

  @property
  def device(self):
    return self._device

  @property
  def backend(self):
    return self._backend


class FBP(Algorithm):
  @classmethod
  def supported_filters(cls, backend):
    if backend == 'astra':
      return [
          'ram-lak',
          'shepp-logan',
          'cosine',
          'hamming',
          'hann',
          'none',
      ]

  def __init__(self,
               device='gpu',
               backend='astra',
               filter_='ram-lak',
               filter_d=1.0):
    super().__init__(device, backend)
    self._filter = filter_
    self.filter_d = filter_d

  @property
  def filter(self):
    return self._filter
