'''
Core parsing logic taken from Mapillary Tools which uses the following license

Copyright (c) 2018, mapillary
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from .parser import Parser
from .telemetry import Telemetry
from .packet import Packet
from .element import UnknownElement
from .elements import TimestampElement, DatetimeElement
from .elements import LatitudeElement, LongitudeElement, AltitudeElement
from .elements import SpeedElement

import datetime
import io
import logging
import os
import sys
import re
import pynmea2
from pymp4.parser import Box
from construct.core import RangeError, ConstError
from dateutil import parser as dup

'''
Pulls geo data out of a BlackVue video files
'''
class BlackvueParser(Parser):
  tel_type = "blackvue"

  def __init__(self, source):
    super().__init__(source)
    self.logger = logging.getLogger("OTK.BlackvueParser")
    
  def read(self) -> Telemetry:
    tel = Telemetry()
    with open(self.source, 'rb') as fd:

      fd.seek(0, io.SEEK_END)
      eof = fd.tell()
      fd.seek(0)

      while fd.tell() < eof:
        try:
          box = Box.parse_stream(fd)
        except RangeError:
          print('error parsing blackvue GPS information, exiting')
          sys.exit(1)
        except ConstError:
          print('error parsing blackvue GPS information, exiting')
          sys.exit(1)

        if box.type.decode('utf-8') == 'free':
          length = len(box.data)
          offset = 0
          while offset < length:
            newb = Box.parse(box.data[offset:])
            if newb.type.decode('utf-8') == 'gps':
              lines = newb.data.decode('utf-8')

              # Parse GPS trace
              timestamp = None
              packet = None
              for l in lines.splitlines():
                m = l.lstrip('[]0123456789')
                if not m:
                  continue

                match = re.search('\[([0-9]+)\]', l)
                # If new timestamp found
                if match and match.group(1) != timestamp:
                  if packet:
                    tel.append(packet)
                  packet = Packet()
                  timestamp = match.group(1)
                  packet[TimestampElement.name] = TimestampElement(float(timestamp) * 1e-3)

                #remove timestamp on tail if it exists
                try:
                  m = m[:m.rindex('[')]
                except:
                  pass

                try:
                  m = m[:m.index("\x00")]
                except:
                  pass

                try:
                  nmea_data = pynmea2.parse(m)
                  if nmea_data and nmea_data.sentence_type == 'GGA':
                    packet[LatitudeElement.name] = LatitudeElement(nmea_data.latitude)
                    packet[LongitudeElement.name] = LongitudeElement(nmea_data.longitude)
                    if nmea_data.altitude:
                      packet[AltitudeElement.name] = AltitudeElement(nmea_data.altitude)
                  if nmea_data and nmea_data.sentence_type == 'VTG':
                    packet[SpeedElement.name] = SpeedElement(nmea_data.spd_over_grnd_kmph / 3.6) #convert to m/s
                except:
                  self.logger.warn("Couldn't parse nmea sentence. Skipping...")

              if packet:
                tel.append(packet)
            offset += newb.end
          break

      return tel
