from .parser import Parser
from .telemetry import Telemetry
from .packet import Packet
from .element import Element, UnknownElement
from .elements import TimestampElement, DatetimeElement

import xml.etree.ElementTree as ET
from dateutil import parser as dup
import logging

# Reference: http://www.topografix.com/GPX/1/1/
class GPXParser(Parser):
  tel_type = 'gpx'

  def __init__(self, source, 
               convert_to_epoch: bool = False,
               require_timestamp: bool = False):
    super().__init__(source, 
                     convert_to_epoch = convert_to_epoch, 
                     require_timestamp = require_timestamp)
    self.logger = logging.getLogger("OTK.GPXParser")

  def read(self):
    tree = ET.parse(self.source)
    tel = Telemetry()
    self._traverse_tree(tree.getroot(), tel)
    if len(tel) == 0:
      self.logger.warn("No telemetry was found. Returning empty Telemetry()")
    return tel

  def _traverse_tree(self, node, tel):
    for child in node:
      # Ignore namespace if it exists
      tag = child.tag[child.tag.find('}')+1:]
      # These are all of the tags that contain the data we care about
      if tag in {"trkpt", "metadata", "rtept", "wpt"}:
        packet = Packet()
        self._extract_node(child, packet)

        if self.require_timestamp and TimestampElement.name not in packet \
            and DatetimeElement.name not in packet:

          self.logger.critical("Could not find any time elements when require_timestamp was set")

        if len(packet) > 0:
          self.logger.info("Adding new packet.")
          tel.append(packet)
        else:
          self.logger.warn("No telemetry was found in node. Packet is empty, skipping.")

      self._traverse_tree(child, tel)
  
  def _extract_node(self, node, packet):
    for key, val in node.items():
      self._add_element(packet, key, val)

    if node.text and not node.text.isspace():
      tag = node.tag[node.tag.find('}')+1:]
      self._add_element(packet, tag, node.text.strip())

    for child in node:
      self._extract_node(child, packet)

  def _add_element(self, packet, key, val):
      if key in self.element_dict:
        element_cls = self.element_dict[key]
        if element_cls == DatetimeElement and self.convert_to_epoch:
          val = dup.parse(val).timestamp()
          packet[TimestampElement.name] = TimestampElement(val)
        else:
          packet[element_cls.name] = element_cls(val)
      else: 
        self.logger.warn("Adding unknown element ({} : {})".format(key, val))
        packet[key] = UnknownElement(val)
