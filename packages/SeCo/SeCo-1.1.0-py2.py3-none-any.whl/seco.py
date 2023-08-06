# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)


# import directive
__all__ = (
  '__author__', '__license__', '__version__', 'SeCo'
)
# package metadata
__author__ = 'Hansheng Zhao'
__license__ = 'BSD-2-Clause + MIT'
__version__ = '1.1.0'


class SeCo(object):
  """ SeCo class for data serialize and compress """

  __slots__ = (
    '_serialize', '_compress',
    '_serializer','_compressor'
  )

  def __init__(
    self, serialize = None, compress = None, **kwargs
  ):
    """
    Initialize method for building object
    :param serialize: str|dict|None, the serialize config
    :param compress: str|None, the compress config
    :param kwargs: dict, the stray keyword args
    """
    # default configurations
    self._serialize = 'json'
    self._compress = 'zlib'
    self._serializer = None
    self._compressor = None
    # acquire serialize (and compress) config
    if serialize is not None:
      if isinstance(serialize, str):
        self._serialize = serialize.lower()
      else:
        if 'serialize' in serialize:
          self._serialize = serialize['serialize'].lower()
        if 'compress' in serialize:
          self._compress = serialize['compress'].lower()
    elif 'serialize' in kwargs:
      self._serialize = kwargs['serialize']
    # acquire compress config
    if compress is not None and isinstance(compress, str):
      self._compress = compress.lower()
    elif 'compress' in kwargs:
      self._compress = kwargs['compress'].lower()

  def __call__(self, payload, switch = True):
    """
    Alias for serialize/deserialize methods
    :param payload: mixed, various objects
    :param switch: bool, whether to serialize
    :return: mixed, objects
    """
    return self.dumps(payload) \
      if switch else self.loads(payload)

  def _instantiate(self):
    """
    Instantiate serializer and compressor
    :return: None
    """
    # setup appropriate serializer
    if self._serializer is None:
      # import json serializer
      import simplejson
      self._serializer = simplejson
      if self._serialize == 'pickle':
        # import pickle serializer
        import pickle
        self._serializer = pickle
      elif self._serialize == 'msgpack':
        # import msgpack serializer
        import msgpack
        self._serializer = msgpack
    # setup appropriate compressor
    if self._compressor is None:
      # import zlib serializer
      import zlib
      self._compressor = zlib
      if self._compress == 'gzip':
        # import gzip compressor
        import gzip
        self._compressor = gzip
      elif self._compress == 'bz2':
        # import bz2 compressor
        import bz2
        self._compressor = bz2
      elif self._compress == 'lzma':
        # import lzma compressor
        import lzma
        self._compressor = lzma

  @property
  def serializer(self):
    """
    Serializer property getter
    :return: internal serializer
    """
    return self._serializer

  @serializer.setter
  def serializer(self, serializer):
    """
    Serializer property setter
    :param serializer: the serializer
    :return: None
    """
    self._serializer = serializer

  @property
  def compressor(self):
    """
    Compressor property getter
    :return: internal compressor
    """
    return self._compressor

  @compressor.setter
  def compressor(self, compressor):
    """
    Compressor property setter
    :param compressor: the compressor
    :return: None
    """
    self._compressor = compressor

  # dumps method for python convention
  def dumps(self, payload):
    """
    Serialize and compress the payload
    :param payload: mixed, serializable object
    :return: byte, the serialized and compressed object
    """
    # instantiate serializer and compressor
    self._instantiate()
    # serialize payload
    payload = self._serializer.dumps(payload)
    # encode payload if payload is string
    if isinstance(payload, (str,)):
      payload = payload.encode()
    # compress and return payload
    return self._compressor.compress(payload)

  def dump(self, payload, file):
    """
    Serialize, compress and save
    :param payload: mixed, serializable object
    :param file: file descriptor
    :return: None
    """
    file.write(self.dumps(payload))
    file.flush()

  # alias for dump
  pack = dump

  # loads method for python convention
  def loads(self, payload):
    """
    Decompress and deserialize the payload
    :param payload: bytes, serialized byte string
    :return: object, the decompressed and deserialized object
    """
    # instantiate serializer and compressor
    self._instantiate()
    # decompress payload
    payload = self._compressor.decompress(payload)
    # deserialize and return payload
    return self._serializer.loads(payload, encoding='UTF8')

  def load(self, file):
    """
    Decompress and deserialize the file
    :param file: file descriptor, or BytesIO instance
    :return: object, the decompressed and deserialized object
    """
    # decompress, deserialize and return payload
    return self.loads(file.read())

  # alias for load
  unpack = load
