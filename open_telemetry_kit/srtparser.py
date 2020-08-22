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

class SRTParser(Parser):
  tel_type = "srt"

  def __init__(self,
               source: str, 
               is_embedded: bool = False, 
               convert_to_epoch: bool = False, 
               require_timestamp: bool = False):
    super().__init__(source, 
                     convert_to_epoch = convert_to_epoch, 
                     require_timestamp = require_timestamp)
    self.is_embedded = is_embedded
    self.beg_timestamp = 0
    self.convert_to_epoch = convert_to_epoch
    self.logger = logging.getLogger("OTK.SRTParser")

  def read(self) -> Telemetry:
    tel = Telemetry()

    _, _, ext = detector.split_path(self.source)
    if self.is_embedded and ext != ".srt":
      if self.require_timestamp:
        video_metadata = detector.read_video_metadata(self.source)
        if video_metadata and "streams" in video_metadata \
           and "tags" in video_metadata["streams"][0]     \
           and "creation_time" in video_metadata["streams"][0]["tags"]:

          video_datetime = video_metadata["streams"][0]["tags"]["creation_time"]
          self.beg_timestamp = dup.parse(video_datetime).timestamp()
          self.logger.info("Setting video creation time to: {}".format(self.beg_timestamp))
        else:
          self.logger.warn("Could not find creation time for video.")

      srt = detector.read_embedded_subtitles(self.source)
      self._process(srt.splitlines(True), tel)

    else:
      with open(self.source, 'r') as srt:
        self._process(srt, tel)

    if len(tel) == 0:
      self.logger.warn("No telemetry was found. Returning empty Telemetry()")

    return tel

  def _process(self, srt: str, tel: Telemetry):
    block = ""
    for line in srt:
      if line == '\n' and len(block) > 0:
        try:
          packet = Packet()
          sec_line_beg = block.find('\n') + 1
          sec_line_end = block.find('\n', sec_line_beg)
          timeframe = block[sec_line_beg : sec_line_end]
          data = block[sec_line_end + 1 : ]
          self._extractTimeframe(timeframe, packet)
          data = self._extractDatetime(data, packet)
          self._extractData(data, packet)
          if len(packet) > 0:
            self.logger.info("Adding new packet.")
            tel.append(packet)
          else:
            self.logger.warn("No telemetry was found in block. Packet is empty, skipping.")
        except Exception:
          self.logger.error("There was an error parsing this srt block. Skipping and continuing...")

        block = ""
      elif line == '\n':
        continue
      else:
        block += line

  # Example timeframe:
  # 00:00:00,033 --> 00:00:00,066
  def _extractTimeframe(self, line: str, packet: Dict[str, Element]):
    sep_pos = line.find("-->")
    if sep_pos > -1:
      tfb = (dup.parse(line[:sep_pos].strip()) - dup.parse("00:00:00")).total_seconds()
      packet[TimeframeBeginElement.name] = TimeframeBeginElement(tfb)
      tfe = (dup.parse(line[sep_pos+3:].strip()) - dup.parse("00:00:00")).total_seconds()
      packet[TimeframeEndElement.name] = TimeframeEndElement(tfe)
    else:
      # Timeframes in this format are one of the few defined requirements in srt
      # If one wasn't found either parsing failed or this file doesn't follow the standard
      self.logger.error("No timeframe was found. It is likely something went wrong with parsing")

  # Example datetimes
  # 2019-09-25 01:22:35,118,697
  # Jun 19, 2019 4:47:39 PM
  def _extractDatetime(self, block: str, packet: Dict[str, Element]):
    # This should find any reasonably formatted (and some not so reasonably formatted) datetimes
    # Looks for:
    # 1+ alphanum, [space, tab, '/', '-',  or .'], 1+ digits, [space, tab, '/', '-',  or .']       Date 
    #   1+ digits, 1+ whitespace,                                                                  Date 
    #   1+ digits, ':' 1+ digits, ':', 1+ digits, ['.' or ','], 0+ whitespace, 0+ digits,          Time 
    #   the same separator previously found, 0+ whitespace, 0+ digits, period identifier           Time 
    match = re.search(r"\w+[ \t,-/.]*\d+[ \t,-/.]*\d+[ \t]*\d+:\d+:\d+([.,])?[ \t]*\d*\1?[ \t]*\d*[ \t]*[aApPmM.]{0,2}", block)

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
        self.logger.info("Converting datetime to epoch")
        dt = dup.parse(dt).timestamp()
        packet[TimestampElement.name] = TimestampElement(dt)
      else:
        packet[DatetimeElement.name] = DatetimeElement(dt)

      return block[0 : match.start()] + block[match.end():]
    
    elif self.require_timestamp:
      if self.beg_timestamp != 0:
        self.logger.info("No datetime was found. Using timeframe and video creation time to estimate timestamp")
        tfb = packet[TimeframeBeginElement.name].value
        tfe = packet[TimeframeEndElement.name].value
        avg = (tfb+tfe) / 2
        packet[TimestampElement.name] = TimestampElement(self.beg_timestamp + avg)

      else:
        self.logger.critical("Could not find any time elements when require_timestamp was set")

    return block

  # Try to identify how data is formated.
  # See respective methods for exampls of each data format
  def _extractData(self, block: str, packet: Dict[str, Element]):
    # Make single line. Dealing with excess whitespace later
    block = block.lstrip()
    if block[0].isalpha():
      self._extractLabeledList(block, packet)
    elif "[" in block:
      self._extractBracket(block, packet)
    else:
      self._extractUnlabledList(block, packet)

    if LatitudeElement.name not in packet or  \
       LongitudeElement.name not in packet or \
       AltitudeElement.name not in packet:
      self.logger.warn("No or only partial GPS data found")

  # Looks for telemetry of the form:
  # F/7.1, SS 320, ISO 100, EV 0, GPS (-122.3699, 37.8166, 15), D 224.22m, H 58.20m, H.S 15.71m/s, V.S 0.10m/s 
  # OR
  # HOME(-122.1505,37.4245) 2019.07.06 19:05:07 //Note: timestamp and newlines will be removed by this point
  # GPS(-122.1509,37.4242,16) BAROMETER:80.0
  # ISO:110 Shutter:120 EV: 0 Fnum:F2.8
  def _extractLabeledList(self, block: str, packet: Dict[str, Element]):
    block = block.replace(',', ' ')
    separator = re.compile(r"[/ :\(]")
    numeric = re.compile(r"[\d\.-]+")
    space = re.compile(r"\s+")
    nonspace = re.compile(r"\S+")
    lbl_start = 0
    while lbl_start < len(block):
      match = separator.search(block, lbl_start)
      lbl_end = match.start()
      sep = match.end()
      label = block[lbl_start:lbl_end]
      if label in ["GPS", "HOME"]:
        end = self._extractGPS(block, lbl_start, packet)
        match = space.search(block, end)
        lbl_start = match.end()
      else:
        match = nonspace.search(block, sep)
        val_start = match.start()
        match = space.search(block, val_start)
        val_end = match.start()
        lbl_start = match.end()
        val_full = block[val_start:val_end]
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
        
  # Input can be:
  # HOME(-121.1505,37.4245)[...]
  # GPS (-122.3699, 37.8166, 15)[...]
  # GPS(-122.3699,37.5929,19) BAROMETER:64.3[...] //(long, lat) OR
  # GPS(37.8757,-122.3061,0.0M) BAROMETER:36.9M[...] //(lat, long)
  def _extractGPS(self, block: str, start: int, packet: Dict[str, Element]):
    gps_start = block.find('(', start)
    label = block[start:gps_start].strip()
    gps_end = block.find(')', gps_start)
    # end_line = block.find('\n', gps_end)

    # coord = re.compile(r"[-\d\.]+")
    coord_split = r"[ ]+"
    coords = re.split(coord_split, block[gps_start + 1 : gps_end])
    # coords = coord.findall(block, gps_start, gps_end)

    if len(coords) < 2:
      self.logger.error("Could not find GPS coordinates where expected")

    if label == "GPS":
      if block[gps_end - 1] == 'M':
        packet[LatitudeElement.name] = LatitudeElement(coords[0])
        packet[LongitudeElement.name] = LongitudeElement(coords[1])
      #long, lat
      else:
        packet[LongitudeElement.name] = LongitudeElement(coords[0])
        packet[LatitudeElement.name] = LatitudeElement(coords[1])

      if len(coords) == 3:
        # If a 'BAROMETER' value exists this will get overwritten
        # This is expected and desired behavior
        packet[AltitudeElement.name] = AltitudeElement(coords[2])

    else: #label == "HOME"
      if block[gps_end - 1] == 'M':
        packet[HomeLatitudeElement.name] = HomeLatitudeElement(coords[0])
        packet[HomeLongitudeElement.name] = HomeLongitudeElement(coords[1])
      #long, lat
      else:
        packet[HomeLongitudeElement.name] = HomeLongitudeElement(coords[0])
        packet[HomeLatitudeElement.name] = HomeLatitudeElement(coords[1])

      if len(coords) == 3:
        packet[HomeAltitudeElement.name] = HomeAltitudeElement(coords[2])

    return gps_end

  # brackets: [iso : 110] [shutter : 1/200.0] [fnum : 280] [ev : 0.7] [ct : 5064] [color_md : default] [focal_len : 240] [latitude: 0.608553] [longtitude: -1.963763] [altitude: 1429.697998]
  def _extractBracket(self, block: str, packet: Dict[str, Element]):
    # find the first '[' and last ']'
    data_start = block.find('[')
    data_end = block.rfind(']')
    data = block[data_start : data_end]
    data = data.replace(',','')

    # This will split on the common delimters found in DJIs srts and return a list
    # List _should_ be alternating keyword, value barring nothing weird from DJI
    # which they have proven is not a safe assumption
    data = re.split(r"[\[\]\s:]+", data)
    if not data[0]: #remove empty string from regex search
      data.pop(0)
    
    for i in range(0, len(data), 2):
      key = data[i]
      if key in self.element_dict:
        element_cls = self.element_dict[key]
        packet[element_cls.name] = element_cls(data[i+1])
      else:
        self.logger.warn("Adding unknown element ({} : {})".format(key, data[i+1]))
        packet[key] = UnknownElement(data[i+1])

  # whitespace: 38.47993, -122.69943, 115.5m, 302°
  def _extractUnlabledList(self, block: str, packet: Dict[str, Element]):
    data = block.strip().split(", ")
    if len(data) > 0 and len(data) <= 4:
      packet[LatitudeElement.name] = LatitudeElement(data[0])
      packet[LongitudeElement.name] = LongitudeElement(data[1])
      packet[AltitudeElement.name] = AltitudeElement(data[2].strip('m'))
      if len(data) > 3:
        packet[PlatformHeadingAngleElement.name] = PlatformHeadingAngleElement(data[3][0:-1])
