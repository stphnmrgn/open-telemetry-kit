from .parser import Parser
from .telemetry import Telemetry
from .packet import Packet
from .element import Element, UnknownElement
from .elements import TimestampElement, TimeframeBeginElement, TimeframeEndElement, DatetimeElement
from .elements import LatitudeElement, LongitudeElement, AltitudeElement, PlatformHeadingAngleElement
from .elements import HomeLatitudeElement, HomeLongitudeElement, HomeAltitudeElement
import open_telemetry_kit.detector as detector

from datetime import timedelta
from dateutil import parser as dup
import re
import os
from typing import Dict
import logging

class ASSParser(Parser):
  tel_type = "ass"

  def __init__(self,
               source: str, 
               is_embedded: bool = False, 
               convert_to_epoch: bool = False):
    super().__init__(source, 
                     convert_to_epoch = convert_to_epoch)
    self.is_embedded = is_embedded
    self.beg_timestamp = 0
    self.convert_to_epoch = convert_to_epoch
    self.logger = logging.getLogger("OTK.ASSParser")

  def read(self) -> Telemetry:
    tel = Telemetry()

    _, _, ext = detector.split_path(self.source)
    if self.is_embedded and ext != ".ass":
      ass = detector.read_embedded_subtitles(self.source, "ass")
      self._process(ass.splitlines(True), tel)

    else:
      with open(self.source, 'r') as srt:
        self._process(srt, tel)

    if len(tel) == 0:
      self.logger.warn("No telemetry was found. Returning empty Telemetry()")

    return tel

  def _process(self, srt: str, tel: Telemetry):
    for line in srt:
      if "Dialogue" in line:
        packet = Packet()
        self._parseLine(line, packet)
        tel.append(packet)

  # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
  # Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,HOME(W: 97.616776, N: 30.219286) 2020-11-01 15:29:24\NGPS(W: 97.621475, N: 30.214199, 161) \NISO:105 SHUTTER:500 EV:0.0 F-NUM:2.8
  def _parseLine(self, line: str, packet: Dict[str, Element]):
    line = line.replace("Dialogue: ", "")
    elements = line.split(',', maxsplit=9)
    tfb = (dup.parse(elements[1]) - dup.parse("00:00:00")).total_seconds()
    packet[TimeframeBeginElement.name] = TimeframeBeginElement(tfb)
    tfe = (dup.parse(elements[2]) - dup.parse("00:00:00")).total_seconds()
    packet[TimeframeEndElement.name] = TimeframeEndElement(tfe)
    data = self._extractDatetime(elements[-1], packet)
    self._extractData(data, packet)

  # Example datetimes
  # 2019-09-25 01:22:35,118,697
  # Jun 19, 2019 4:47:39 PM
  def _extractDatetime(self, data: str, packet: Dict[str, Element]):
    # This should find any reasonably formatted (and some not so reasonably formatted) datetimes
    # Looks for:
    # 1+ alphanum, [space, tab, '/', '-',  or .'], 1+ digits, [space, tab, '/', '-',  or .']       Date 
    #   1+ digits, 1+ whitespace,                                                                  Date 
    #   1+ digits, ':' 1+ digits, ':', 1+ digits, ['.' or ','], 0+ whitespace, 0+ digits,          Time 
    #   the same separator previously found, 0+ whitespace, 0+ digits, period identifier           Time 
    match = re.search(r"\w+[ \t,-/.]*\d+[ \t,-/.]*\d+[ \t]*\d+:\d+:\d+([.,])?[ \t]*\d*\1?[ \t]*\d*[ \t]*[aApPmM.]{0,2}", data)

    # dateutil is pretty good, but can't handle the double microsecond separator 
    # that sometimes shows up in DJIs telemetry so check to see if it exists and get rid of it
    # Also, convert to epoch microseconds while we're at it
    if match:
      micro_syn = match[1]
      dt = match[0]
      if micro_syn and dt.count(micro_syn) > 1:
        #concatentate timestamp pre-2nd separator with post-2nd separator
        dt = dt[:dt.rfind(micro_syn)] + dt[dt.rfind(micro_syn)+1:]
      
      if (self.convert_to_epoch):
        self.logger.debug("Converting datetime to epoch")
        dt = dup.parse(dt).timestamp()
        packet[TimestampElement.name] = TimestampElement(dt)
      else:
        packet[DatetimeElement.name] = DatetimeElement(dt)

      return data[0 : match.start()] + data[match.end():]
    
    elif self.require_timestamp:
      if self.beg_timestamp != 0:
        self.logger.info("No datetime was found. Using timeframe and video creation time to estimate timestamp")
        tfb = packet[TimeframeBeginElement.name].value
        tfe = packet[TimeframeEndElement.name].value
        avg = (tfb+tfe) / 2
        packet[TimestampElement.name] = TimestampElement(self.beg_timestamp + avg)

      else:
        self.logger.critical("Could not find any time elements when require_timestamp was set")

    return data

  def _extractData(self, data: str, packet: Dict[str, Element]):
    data = data.replace(r"\N", "")

    lbl_val_delim = re.compile(r"[/ :\(]")
    numeric = re.compile(r"[\d\./-]+")
    space = re.compile(r"\s+")
    nonspace = re.compile(r"\S+")

    lbl_start = 0
    while lbl_start < len(data):
      match = lbl_val_delim.search(data, lbl_start)
      lbl_end = match.start()
      sep = match.end()
      label = data[lbl_start:lbl_end]
      if label in ["GPS", "HOME"]:
        end = self._extractGPS(data, lbl_start, packet)
        match = space.search(data, end)
        lbl_start = match.end()
      else:
        match = nonspace.search(data, sep)
        val_start = match.start()
        match = space.search(data, val_start)
        val_end = match.start()
        lbl_start = match.end()
        val_full = data[val_start:val_end]
        match = numeric.search(val_full)
        try:
          val = match[0]
          if label in self.element_dict:
            packet[self.element_dict[label].name] = self.element_dict[label](val)
          else:
            self.logger.warn("Adding unknown element ({} : {})".format(label, val))
            packet[label] = UnknownElement(val)
        except:
          self.logger.info("Could not find valid value for '{}' element".format(label))

    if LatitudeElement.name not in packet or  \
       LongitudeElement.name not in packet or \
       AltitudeElement.name not in packet:
      self.logger.warn("No or only partial GPS data found")

        
  # HOME(W: 122.254875, N: 38.124855)  GPS(W: 122.252266, N: 38.128864, 91)
  def _extractGPS(self, line: str, start: int, packet: Dict[str, Element]):

    gps_start = line.find('(', start)
    label = line[start:gps_start].strip()
    gps_end = line.find(')', gps_start)

    coord_split = r", "
    coords = re.split(coord_split, line[gps_start + 1 : gps_end])
    numeric = re.compile(r"[\d\.-]+")
    # coords = [numeric.search(coord)[0] for coord in coords ]

    if len(coords) < 2:
      self.logger.error("Could not find GPS coordinates where expected")

    if label == "GPS":
      packet[LongitudeElement.name] = LongitudeElement( numeric.search(coords[0])[0] )
      if 'W' in coords[0]:
        packet[LongitudeElement.name].value *= -1

      packet[LatitudeElement.name] = LatitudeElement( numeric.search(coords[1])[0] )
      if 'S' in coords[1]:
        packet[LongitudeElement.name].value *= -1

      if len(coords) == 3:
        packet[AltitudeElement.name] = AltitudeElement(coords[2])

    else: #label == "HOME"
      packet[HomeLongitudeElement.name] = HomeLongitudeElement(numeric.search(coords[0])[0])
      if 'W' in coords[0]:
        packet[HomeLongitudeElement.name].value *= -1

      packet[HomeLatitudeElement.name] = HomeLatitudeElement(numeric.search(coords[1])[0])
      if 'S' in coords[1]:
        packet[HomeLongitudeElement.name].value *= -1

      if len(coords) == 3:
        packet[HomeAltitudeElement.name] = HomeAltitudeElement(coords[2])

    return gps_end
