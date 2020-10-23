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
  def __init__(self, source, 
               convert_to_epoch: bool = False):
    super().__init__(source, 
                     convert_to_epoch = convert_to_epoch)
    self.logger = logging.getLogger("OTK.BlackvueParser")
    
  def read(self) -> Telemetry:
    tel = Telemetry()
    with open(self.source, 'rb') as fd:

      fd.seek(0, io.SEEK_END)
      eof = fd.tell()
      fd.seek(0)
      date = None

      first_gps_date = None
      first_gps_time = None
      found_first_gps_date = False
      found_first_gps_time = False

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
              match = re.search('\[([0-9]+)\]', l)
              if match and match.group(1) != timestamp:
                if packet:
                  tel.append(packet)
                packet = Packet()
                timestamp = match.group(1)
                packet[TimestampElement.name] = TimestampElement(float(timestamp) * 1e-3)

              m = l.lstrip('[]0123456789')
             ###############################################################################
             ############################################################################### 
              #By default, use camera timestamp. Only use GPS Timestamp if camera was not set up correctly and date/time is wrong
              # if using camera ts - only use GPGGA info with exception of GPRMC as possible first data point
              # If not using camera tx (ie using GPS ts) - use both GPGGA and GPRMC
              # Why tho...
              if use_nmea_stream_timestamp==False:
                if "$GPGGA" in m:
                  match = re.search('\[([0-9]+)\]', l)
                  if match:
                    epoch_in_local_time = match.group(1)

                  camera_date=datetime.datetime.utcfromtimestamp(int(epoch_in_local_time)/1000.0)
                  data = pynmea2.parse(m)
                  if(data.is_valid):
                    if  found_first_gps_time == False:
                      first_gps_time = data.timestamp
                      found_first_gps_time = True
                    lat, lon, alt = data.latitude, data.longitude, data.altitude
                    points.append((camera_date, lat, lon, alt))

              if use_nmea_stream_timestamp==True or found_first_gps_date==False:
                if "GPRMC" in m:
                  try:
                    data = pynmea2.parse(m)
                    if data.is_valid:
                      date = data.datetime.date()
                      if found_first_gps_date == False:
                        first_gps_date=date
                  except pynmea2.ChecksumError as e:
                    # There are often Checksum errors in the GPS stream, better not to show errors to user
                    pass
                  except Exception as e:
                    print(
                      "Warning: Error in parsing gps trace to extract date information, nmea parsing failed")
              if use_nmea_stream_timestamp==True:
                if "$GPGGA" in m:
                  try:
                    data = pynmea2.parse(m)
                    if(data.is_valid):
                      lat, lon, alt = data.latitude, data.longitude, data.altitude
                      if not date:
                        timestamp = data.timestamp
                      else:
                        timestamp = datetime.datetime.combine(
                        date, data.timestamp)
                      points.append((timestamp, lat, lon, alt))

                  except Exception as e:
                    print(
                      "Error in parsing gps trace to extract time and gps information, nmea parsing failed due to {}".format(e))
            
            #If there are no points after parsing just return empty vector
            if points == []:
              return []
            #After parsing all points, fix timedate issues
            if use_nmea_stream_timestamp==False:
              # If we use the camera timestamp, we need to get the timezone offset, since Mapillary backend expects UTC timestamps
              first_gps_timestamp = datetime.datetime.combine(first_gps_date, first_gps_time)
              delta_t = points[0][0]-first_gps_timestamp
              if delta_t.days>0:
                hours_diff_to_utc = round(delta_t.total_seconds()/3600)
              else:
                hours_diff_to_utc = round(delta_t.total_seconds()/3600) * -1
              utc_points=[]
              for idx, point in enumerate(points):
                delay_compensation = datetime.timedelta(seconds=-1.8) #Compensate for solution age when location gets timestamped by camera clock. Value is empirical from various cameras/recordings
                new_timestamp = points[idx][0]+datetime.timedelta(hours=hours_diff_to_utc)+delay_compensation
                lat = points[idx][1]
                lon = points[idx][2]
                alt = points[idx][3]
                utc_points.append((new_timestamp, lat, lon, alt))

              points = utc_points
              points.sort()

            else:
              #add date to points that don't have it yet, because GPRMC message came later 
              utc_points=[]
              for idx, point in enumerate(points):
                if type(points[idx][0]) != type(datetime.datetime.today()):
                  timestamp = datetime.datetime.combine(
                      first_gps_date, points[idx][0])
                else:
                  timestamp = points[idx][0]                  
                  lat = points[idx][1]
                  lon = points[idx][2]
                  alt = points[idx][3]
                  utc_points.append((timestamp, lat, lon, alt))

                points = utc_points
                points.sort()

            offset += newb.end
             ###############################################################################
             ############################################################################### 

        break

    return points
