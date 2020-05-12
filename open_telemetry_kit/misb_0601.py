#!/usr/bin/env python3

from .klv_common import bytes_to_int, bytes_to_float, bytes_to_str
import logging
from abc import ABCMeta
from abc import abstractmethod
from datetime import datetime
from dateutil import parser as dup
from typing import Tuple

class MISB0601(metaclass=ABCMeta):
  @classmethod
  @abstractmethod
  def fromMISB(cls, value):
    pass

  @property
  @classmethod
  @abstractmethod
  def misb_key(cls):
    pass

  @property
  @classmethod
  @abstractmethod
  def misb_name(cls) -> str:
    pass

  @property
  @classmethod
  @abstractmethod
  def misb_tag(cls) -> int:
    pass

  @property
  @classmethod
  @abstractmethod
  def misb_units(cls) -> str:
    pass

class IntMISB(MISB0601):
  @property
  @classmethod
  def _signed(cls) -> bool:
    False

  @classmethod
  def fromMISB(cls, value):
    return cls(bytes_to_int(value, cls._signed))

class FloatMISB(MISB0601):
  @property
  @classmethod
  @abstractmethod
  def _domain(cls) -> Tuple[int, int]:
    pass

  @property
  @classmethod
  @abstractmethod
  def _range(cls) -> Tuple[int, int]:
    pass

  @property
  @classmethod
  def _invalid(cls) -> bytes:
    pass

  @classmethod
  def fromMISB(cls, value):
    if isinstance(cls._invalid, bytes) and value == cls._invalid:
      c = cls(0)
      c.value = None
      return c
    elif cls._domain == 'IMAPB':
      l = len(value)
      return cls(bytes_to_float(value, (0, 2**(8*l)-1), cls._range))
    else:
      return cls(bytes_to_float(value, cls._domain, cls._range))

class StrMISB(MISB0601):
  @classmethod
  def fromMISB(cls, value):
    return cls(bytes_to_str(value))
