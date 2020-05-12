#!/usr/bin/env python3

from abc import ABCMeta
from abc import abstractmethod
import logging
from typing import Any, Set

logger = logging.getLogger("OTK.Element")
class Element(metaclass=ABCMeta):
  def __init__(self, value: Any):
    self.value = value

  def __str__(self):
    # return '{}'.format(self.value)
    return str(self.value)

  def __repr__(self) -> str:
    return "{}('{}')".format(self.__class__.__name__, self.value)

  @property
  @classmethod
  @abstractmethod
  def name(cls) -> str:
    pass

  @property
  @classmethod
  @abstractmethod
  def names(cls) -> Set[str]:
    pass

  def toJson(self) -> Any:
    return self.value

class FloatElement(Element):
  def __init__(self, value: float):
    try:
      self.value = float(value)
    except:
      logger.error("'{}' could not be converted to a float value, leaving as string.".format(value))
      self.value = str(value)

class IntElement(Element):
  def __init__(self, value: int):
    try:
      self.value = int(value)
    except:
      logger.error("'{}' could not be converted to a int value, leaving as string.".format(value))
      self.value = str(value)

class StrElement(Element):
  def __init__(self, value: str):
      self.value = str(value)

class UnknownElement(Element):
  name = "unknown"
  names = {}

  def __init__(self, value: str):
    self.value = str(value)
