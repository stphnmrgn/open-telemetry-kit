from .telemetry import Telemetry
from .element import Element
from abc import ABCMeta
from abc import abstractmethod

class Parser(metaclass=ABCMeta):
  def __init__(self, source, 
               convert_to_epoch: bool = False,
               require_timestamp: bool = False):
    self.source = source
    self.convert_to_epoch = convert_to_epoch
    self.require_timestamp = require_timestamp
    self.element_dict = {}
    self.__build_dict(Element)

  def __build_dict(self, elem):
    try:
      for name in elem.names:
        self.element_dict[name] = elem
    except:
      pass

    for sub in elem.__subclasses__():
      self.__build_dict(sub)

  def __str__(self) -> str:
    return "{}('{}')".format(self.__class__.__name__, self.source)

  def __repr__(self) -> str:
    return "{}('{}')".format(self.__class__.__name__, self.source)

  @property
  @classmethod
  @abstractmethod
  def tel_type(self) -> str:
    pass

  @abstractmethod
  def read(self) -> Telemetry:
    pass