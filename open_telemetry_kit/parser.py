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
    for subcls in Element.__subclasses__():
      for el in subcls.__subclasses__():
        for name in el.names:
          self.element_dict[name] = el

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