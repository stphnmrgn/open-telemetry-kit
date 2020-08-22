from .parser import Parser
from .telemetry import Telemetry
from .packet import Packet
from .element import UnknownElement
from .elements import TimestampElement, DatetimeElement

import csv
from dateutil import parser as dup
import logging

class CSVParser(Parser):
  tel_type = "csv"

  def __init__(self, source: str, 
               convert_to_epoch: bool = False,
               require_timestamp: bool = False):
    super().__init__(source, 
                     convert_to_epoch = convert_to_epoch, 
                     require_timestamp = require_timestamp)
    self.logger = logging.getLogger("OTK.CSVParser")

  def read(self) -> Telemetry:
    tel = Telemetry()
    with open(self.source, newline='') as csvfile:
      reader =  csv.DictReader(csvfile)

      for idx, name in enumerate(reader.fieldnames):
        reader.fieldnames[idx] = name.strip()

      for row in reader:
        packet = Packet()
          
        for key, val in row.items():
          if key in self.element_dict:
            #element_dict[key] returns a class
            element_cls = self.element_dict[key]
            if element_cls == DatetimeElement and self.convert_to_epoch:
              val = dup.parse(val).timestamp()
              packet[TimestampElement.name] = TimestampElement(val)
            elif element_cls == TimestampElement:
              if val.find('.') > 0: #probably a float in epoch seconds
                packet[element_cls.name] = element_cls(val)

              # Based on this SO post: https://bit.ly/2WMGOc1
              elif len(val) >= 16: #probably microseconds
                packet[element_cls.name] = element_cls(float(val) * 1e-6)
              elif len(val) >= 13: #probably milliseconds
                packet[element_cls.name] = element_cls(float(val) * 1e-3)
              else: #probably seconds
                packet[element_cls.name] = element_cls(val)
            else:
              packet[element_cls.name] = element_cls(val)
              packet[element_cls.name].value = self.convert_to_metric(key, packet[element_cls.name].value)

          else:
            self.logger.warn("Adding unknown element ({} : {})".format(key, val))
            packet[key] = UnknownElement(val)
        
        if self.require_timestamp and TimestampElement.name not in packet \
           and DatetimeElement.name not in packet:

          self.logger.critical("Could not find any time elements when require_timestamp was set")

        if len(packet) > 0:
          self.logger.info("Adding new packet.")
          tel.append(packet)
        else:
          self.logger.warn("No telemetry was found in block. Packet is empty, skipping.")

    if len(tel) == 0:
      self.logger.warn("No telemetry was found. Returning empty Telemetry()")
    return tel

  def convert_to_metric(self, key: str, val: float):
    if ("feet" in key):
      return  val * 0.3048
    if ("mph" in key):
      return  val * 0.44704
    
    return val
