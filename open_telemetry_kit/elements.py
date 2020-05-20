from .element import Element, FloatElement, IntElement, StrElement
from .misb_0601 import MISB0601, IntMISB, FloatMISB, StrMISB 
from .klv_common import bytes_to_int, bytes_to_float, bytes_to_str, read_len, read_ber_oid
from datetime import datetime
from dateutil import parser as dup
from io import BytesIO
from typing import List

class ChecksumElement(IntElement, IntMISB):
  name = "checksum"
  names = {"checksum", "Checksum"}

  misb_name = "Checksum"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 03 01 00 00 00"
  misb_tag = 1
  misb_units = "None"

class TimestampElement(FloatElement, IntMISB):
  name = "timestamp"
  names = {"timestamp", "Timestamp", "time stamp", "Time Stamp"}

  misb_name = "Precision Time Stamp"
  misb_key = "06 0E 2B 34 01 01 01 03 07 02 01 01 01 05 00 00"
  misb_tag = 2
  misb_units = "Microseconds"

  _state_code = {0 : "seconds",
                1 : "milliseconds",
                2 : "microseconds"}

  # Python returns a float value in seconds for timestamp so conform to that 
  def __init__(self, value: float):
    super().__init__(value)
    self.state = self._state_code[0]

  @classmethod
  def fromMISB(cls, value: bytes):
    # Initialize as 0 to avoid converting back and for between [micro]seconds
    ts = cls(0).to_microseconds()
    ts.value = bytes_to_int(value)
    return ts
  
  def to_seconds(self):
    if self.state == self._state_code[1]:
      self.value = self.value * 1e-3
      self.state = self._state_code[0]

    elif self.state == self._state_code[2]:
      self.value = self.value * 1e-6
      self.state = self._state_code[0]

    return self

  def to_milliseconds(self):
    if self.state == self._state_code[0]:
      self.value = self.value * 1e3
      self.state = self._state_code[1]

    elif self.state == self._state_code[2]:
      self.value = self.value * 1e-3
      self.state = self._state_code[1]

    return self

  def to_microseconds(self):
    if self.state == self._state_code[0]:
      self.value = int(self.value * 1e6)
      self.state = self._state_code[2]

    elif self.state == self._state_code[1]:
      self.value = int(self.value * 1e3)
      self.state = self._state_code[2]

    return self

class DatetimeElement(Element):
  name = "datetime"
  names = {"datetime", "Datetime", "DateTime", "time", "datetime(utc)"}

  def __init__(self, value: datetime):
    self.value = dup.parse(value)

  def toJson(self) -> str:
    return str(self.value)

class MissionIDElement(StrElement, StrMISB):
  name = "missionID" 
  names = {"missionID", "MissionId", "Missionid", "missionID",
           "missionId", "missionid"}

  misb_name = "Mission ID"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 01 03 00 00 00"
  misb_tag = 3
  misb_units = "None"

class PlatformHeadingAngleElement(FloatElement, FloatMISB):
  name = "platformHeadingAngle"
  names = {"platformHeadingAngle", "PlatformHeadingAngle", "platformheadingangle",
           "headingAngle", "HeadingAngle", "headingangle", "Heading Angle",
           "heading angle", "heading", "Heading", "yaw", "Yaw", "yaw(deg)", "compass_heading(degrees)"}

  misb_name = "Platform Heading Angle"
  misb_key = "06 0E 2B 34 01 01 01 07 07 01 10 01 06 00 00 00"
  misb_tag = 5
  misb_units = "Degrees"
  _domain = (0, 2**16 - 1)
  _range = (0, 360)

class PlatformPitchAngleElement(FloatElement, FloatMISB):
  name = "platformPitchAngleShort"
  names = {"platformPitchAngleShort", "PlatformPitchAngleShort", "platformpitchangleshort",
           "pitchAngleShort", "PitchAngleShort", "pitchangleshort", "Pitch Angle Short", 
           "pitch angle short"}

  misb_name = "Platform Pitch Angle"
  misb_key = "06 0E 2B 34 01 01 01 07 07 01 10 01 05 00 00 00"
  misb_tag = 6
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-20, 20)
  _invalid = bytes.fromhex('8000')

class PlatformPitchAngleFullElement(FloatElement, FloatMISB):
  name = "platformPitchAngleFull"
  names = {"platformPitchAngleFull", "PlatformPitchAngleFull", "platformpitchangleFull",
           "pitchAngleFull", "PitchAngleFull", "pitchanglefull", "Pitch Angle Full", 
           "pitch angle full", "pitch", "Pitch", "pitch(deg)", "pitch(degrees)"}

  misb_name = "Platform Pitch Angle (Full)"
  misb_key = "06 0E 2B 34 01 01 01 07 07 01 10 01 05 00 00 00"
  misb_tag = 90
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('80000000')

class PlatformRollAngleElement(FloatElement, FloatMISB):
  name = "platformRollAngleShort"
  names = {"platformRollAngleShort", "PlatformRollAngleShort", "platformrollangleshort",
           "rollAngleShort", "RollAngleShort", "rollangleshort", "Roll Angle Short",
           "roll angle short", "roll short", "Roll Short"}

  misb_name = "Platform Roll Angle"
  misb_key = "06 0E 2B 34 01 01 01 07 07 01 10 01 04 00 00 00"
  misb_tag = 7
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-50, 50)
  _invalid = bytes.fromhex('8000')

class PlatformRollAngleFullElement(FloatElement, FloatMISB):
  name = "platformRollAngleFull"
  names = {"platformRollAngleFull", "PlatformRollAngleFull", "platformrollanglefull",
           "rollAngleFull", "RollAngleFull", "rollanglefull", "Roll Angle Full",
           "roll angle full", "roll full", "Roll Full", "roll", "Roll", "roll(deg)", "roll(degrees)"}

  misb_name = "Platform Roll Angle (Full)"
  misb_key = "06 0E 2B 34 01 01 01 07 07 01 10 01 04 00 00 00"
  misb_tag = 91
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('80000000')

class PlatformDesignationElement(StrElement, StrMISB):
  name = "platformDesignation"
  names = {"platformDesignation", "PlatformDesignation", "platformdesignation",
           "Platform Designation", "platform designation", "platform", "model"}

  misb_name = "Platform Designation"
  misb_key = "06 0E 2B 34 01 01 01 01 01 01 20 01 00 00 00 00"
  misb_tag = 10
  misb_units = "None"

class ImageSourceSensorElement(StrElement, StrMISB):
  name = "imageSourceSensor"
  names = {"imageSourceSensor", "ImageSourceSensor", "imagesourcesensor",
           "Image Source Sensor", "image source sensor", "Image Source", 
           "image source", "Source Sensor", "source sensor"}

  misb_name = "Image Source Sensor"
  misb_key = "06 0E 2B 34 01 01 01 01 04 20 01 02 01 01 00 00"
  misb_tag = 11
  misb_units = "None"

class ImageCoordinateSystemElement(StrElement, StrMISB):
  name = "imageCoordinateSystem"
  names = {"imageCoordinateSystem", "ImageCoordinateSystem", "imagecoordinateSystem",
           "Image Coordinate System", "image coordinate system", "Coordinate System",
           "coordinate system"}

  misb_name = "Image Coordinate System"
  misb_key = "06 0E 2B 34 01 01 01 01 07 01 01 01 00 00 00 00"
  misb_tag = 12
  misb_units = "None"

class LatitudeElement(FloatElement, FloatMISB):
  name = "latitude"
  names = {"Latitude", "latitude", "sensorLatitude", "SensorLatitude", "sensorlatitude",
           "Sensor Latitude", "sensor latitude", "Lat", "lat", "LATITUDE", "LAT"}

  misb_name = "Sensor Latitude"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 02 04 02 00"
  misb_tag = 13
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class LongitudeElement(FloatElement, FloatMISB):
  name = "longitude"
  names = {"Longitude", "longitude", "sensorLongitude", "SensorLongitude",
           "sensorlongitude", "Sensor Longitude", "sensor longitude", "Long", "long",
           "LONG", "Lon", "lon", "LON", "longtitude"} #DJI can't spell

  misb_name = "Sensor Longitude"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 02 06 02 00"
  misb_tag = 14
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class AltitudeElement(FloatElement, FloatMISB):
  name = "altitude"
  names = {"Altitude", "altitude", "sensorTrueAltitude", "SensorTrueAltitude",
           "sensortruealtitude", "Sensor True Altitude", "sensor true altitude",
           "ALT", "Alt", "alt", "Altitude (m)", "ele", "BAROMETER", "altitude(feet)",
           "altitude_above_seaLevel(meters)"}

  misb_name = "Sensor True Altitude"
  misb_key = "06 0E 2B 34 01 01 01 01 07 01 02 01 02 02 00 00"
  misb_tag = 15
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (-900, 19000)

class SensorEllipsoidHeightElement(FloatElement, FloatMISB):
  name = "sensorEllipsoidHeight"
  names = {"sensorEllipsoidHeight", "SensorEllipsoidHeight", "sensorellipsoidheight",
           "Sensor Ellipsoid Height", "sensor ellipsoid height"}

  misb_name = "Sensor Ellipsoid Height"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 01 82 47 00 00"
  misb_tag = 75
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (-900, 19000)

class SensorEllipsoidHeightExtendedElement(FloatElement, FloatMISB):
  name = "sensorEllipsoidHeightExtended"
  names = {"sensorEllipsoidHeightExtended", "SensorEllipsoidHeightExtended",
           "sensorellipsoidheightextended", "Sensor Ellipsoid Height Extended",
           "sensor ellipsoid heigt extended"}

  misb_name = "Sensor Ellipsoid Height Extended"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 01 82 47 00 00"
  misb_tag = 104
  misb_units = "Meters"
  _domain = "IMAPB"
  _range = (-900, 40000)

class SensorHorizontalFOVElement(FloatElement, FloatMISB):
  name = "sensorHorizontalFOV"
  names = {"sensorHorizontalFOV", "SensorHorizontalFOV", "sensorhorizontalfov",
           "Sensor Horizontal FOV", "sensor horizontal FOV", "sensor horizontal fov",
           "Horizontal FOV", "horizontal FOV", "horizontal fov", "Horizontal FOV (deg)",
           "sensorHorizontalFov"}

  misb_name = "Sensor Horizontal Field of View"
  misb_key = "06 0E 2B 34 01 01 01 02 04 20 02 01 01 08 00 00"
  misb_tag = 16
  misb_units = "Degrees"
  _domain = (0, 2**16 - 1)
  _range = (0, 180)

class SensorVerticalFOVElement(FloatElement, FloatMISB):
  name = "sensorVerticalFOV"
  names = {"sensorVerticalFOV", "SensorVerticalFOV", "sensorverticalfov",
           "Sensor Vertical FOV", "sensor vertical FOV", "sensor vertical fov",
           "Vertical FOV", "vertical FOV", "vertical fov", "Vertical FOV (deg)",
           "sensorVerticalFov"}

  misb_name = "Sensor Vertical Field of View"
  misb_key = "06 0E 2B 34 01 01 01 07 04 20 02 01 01 0A 01 00"
  misb_tag = 17
  misb_units = "Degrees"
  _domain = (0, 2**16 - 1)
  _range = (0, 180)

class SensorRelativeAzimuthAngleElement(FloatElement, FloatMISB):
  name = "sensorRelativeAzimuthAngle"
  names = {"sensorRelativeAzimuthAngle", "SensorRelativeAzimuthAngle",
           "sensorrelaztiveazimuthangle", "Sensor Relative Azimuth Angle",
           "sensor relative azimuth angle", "azimuthAngle", "AzimuthAngle",
           "azimuthangle", "Azimuth Angle", "azimuth angle", "Pan", "pan", "Pan (deg)"}

  misb_name = "Sensor Relative Azimuth Angle"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 04 00 00 00"
  misb_tag = 18
  misb_units = "Degrees"
  _domain = (0, 2**32 - 1)
  _range = (0, 360)

class SensorRelativeElevationAngleElement(FloatElement, FloatMISB):
  name = "sensorRelativeElevationAngle"
  names = {"sensorRelativeElevationAngle", "SensorRelativeElevationAngle",
           "sensorrelativeelevationangle", "Sensor Relative Elevation Angle",
           "sensor relative elevation angle", "Tilt", "tilt", "Tilt (deg)"}

  misb_name = "Sensor Relative Elevation Angle"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 05 00 00 00"
  misb_tag = 19
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class SensorRelativeRollAngleElement(FloatElement, FloatMISB):
  name = "sensorRelativeRollAngle"
  names = {"sensorRelativeRollAngle", "SensorRelativeRollAngle",
           "sensorrelativerollangle", "Sensor Relative Roll Angle",
           "sensor relative roll angle", "Roll", "roll", "Roll (deg)"}

  misb_name = "Sensor Relative Roll Angle"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 06 00 00 00"
  misb_tag = 20
  misb_units = "Degrees"
  _domain = (0, 2**32 - 1)
  _range = (0, 360)

class SlantRangeElement(FloatElement, FloatMISB):
  name = "slantRange"
  names = {"slantRange", "SlantRange", "slantrange", "Slant Range", "slant range",
           "Slant Range (m)"}

  misb_name = "Slant Range"
  misb_key = "06 0E 2B 34 01 01 01 01 07 01 08 01 01 00 00 00"
  misb_tag = 21
  misb_units = "Meters"
  _domain = (0, 2**32 - 1)
  _range = (0, 5000000)

class TargetWidthElement(FloatElement, FloatMISB):
  name = "targetWidth"
  names = {"targetWidth", "TargetWidth", "targetwidth", "Target Width", "target width",
           "Horizontal Span (m)"}

  misb_name = "Target Width"
  misb_key = "06 0E 2B 34 01 01 01 01 07 01 09 02 01 00 00 00"
  misb_tag = 22
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (0, 10000)

class TargetWidthExtendedElement(FloatElement, FloatMISB):
  name = "targetWidthExtended"
  names = {"targetWidthExtended", "TargetWidthExtended", "targetwidthextended",
           "Target Width Extended", "target width extended"}

  misb_name = "Target Width Extended"
  misb_key = "06 0E 2B 34 01 01 01 01 07 01 09 02 01 00 00 00"
  misb_tag = 96
  misb_units = "Meters"
  _domain = "IMAPB"
  _range = (0, 1500000)

class FrameCenterLatitudeElement(FloatElement, FloatMISB):
  name = "frameCenterLatitude"
  names = {"frameCenterLatitude", "FrameCenterLatitude", "framecenterlatitude",
           "Frame Center Latitude", "frame center latitude", "Center Latitude",
           "center latitude"}

  misb_name = "Frame Center Latitude"
  misb_key = "06 0E 2B 34 01 01 01 01 07 01 02 01 03 02 00 00"
  misb_tag = 23
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class FrameCenterLongitudeElement(FloatElement, FloatMISB):
  name = "frameCenterLongitude"
  names = {"frameCenterLongitude", "FrameCenterLongitude", "framecenterlongitude",
           "Frame Center Longitude", "frame center longitude", "Center Longitude",
           "center longitude"}

  misb_name = "Frame Center Longitude "
  misb_key = "06 0E 2B 34 01 01 01 01 07 01 02 01 03 04 00 00"
  misb_tag = 24
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class FrameCenterElevationElement(FloatElement, FloatMISB):
  name = "frameCenterAltitude"
  names = {"frameCenterAltitude", "FrameCenterAltitude", "framecenteraltitude",
           "Frame Center Altitude", "frame center altitude", "Center Altitude",
           "center altitude", "Center Altitude (m)", "frameCenterElevation",
           "FrameCenterElevation", "framecenterelevation"}

  misb_name = "Frame Center Elevation "
  misb_key = "06 0E 2B 34 01 01 01 0A 07 01 02 01 03 16 00 00"
  misb_tag = 25
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (-900, 19000)

class FrameCenterHeightAboveEllipsoidElement(FloatElement, FloatMISB):
  name = "frameCenterHeightAboveEllipsoid"
  names = {"frameCenterHeightAboveEllipsoid", "FrameCenterHeightAboveEllipsoid",
           "framecenterheightaboveellipsoid", "Frame Center Height Above Ellipsoid",
           "frame center height above ellipsoid"}

  misb_name = "Frame Center Height Above Ellipsoid"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 03 48 00 00 00"
  misb_tag = 78
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (-900, 19000)

class UASLocalSetVersionElement(IntElement, IntMISB):
  name = "UASLocalSetVersion"
  names = {"UASLocalSetVersion", "uaslocalsetversion", "UAS Local Set Version",
           "uas local set version", "uasLocalSetVersion"}

  misb_name = "UAS Datalink LS Version Number"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 03 03 00 00 00"
  misb_tag = 65
  misb_units = "None"

# class MotionImageryCoreIdentifierElement(Element):
#   #This is a KVL/MISB specific element
#   #This doesn't seem to be correctly implemented anywhere so just going to leave
#   #it commented out until further notice
#   name = "motionImageryCoreIdentifier"
#   names = {"motionImageryCoreIdentifier"}

#   def __init__(self, value: float):
#     self.value = value
  
class SensorWGS84AltitudeElement(FloatElement):
  name = "sensorWGS84Altitude"
  names = {"sensorWGS84Altitude", "SensorWGS84Altitude", "sensorWGS84altitude",
           "sensortwgs64altitude"}

class SensorGroundAltitudeElement(FloatElement):
  name = "sensorGroundAltitude"
  names = {"sensorGroundAltitude", "SensorGroundAltitude", "sensorgroundaltitude",
           "Sensor Ground Altitude", "sensor ground altitude"}

class SensorLaunchAltitudeElement(FloatElement):
  name = "sensorLaunchAltitude"
  names = {"sensorLaunchAltitude", "SensorLaunchAltitude", "sensorlaunchaltitude",
           "Sensor Launch Altitude", "sensor launch altitude"}

class TimeframeBeginElement(FloatElement):
  name = "timeframeBegin"
  names = {"timeframeBegin", "TimeframeBegin", "timeframebegin", "Timeframe Begin",
           "timeframe begin", "time(millisecond)"}

class TimeframeEndElement(FloatElement):
  name = "timeframeEnd"
  names = {"timeframeEnd", "TimeframeEnd", "timeframeend", "Timeframe End",
           "timeframe end"}

class SpeedElement(FloatElement, IntMISB):
  name = "speed"
  names = {"speed", "Speed", "velocity", "Velocity", "badelf:speed", "speed(mph)", "speed(m/s)"}

  misb_name = "Platform True Airspeed"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 0A 00 00 00"
  misb_tag = 8
  misb_units = "Meters/Second"

class PlatformTailNumberElement(StrElement, StrMISB):
  name = "platformTailNumber"
  names = {"platformTailNumber"}

  misb_name = "Platform Tail Number"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 01 02 00 00 00"
  misb_tag = 4
  misb_units = "None"

class PlatformIndicatedAirspeedElement(IntElement, IntMISB):
  name = "platformIndicatedAirspeed"
  names = {"platformIndicatedAirspeed"}

  misb_name = "Platform Indicated Airspeed"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 0B 00 00 00"
  misb_tag = 9
  misb_units = "Meters/Second"

class OffsetCornerLatitudePoint1Element(FloatElement, FloatMISB):
  name = "offsetCornerLatitude"
  names = {"offsetCornerLatitude"}

  misb_name = "Offset Corner Latitude Point 1"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 07 01 00"
  misb_tag = 26
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLat (Tag 23)
  _invalid = bytes.fromhex('8000')

class OffsetCornerLatitudePoint2Element(FloatElement, FloatMISB):
  name = "offsetCornerLatitude2"
  names = {"offsetCornerLatitude2"}

  misb_name = "Offset Corner Latitude Point 2"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 08 01 00"
  misb_tag = 28
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLat (Tag 23)
  _invalid = bytes.fromhex('8000')

class OffsetCornerLatitudePoint3Element(FloatElement, FloatMISB):
  name = "offsetCornerLatitude3"
  names = {"offsetCornerLatitude3"}

  misb_name = "Offset Corner Latitude Point 3"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 09 01 00"
  misb_tag = 30
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLat (Tag 23)
  _invalid = bytes.fromhex('8000')

class OffsetCornerLatitudePoint4Element(FloatElement, FloatMISB):
  name = "offsetCornerLatitude4"
  names = {"offsetCornerLatitude4"}

  misb_name = "Offset Corner Latitude Point 4"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0A 01 00"
  misb_tag = 32
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLat (Tag 23)
  _invalid = bytes.fromhex('8000')

class OffsetCornerLongitudePoint1Element(FloatElement, FloatMISB):
  name = "offsetCornerLongitude"
  names = {"offsetCornerLongitude"}

  misb_name = "Offset Corner Longitude Point 1"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0B 01 00"
  misb_tag = 27
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLong (Tag 24)
  _invalid = bytes.fromhex('8000')

class OffsetCornerLongitudePoint2Element(FloatElement, FloatMISB):
  name = "offsetCornerLongitude2"
  names = {"offsetCornerLongitude2"}

  misb_name = "Offset Corner Longitude Point 2"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0C 01 00"
  misb_tag = 29
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLong (Tag 24)
  _invalid = bytes.fromhex('8000')

class OffsetCornerLongitudePoint3Element(FloatElement, FloatMISB):
  name = "offsetCornerLongitude3"
  names = {"offsetCornerLongitude3"}

  misb_name = "Offset Corner Longitude Point 3"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0D 01 00"
  misb_tag = 31
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLong (Tag 24)
  _invalid = bytes.fromhex('8000')

class OffsetCornerLongitudePoint4Element(FloatElement, FloatMISB):
  name = "offsetCornerLongitude4"
  names = {"offsetCornerLongitude4"}

  misb_name = "Offset Corner Longitude Point 4"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0E 01 00"
  misb_tag = 33
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-0.075, 0.075)
  # TODO
  # + FrameCenterLong (Tag 24)
  _invalid = bytes.fromhex('8000')

class IcingDetectedElement(StrElement, StrMISB):
  name = "icingDetected"
  names = {"icingDetected"}

  misb_name = "Icing Detected"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 0C 00 00 00"
  misb_tag = 34
  misb_units = "Icing Code"

  _code = {0 : "Detector off",
           1 : "No icing detected",
           2 : "Icing detected"}

  @classmethod
  def fromMISB(cls, value: bytes):
    return cls(cls._code[bytes_to_int(value)])

class WindDirectionElement(FloatElement, FloatMISB):
  name = "windDirection"
  names = {"windDirection"}

  misb_name = "Wind Direction"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 0D 00 00 00"
  misb_tag = 35
  misb_units = "Degrees"
  _domain = (0, 2**16 - 1)
  _range = (0, 360)

class WindSpeedElement(FloatElement, FloatMISB):
  name = "windSpeed"
  names = {"windSpeed"}

  misb_name = "Wind Speed"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 0E 00 00 00"
  misb_tag = 36
  misb_units = "Meters/Second"
  _domain = (0, 255)
  _range = (0, 100)

class StaticPressureElement(FloatElement, FloatMISB):
  name = "staticPressure"
  names = {"staticPressure"}

  misb_name = "Static Pressure"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 0F 00 00 00"
  misb_tag = 37
  misb_units = "Millibar"
  _domain = (0, 2**16 - 1)
  _range = (0, 5000)

class DensityAltitudeElement(FloatElement, FloatMISB):
  name = "densityAltitude"
  names = {"densityAltitude"}

  misb_name = "Density Altitude"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 10 00 00 00"
  misb_tag = 38
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (-900, 19000)

class OutsideAirTemperatureElement(IntElement, IntMISB):
  name = "outsideAirTemperature"
  names = {"outsideAirTemperature"}

  misb_name = "Outside Air Temperature"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 11 00 00 00"
  misb_tag = 39
  misb_units = "Celsius"
  _signed = True

class TargetLocationLatitudeElement(FloatElement, FloatMISB):
  name = "targetLocationLatitude"
  names = {"targetLocationLatitude"}

  misb_name = "Target Location Latitude"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 02 00 00 00"
  misb_tag = 40
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class TargetLocationLongitudeElement(FloatElement, FloatMISB):
  name = "targetLocationLongitude"
  names = {"targetLocationLongitude"}

  misb_name = "Target Location Longitude"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 03 00 00 00"
  misb_tag = 41
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class TargetLocationElevationElement(FloatElement, FloatMISB):
  name = "targetLocationElevation"
  names = {"targetLocationElevation"}

  misb_name = "Target Location Elevation"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 04 00 00 00"
  misb_tag = 42
  misb_units = "Meters"
  _domain = (0, 2**32 - 1)
  _range = (-900, 19000)

class TargetTrackGateWidthElement(IntElement, IntMISB):
  name = "targetTrackGateWidth"
  names = {"targetTrackGateWidth"}

  misb_name = "Target Track Gate Width"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 05 00 00 00"
  misb_tag = 43
  misb_units = "Pixels"

  @classmethod
  def fromMISB(cls, value: str):
    return cls(bytes_to_int(value) * 2)

class TargetTrackGateHeightElement(IntElement, IntMISB):
  name = "targetTrackGateHeight"
  names = {"targetTrackGateHeight"}

  misb_name = "Target Track Gate Height"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 06 00 00 00"
  misb_tag = 44
  misb_units = "Pixels"

  @classmethod
  def fromMISB(cls, value: str):
    return cls(bytes_to_int(value) * 2)

class TargetErrorEstimateCE90Element(FloatElement, FloatMISB):
  name = "targetErrorEstimateCE90"
  names = {"targetErrorEstimateCE90"}

  misb_name = "Target Error Estimate - CE90"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 07 00 00 00"
  misb_tag = 45
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (0, 4095)

class TargetErrorEstimateLE90Element(FloatElement, FloatMISB):
  name = "targetErrorEstimateLE90"
  names = {"targetErrorEstimateLE90"}

  misb_name = "Target Error Estimate - LE90"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 08 00 00 00"
  misb_tag = 46
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (0, 4095)

class GenericFlagDataElement(IntElement, IntMISB):
  name = "genericFlagData"
  names = {"genericFlagData"}

  misb_name = "Generic Flag Data"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 01 00 00 00"
  misb_tag = 47
  misb_units = "None"

class SecurityLocalSetElement(StrElement, MISB0601):
  name = "securityLocalSet"
  names = {"securityLocalSet"}

  misb_name = "Security Local Set"
  misb_key = "06 0E 2B 34 02 03 01 01 0E 01 03 03 02 00 00 00"
  misb_tag = 48
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class DifferentialPressureElement(FloatElement, FloatMISB):
  name = "differentialPressure"
  names = {"differentialPressure"}

  misb_name = "Differential Pressure"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 01 00 00 00"
  misb_tag = 49
  misb_units = "Millibar"
  _domain = (0, 2**16 - 1)
  _range = (0, 5000)

class PlatformAngleofAttackElement(FloatElement, FloatMISB):
  name = "platformAngleofAttack"
  names = {"platformAngleofAttack"}

  misb_name = "Platform Angle of Attack"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 02 00 00 00"
  misb_tag = 50
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-20, 20)
  _invalid = bytes.fromhex('8000')

class PlatformVerticalSpeedElement(FloatElement, FloatMISB):
  name = "platformVerticalSpeed"
  names = {"platformVerticalSpeed", "V.S"}

  misb_name = "Platform Vertical Speed"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 03 00 00 00"
  misb_tag = 51
  misb_units = "Meters/Second"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000')

class PlatformSideslipAngleElement(FloatElement, FloatMISB):
  name = "platformSideslipAngle"
  names = {"platformSideslipAngle"}

  misb_name = "Platform Sideslip Angle"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 04 00 00 00"
  misb_tag = 52
  misb_units = "Degrees"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-20, 20)
  _invalid = bytes.fromhex('8000')

class AirfieldBarometricPressureElement(FloatElement, FloatMISB):
  name = "airfieldBarometricPressure"
  names = {"airfieldBarometricPressure"}

  misb_name = "Airfield Barometric Pressure"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 02 00 00 00"
  misb_tag = 53
  misb_units = "Millibar"
  _domain = (0, 2**16 - 1)
  _range = (0, 5000)

class AirfieldElevationElement(FloatElement, FloatMISB):
  name = "airfieldElevation"
  names = {"airfieldElevation"}

  misb_name = "Airfield Elevation"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 03 00 00 00"
  misb_tag = 54
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (-900, 19000)

class RelativeHumidityElement(FloatElement, FloatMISB):
  name = "relativeHumidity"
  names = {"relativeHumidity"}

  misb_name = "Relative Humidity"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 09 00 00 00"
  misb_tag = 55
  misb_units = "Percent"
  _domain = (0, 2**8 - 1)
  _range = (0, 100)

class PlatformGroundSpeedElement(FloatElement, IntMISB):
  name = "platformGroundSpeed"
  names = {"platformGroundSpeed", "H.S"}

  misb_name = "Platform Ground Speed"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 05 00 00 00"
  misb_tag = 56
  misb_units = "Meters/Second"

class GroundRangeElement(FloatElement, FloatMISB):
  name = "groundRange"
  names = {"groundRange"}

  misb_name = "Ground Range"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 06 00 00 00"
  misb_tag = 57
  misb_units = "Meters"
  _domain = (0, 2**32 - 1)
  _range = (0, 5000000)

class PlatformFuelRemainingElement(FloatElement, FloatMISB):
  name = "platformFuelRemaining"
  names = {"platformFuelRemaining"}

  misb_name = "Platform Fuel Remaining"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 07 00 00 00"
  misb_tag = 58
  misb_units = "Kilograms"
  _domain = (0, 2**16 - 1)
  _range = (0, 10000)

class PlatformCallSignElement(StrElement, StrMISB):
  name = "platformCallSign"
  names = {"platformCallSign"}

  misb_name = "Platform Call Sign"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 01 01 00 00 00"
  misb_tag = 59
  misb_units = "None"

class WeaponLoadElement(IntElement, IntMISB):
  name = "weaponLoad"
  names = {"weaponLoad"}

  misb_name = "Weapon Load"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 12 00 00 00"
  misb_tag = 60
  misb_units = "None"

class WeaponFiredElement(IntElement, IntMISB):
  name = "weaponFired"
  names = {"weaponFired"}

  misb_name = "Weapon Fired"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 13 00 00 00"
  misb_tag = 61
  misb_units = "None"

class LaserPRFCodeElement(IntElement, IntMISB):

  name = "laserPRFCode"
  names = {"laserPRFCode"}

  misb_name = "Laser PRF Code"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 02 01 00 00 00"
  misb_tag = 62
  misb_units = "None"

class SensorFieldofViewNameElement(StrElement, StrMISB):
  name = "sensorFieldofViewName"
  names = {"sensorFieldofViewName"}

  misb_name = "Sensor Field of View Name"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 02 02 00 00 00"
  misb_tag = 63
  misb_units = "None"

  _code = {0 : "Ultranarrow",
           1 : "Narrow",
           2 : "Medium",
           3 : "Wide",
           4 : "Ultrawide",
           5 : "Narrow Medium",
           6 : "2x Ultranarrow",
           7 : "4x Ultranarrow"}

  @classmethod
  def fromMISB(cls, value: bytes):
    return cls(cls._code[bytes_to_int(value)])

class PlatformMagneticHeadingElement(FloatElement, FloatMISB):
  name = "platformMagneticHeading"
  names = {"platformMagneticHeading"}

  misb_name = "Platform Magnetic Heading"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 08 00 00 00"
  misb_tag = 64
  misb_units = "Degrees"
  _domain = (0, 2**16 - 1)
  _range = (0, 360)

class AlternatePlatformLatitudeElement(FloatElement, FloatMISB):
  name = "alternatePlatformLatitude"
  names = {"alternatePlatformLatitude"}

  misb_name = "Alternate Platform Latitude"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 14 00 00 00"
  misb_tag = 67
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class AlternatePlatformLongitudeElement(FloatElement, FloatMISB):
  name = "alternatePlatformLongitude"
  names = {"alternatePlatformLongitude"}

  misb_name = "Alternate Platform Longitude"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 15 00 00 00"
  misb_tag = 68
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class AlternatePlatformAltitudeElement(FloatElement, FloatMISB):
  name = "alternatePlatformAltitude"
  names = {"alternatePlatformAltitude"}

  misb_name = "Alternate Platform Altitude"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 16 00 00 00"
  misb_tag = 69
  misb_units = "Degrees"
  _domain = (0, 2**32 - 1)
  _range = (-900, 19000)
  _invalid = bytes.fromhex('8000 0000')

class AlternatePlatformNameElement(StrElement, StrMISB):
  name = "alternatePlatformName"
  names = {"alternatePlatformName"}

  misb_name = "Alternate Platform Name"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 17 00 00 00"
  misb_tag = 70
  misb_units = "None"

class AlternatePlatformHeadingElement(StrElement, FloatMISB):
  name = "alternatePlatformHeading"
  names = {"alternatePlatformHeading"}

  misb_name = "Alternate Platform Heading"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 18 00 00 00"
  misb_tag = 71
  misb_units = "Degrees"
  _domain = (0, 2**16 - 1)
  _range = (0, 360)

class EventStartTimeUTCElement(StrElement, IntMISB):
  name = "eventStartTimeUTC"
  names = {"evenStartTimeUTC"}

  misb_name = "Event Start Time - UTC"
  misb_key = "06 0E 2B 34 01 01 01 01 07 02 01 02 07 01 00 00"
  misb_tag = 72
  misb_units = "Microseconds"

class RVTLocalSetElement(StrElement, MISB0601):
  name = "RVTLocalSet"
  names = {"RVTLocalSet"}

  misb_name = "RVT Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 01 02 00 00 00"
  misb_tag = 73
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB ST 0806
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class VMTILocalSetElement(StrElement, MISB0601):
  name = "VMTILocalSet"
  names = {"VMTILocalSet"}

  misb_name = "VMTI Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 06 00 00 00"
  misb_tag = 74
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB ST 0903
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class AlternatePlatformEllipsoidHeightElement(FloatElement, FloatMISB):
  name = "alternatePlatformEllipsoidHeight"
  names = {"alternatePlatformEllipsoidHeight", "AlternatePlatformEllipsoidHeight", "alternateplatformellipsoidheight",
           "Alternate Platform Ellipsoid Height", "alternate platform ellipsoid height"}

  misb_name = "Allternate Platform Ellipsoid Height"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 01 82 48 00 00"
  misb_tag = 76
  misb_units = "Meters"
  _domain = (0, 2**16 - 1)
  _range = (-900, 19000)

class OperationalModeElement(StrElement, StrMISB):
  name = "operationalMode"
  names = {"operationalMode"}

  misb_name = "Operational Mode"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 03 21 00 00 00"
  misb_tag = 77
  misb_units = "Meters"
  _code = {0 : "Other",
           1 : "Operational",
           2 : "Training",
           3 : "Exercise",
           4 : "Maintenance",
           5 : "Test"}

  @classmethod
  def fromMISB(cls, value: bytes):
    return cls(cls._code[bytes_to_int(value)])

class SensorNorthVelocityElement(FloatElement, FloatMISB):
  name = "sensorNorthVelocity"
  names = {"sensorNorthVelocity"}

  misb_name = "Sensor North Velocity"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 02 7E 00 00 00"
  misb_tag = 79
  misb_units = "Meters/Second"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-327, 327)
  _invalid = bytes.fromhex('8000')

class SensorEastVelocityElement(FloatElement, FloatMISB):
  name = "sensorEastVelocity"
  names = {"sensorEastVelocity"}

  misb_name = "Sensor East Velocity"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 02 7F 00 00 00"
  misb_tag = 80
  misb_units = "Meters/Second"
  _domain = (-(2**15 - 1), 2**15 - 1)
  _range = (-327, 327)
  _invalid = bytes.fromhex('8000')

class ImageHorizonPixelPackElement(FloatElement, MISB0601):
  name = "imageHorizonPixelPack"
  names = {"imageHorizonPixelPack"}

  misb_name = "image Horizon Pixel Pack"
  misb_key = "06 0E 2B 34 02 05 01 01 0E 01 03 02 08 00 00 00"
  misb_tag = 81 
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: str):
    # Looks like the initialization for this is system dependent
    # Something fancy will need to be done if this ever gets implemented
    pass

class CornerLatitudePoint1Element(FloatElement, FloatMISB):
  name = "cornerLatitudePoint1"
  names = {"cornerLatitudePoint1"}

  misb_name = "Corner Latitude Point 1 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 07 01 00"
  misb_tag = 82
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class CornerLongitudePoint1Element(FloatElement, FloatMISB):
  name = "cornerLongitudePoint1"
  names = {"cornerLongitudePoint1"}

  misb_name = "Corner Longitude Point 1 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0B 01 00"
  misb_tag = 83
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class CornerLatitudePoint2Element(FloatElement, FloatMISB):
  name = "cornerLatitudePoint2"
  names = {"cornerLatitudePoint2"}

  misb_name = "Corner Latitude Point 2 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 08 01 00"
  misb_tag = 84
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class CornerLongitudePoint2Element(FloatElement, FloatMISB):
  name = "cornerLongitudePoint2"
  names = {"cornerLongitudePoint2"}

  misb_name = "Corner Longitude Point 2 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0C 01 00"
  misb_tag = 85
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class CornerLatitudePoint3Element(FloatElement, FloatMISB):
  name = "cornerLatitudePoint3"
  names = {"cornerLatitudePoint3"}

  misb_name = "Corner Latitude Point 3 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 09 01 00"
  misb_tag = 86
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class CornerLongitudePoint3Element(FloatElement, FloatMISB):
  name = "cornerLongitudePoint3"
  names = {"cornerLongitudePoint3"}

  misb_name = "Corner Longitude Point 3 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0D 01 00"
  misb_tag = 87
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class CornerLatitudePoint4Element(FloatElement, FloatMISB):
  name = "cornerLatitudePoint4"
  names = {"cornerLatitudePoint4"}

  misb_name = "Corner Latitude Point 4 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0A 01 00"
  misb_tag = 88
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-90, 90)
  _invalid = bytes.fromhex('8000 0000')

class CornerLongitudePoint4Element(FloatElement, FloatMISB):
  name = "cornerLongitudePoint4"
  names = {"cornerLongitudePoint4"}

  misb_name = "Corner Longitude Point 4 (Full)"
  misb_key = "06 0E 2B 34 01 01 01 03 07 01 02 01 03 0E 01 00"
  misb_tag = 89
  misb_units = "Degrees"
  _domain = (-(2**31 - 1), 2**31 - 1)
  _range = (-180, 180)
  _invalid = bytes.fromhex('8000 0000')

class PlatformAngleofAttackFullElement(FloatElement, FloatMISB):
  name = "PlatformAngleofAttackFull"
  names = {"PlatformAngleofAttackFull"}

  misb_name = "Platform Angle of Attack (Full)"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 02 00 00 00"
  misb_tag = 92
  misb_units = "Degrees"
  _range = (-90, 90)
  _domain = (-(2**31 - 1), 2**31 - 1)
  _invalid = bytes.fromhex('8000 0000')

class PlatformSideslipAngleFullElement(FloatElement, FloatMISB):
  name = "PlatformSideslipAngleFull"
  names = {"PlatformSideslipAngleFull"}

  misb_name = "Platform Sideslip Angle (Full)"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 04 00 00 00"
  misb_tag = 93
  misb_units = "Degrees"
  _range = (-180, 180)
  _domain = (-(2**31 - 1), 2**31 - 1)
  _invalid = bytes.fromhex('8000 0000')

class MIISCoreIdentifierElement(StrElement, MISB0601):
  name = "MIISCoreIdentifier"
  names = {"MIISCoreIdentifier"}

  misb_name = "MIIS Core Identifier"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 05 03 00 00 00"
  misb_tag = 94
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB ST 1204
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class SARMotionImageryLocalSetElement(StrElement, MISB0601):
  name = "SARMotionImageryLocalSet"
  names = {"SARMotionImageryLocalSet"}

  misb_name = "SAR Motion Imagery Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 0D 00 00 00"
  misb_tag = 95
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB 1206
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class RangeImageLocalSetElement(StrElement, MISB0601):
  name = "rangeImageLocalSet"
  names = {"rangeImageLocalSet"}

  misb_name = "Range Image Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 0C 00 00 00"
  misb_tag = 97
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB 1002
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class GeoRegistrationLocalSetElement(StrElement, MISB0601):
  name = "geoRegistrationLocalSet"
  names = {"geoRegistrationLocalSet"}

  misb_name = "Geo-Registration Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 01 00 00 00"
  misb_tag = 98
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB 1601
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class CompositeImagingLocalSetElement(StrElement, MISB0601):
  name = "compositeImagingLocalSet"
  names = {"compositeImagingLocalSet"}

  misb_name = "Composite Imaging Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 02 00 00 00"
  misb_tag = 99
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB 1602
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class SegmentLocalSetElement(StrElement, MISB0601):
  name = "segmentLocalSet"
  names = {"segmentLocalSet"}

  misb_name = "Segment Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 03 00 00 00"
  misb_tag = 100
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB 1607
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class AmendLocalSetElement(StrElement, MISB0601):
  name = "amendLocalSet"
  names = {"amendLocalSet"}

  misb_name = "Amend Local Set"
  misb_key = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 03 01 00 00"
  misb_tag = 101
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB 1607
    # This contains elements from a different standard so this will have
    # to have its own special procedures because it's a fancy boi
    pass

class SDCCFLPElement(StrElement, MISB0601):
  name = "SDCCFLP"
  names = {"SDCCFLP"}

  misb_name = "SDCC-FLP"
  misb_key = "06 0E 2B 34 02 05 01 01 0E 01 03 03 21 00 00 00"
  misb_tag = 102
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    # MISB 1010
    # This element is definied in the standard above
    pass

class DensityAltitudeExtendedElement(FloatElement, FloatMISB):
  name = "densityAltitudeExtended"
  names = {"densityAltitudeExtended"}

  misb_name = "Density Altitude Extended"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 10 00 00 00"
  misb_tag = 103
  misb_units = "Meters"
  _domain = "IMAPB"
  _range = (-900, 40000)

class AltPlatformEllipsoidHeightExtendedElement(FloatElement, FloatMISB):
  name = "alternatePlatformEllipsoidHeightExtended"
  names = {"alternatePlatformEllipsoidHeightExtended"}

  misb_name = "Alternate Platform Ellipsoid Height Extended"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 02 01 82 48 00 00"
  misb_tag = 105
  misb_units = "Meters"
  _domain = "IMAPB"
  _range = (-900, 40000)

class StreamDesignatorElement(StrElement, StrMISB):
  name = "streamDesignator"
  names = {"streamDesignator"}

  misb_name = "Stream Designator"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 03 03 00 00 00"
  misb_tag = 106
  misb_units = "None"

class OperationalBaseElement(StrElement, StrMISB):
  name = "operationalBase"
  names = {"operationalBase"}

  misb_name = "Operational Base"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 03 03 00 00 00"
  misb_tag = 107
  misb_units = "None"

class BroadcastSourceElement(StrElement, StrMISB):
  name = "broadcastSource"
  names = {"broadcastSource"}

  misb_name = "Broadcast Source"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 03 03 00 00 00"
  misb_tag = 108
  misb_units = "None"

class RangeToRecoveryElement(FloatElement, FloatMISB):
  name = "rangeToRecovery"
  names = {"rangeToRecovery"}

  misb_name = "Range To Recovery"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 30 00 00 00"
  misb_tag = 109
  misb_units = "Kilometers"
  _domain = "IMAPB"
  _range = (0, 21000)

class TimeAirborneElement(IntElement, IntMISB):
  name = "timeAirborne"
  names = {"timeAirborne"}

  misb_name = "Time Airborne"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 31 00 00 00"
  misb_tag = 110
  misb_units = "Seconds"

class PropulsionUnitSpeedElement(IntElement, IntMISB):
  name = "propulsionUnitSpeed"
  names = {"propulsionUnitSpeed"}

  misb_name = "Propulsion Unit Speed"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 32 00 00 00"
  misb_tag = 111
  misb_units = "Revolutions Per Minute"

class PlatformCourseAngleElement(FloatElement, FloatMISB):
  name = "platformCourseAngle"
  names = {"platformCourseAngle"}

  misb_name = "Platform Course Angle"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 33 00 00 00"
  misb_tag = 112
  misb_units = "Degrees"
  _domain = "IMAPB"
  _range = (0, 360)

class AltitudeAGLElement(FloatElement, FloatMISB):
  name = "altitudeAGL"
  names = {"altitudeAGL"}

  misb_name = "Altitude AGL"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 34 00 00 00"
  misb_tag = 113
  misb_units = "Meters"
  _domain = "IMAPB"
  _range = (-900, 40000)

class RadarAltimeterElement(FloatElement, FloatMISB):
  name = "radarAltimeter"
  names = {"radarAltimeter"}

  misb_name = "Radar Altimeter"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 35 00 00 00"
  misb_tag = 114
  misb_units = "Meters"
  _domain = "IMAPB"
  _range = (-900, 40000)

class ControlCommandElement(Element, MISB0601):
  name = "controlCommand"
  names = {"controlCommand"}

  misb_name = "Control Command"
  misb_key = "06 0E 2B 34 02 05 01 01 0E 01 03 01 01 00 00 00"
  misb_tag = 115
  misb_units = "None"

  def __init__(self, id: int, string: str, time: int):
    self.value = (id, string, time)

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    cmd_id = read_ber_oid(stream)
    str_len = read_len(stream)
    cmd_str = bytes_to_str(stream.read(str_len))
    cmd_time = bytes_to_int(stream.read(8))
    return cls(cmd_id, cmd_str, cmd_time)

class ControlCommandVerificationListElement(Element, MISB0601):
  name = "controlCommandVerificationList"
  names = {"controlCommandVerificationList"}

  misb_name = "Control Command Verification List"
  misb_key = "06 0E 2B 34 02 05 01 01 0E 01 03 02 11 00 00 00"
  misb_tag = 116
  misb_units = "None"

  def __init__(self, cmd_list: List[int]):
    self.value = cmd_list

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    cmd_list = []
    while stream.tell() != end:
      cmd_list.append(read_ber_oid(stream))
    return cls(cmd_list)

class SensorAzimuthRateElement(FloatElement, FloatMISB):
  name = "sensorAzimuthRate"
  names = {"sensorAzimuthRate"}

  misb_name = "Sensor Azimuth Rate"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 09 00 00"
  misb_tag = 117
  misb_units = "Degrees Per Second"
  _domain = "IMAPB"
  _range = (-1000, 1000)

class SensorElevationRateElement(FloatElement, FloatMISB):
  name = "sensorElevationRate"
  names = {"sensorElevationRate"}

  misb_name = "Sensor Elevation Rate"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 0A 00 00"
  misb_tag = 118
  misb_units = "Degrees Per Second"
  _domain = "IMAPB"
  _range = (-1000, 1000)

class SensorRollRateElement(FloatElement, FloatMISB):
  name = "sensorRollRate"
  names = {"sensorRollRate"}

  misb_name = "Sensor Roll Rate"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 0B 00 00"
  misb_tag = 119
  misb_units = "Degrees Per Second"
  _domain = "IMAPB"
  _range = (-1000, 1000)

class OnboardMIStoragePercentFullElement(FloatElement, FloatMISB):
  name = "onboardMIStoragePercentFull"
  names = {"onboardMIStoragePercentFull"}

  misb_name = "On-board MI Storage Percent Full"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 0C 00 00"
  misb_tag = 120
  misb_units = "Percentage"
  _domain = "IMAPB"
  _range = (0, 100)

class ActiveWavelengthListElement(Element, MISB0601):
  name = "activeWavelengthList"
  names = {"activeWavelengthList"}

  misb_name = "Active Wavelength List"
  misb_key = "06 0E 2B 34 02 05 01 01 0E 01 03 02 0A 00 00 00"
  misb_tag = 121
  misb_units = "None"
  _code = { 1 : "VIS",
            2 : "IR",
            3 : "NIR",
            4 : "MIR", 
            5 : "LIR",
            6 : "FIR"}

  def __init__(self, value: List[str]):
    self.value = value

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    cmd_list = []
    while stream.tell() != end:
      cmd_list.append(cls._code[read_ber_oid(stream)])
    return cls(cmd_list)

class CountryCodesElement(StrElement, MISB0601):
  name = "countryCodes"
  names = {"countryCodes"}

  misb_name = "Country Codes"
  misb_key = "06 0E 2B 34 02 04 01 01 0E 01 03 03 02 00 00 00"
  misb_tag = 122
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    length = read_len(stream)
    coding_method = bytes_to_int(stream.read(length))
    countries = str(coding_method) + " "
    while stream.tell() != end:
      length = read_len(stream)
      if length == 0:
        countries += "(Unknown Country) "
      else:
        countries += bytes_to_str(stream.read(length)) + ' '

    return cls(countries)

class NumNAVSATSinViewElement(IntElement, IntMISB):
  name = "numberOfNAVSATsInView"
  names = {"numberOfNAVSATsInView"}

  misb_name = "Number of NAVSATs in View"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 00 00 00"
  misb_tag = 123
  misb_units = "Count"

class PositioningMethodSourceElement(Element, IntMISB):
  name = "positioningMethodSource"
  names = {"positioningMethodSource"}

  misb_name = "Positioning Method Source"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 0E 00 00"
  misb_tag = 124
  misb_units = "None"
  _code = { 0 : "INS",
            1 : "GPS", 
            2 : "Galileo",
            3 : "QZSS",
            4 : "NAVIC",
            5 : "GLONASS",
            6 : "BeiDou-1",
            7 : "BeiDou-2"}

  def __init__(self, value: int):
    self.value = []
    for i in range(8):
      if value & (1 << i):
       self.value.append(self._code[i])

class PlatformStatusElement(Element, IntMISB):
  name = "platformStatus"
  names = {"platformStatus"}

  misb_name = "Platform Status"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 37 00 00 00"
  misb_tag = 125
  misb_units = "None"
  _code = { 0  : "Active",
            1  : "Pre-flight", 
            2  : "Pre-flight-taxiing",
            3  : "Run-up",
            4  : "Take-off",
            5  : "Ingress",
            6  : "Manual Operation",
            7  : "Automated-orbit",
            8  : "Transitioning",
            9  : "Egress",
            10 : "Landing",
            11 : "Landed-taxiing",
            12 : "Landed-Parked" }

  def __init__(self, value: int):
    self.value = self._code[value]

class SensorControlModeElement(Element, IntMISB):
  name = "sensorControlMode"
  names = {"sensorControlMode"}

  misb_name = "Sensor Control Mode"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 0F 00 00"
  misb_tag = 126
  misb_units = "None"
  _code = { 0  : "Off",
            1  : "Home Position", 
            2  : "Uncontrolled",
            3  : "Manual Control",
            4  : "Calibrating",
            5  : "Auto - Holding Position",
            6  : "Auto - Tracking"}

  def __init__(self, value: int):
    self.value = self._code[value]

class SensorFrameRatePackElement(FloatElement, MISB0601):
  name = "sensorFrameRatePack"
  names = {"sensorFrameRatePack"}

  misb_name = "Sensor Frame Rate Pack"
  misb_key = "06 0E 2B 34 02 05 01 01 0E 01 03 02 10 00 00 00"
  misb_tag = 127
  misb_units = "None"

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    num = read_ber_oid(stream)
    if stream.tell() != end:
      den = read_ber_oid(stream)
    else:
      den = 1
    return cls(num/den)

class WavelengthsListElement(Element, MISB0601):
  name = "wavelengthsList"
  names = {"wavelengthsList"}

  misb_name = "Wavelengths List"
  misb_key = "06 0E 2B 34 02 04 01 01 0E 01 03 02 01 00 00 00"
  misb_tag = 128
  misb_units = "None"
  _code = { 1 : "VIS",
            2 : "IR",
            3 : "NIR",
            4 : "MIR", 
            5 : "LIR",
            6 : "FIR"}

  def __init__(self, value: List[str]):
    self.value = value

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    records = []
    while stream.tell() != end:
      record = ""
      length = read_len(stream)
      ber_start = stream.tell()
      record += str(read_ber_oid(stream))
      ber_len = stream.tell() - ber_start
      min_val = bytes_to_float(stream.read(4), (0, 2**(8*4)-1), (0, 1e9))
      max_val = bytes_to_float(stream.read(4), (0, 2**(8*4)-1), (0, 1e9))
      name = bytes_to_str(stream.read(length - (ber_len + 8)))
      record += ", " + str(min_val) + ", " + str(max_val) + ", " + name
      records.append(record)

    return cls(record)

class TargetIDElement(StrElement, StrMISB):
  name = "targetID"
  names = {"targetID"}

  misb_name = "Target ID"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 03 03 00 00 00"
  misb_tag = 129
  misb_units = "None"

class AirbaseLocationsElement(Element, MISB0601):
  name = "airbaseLocations"
  names = {"airbaseLocations"}

  misb_name = "Airbase Locations"
  misb_key = "06 0E 2B 34 02 04 01 01 0E 01 03 01 01 00 00 00"
  misb_tag = 130
  misb_units = "None"

  def __init__(self, value: List[str]):
    self.value = value

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    locations = []
    while stream.tell() != end:
      location = ""
      length = read_len(stream)
      if length == 0:
        location = "Unknown"
      else:
        lat = bytes_to_float(stream.read(4), (0, 2**(8*4)-1), (-90, 90))
        lon = bytes_to_float(stream.read(4), (0, 2**(8*4)-1), (-180, 180))
        hae = bytes_to_float(stream.read(3), (0, 2**(8*3)-1), (-900, 9000))
        location = str(lat) + ', ' + str(lon) + ', ' + str(hae)

      locations.append(location)

    if len(locations) < 2:
      locations.append(locations[0])

    return cls(locations)

class TakeoffTimeElement(IntElement, IntMISB):
  name = "takeoffTime"
  names = {"takeoffTime"}

  misb_name = "Take-off Time"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 01 38 00 00 00"
  misb_tag = 131
  misb_units = "Microseconds"

class TransmissionFrequencyElement(FloatElement, FloatMISB):
  name = "transmissionFrequency"
  names = {"transmissionFrequency"}

  misb_name = "Transmission Frequency"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 13 00 00"
  misb_tag = 132
  misb_units = "MHz"
  _domain = "IMAPB"
  _range = (1, 99999)

class OnboardMIStorageCapacityElement(IntElement, IntMISB):
  name = "onboardMIStorageCapacity"
  names = {"onboardMIStorageCapacity"}

  misb_name = "On-board MI Storage Capacity"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 14 00 00"
  misb_tag = 133
  misb_units = "Gigabytes"

class ZoomPercentageElement(FloatElement, FloatMISB):
  name = "zoomPercentage"
  names = {"zoomPercentage"}

  misb_name = "Zoom Percentage"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 15 00 00"
  misb_tag = 134
  misb_units = "Percent"
  _domain = "IMAPB"
  _range = (0, 100)

class CommunicationsMethodElement(StrElement, StrMISB):
  name = "communicationsMethod"
  names = {"communicationsMethod"}

  misb_name = "Communications Method"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 04 03 03 00 00 00"
  misb_tag = 135
  misb_units = "None"

class LeapSecondsElement(IntElement, IntMISB):
  name = "leapSeconds"
  names = {"leapSeconds"}

  misb_name = "Leap Seconds"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 00 00 00"
  misb_tag = 136
  misb_units = "Seconds"
  _signed = True

class CorrectionOffsetElement(IntElement, IntMISB):
  name = "correctionOffset"
  names = {"correctionOffset"}

  misb_name = "Correction Offset"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 17 00 00"
  misb_tag = 137
  misb_units = "Microseconds"
  _signed = True

class PayloadListElement(Element, MISB0601):
  name = "payloadList"
  names = {"payloadList"}

  misb_name = "Payload List"
  misb_key = "06 0E 2B 34 02 04 01 01 0E 01 03 02 00 00 00 00"
  misb_tag = 138
  misb_units = "None"
  _code = { 0 : "Electro Optical MI Sensor",
            1 : "LIDAR",
            2 : "RADAR",
            3 : "SIGINT", 
            4 : "SAR"}

  def __init__(self, value: List[str]):
    self.value = value

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    payloads = []
    payloads.append(read_ber_oid(stream))
    while stream.tell() != end:
      length = read_len(stream)
      pid  = str(read_ber_oid(stream))
      ptype = cls._code[read_ber_oid(stream)]
      name_len = read_len(stream)
      name = bytes_to_str(stream.read(name_len))
      record = pid + ', ' + ptype + ', ' + name
      payloads.append(record)

    return cls(payloads)

class ActivePayloadsElement(Element, MISB0601):
  name = "activePayloads"
  names = {"activePayloads"}

  misb_name = "Active Payloads"
  misb_key = "06 0E 2B 34 01 01 01 01 0E 01 01 02 0A 1A 00 00"
  misb_tag = 139
  misb_units = "None"

  def __init__(self, value: List[int]):
    self.value = value

  @classmethod
  def fromMISB(cls, value: bytes):
    val = bytes_to_int(value)
    active = []
    for i in range(len(value)):
      if val & (1 << i):
       active.append(i)
    return cls(active)

class WeaponsStoresElement(Element, MISB0601):
  name = "weaponsStores"
  names = {"weaponsStores"}

  misb_name = "Weapons Stores"
  misb_key = "06 0E 2B 34 02 04 01 01 0E 01 03 01 03 00 00 00"
  misb_tag = 140
  misb_units = "None"
  _code = { 0  : "Off",
            1  : "Initialization",
            2  : "Ready/Degraded",
            3  : "Ready/All Up Round",
            4  : "Launch",
            5  : "Free Flight",
            6  : "Abort",
            7  : "Miss Fire",
            8  : "Hang Fire",
            9  : "Jettisoned",
            10 : "Stepped Over",
            11 : "No Status Available"}
  _code_1 = { 1 : "Fuze Enabled",
             2 : "Laser Enabled",
             3 : "Target Enabled",
             4 : "Weapon Armed"}

  def __init__(self, value: List[int]):
    self.value = value

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    weapons = []
    while stream.tell() != end:
      length = read_len(stream)
      station = read_ber_oid(stream)
      hardpoint = read_ber_oid(stream)
      carriage = read_ber_oid(stream)
      store = read_ber_oid(stream)
      state = str(station) + ', ' + str(hardpoint) + ', ' + str(carriage) + ', ' + str(store) + ', '
      status = read_ber_oid(stream)
      general = cls._code[ 127 & status ]
      state += general + ', '
      if status >> 8:
        engagement = cls._code_1[status>>8]
        state += engagement + ', '
      
      type_len = read_len(stream)
      state += stream.read(type_len)

      weapons.append(state)

    return cls(state)

class WaypointListElement(Element, MISB0601):
  name = "waypointList"
  names = {"waypointList"}

  misb_name = "Waypoint List"
  misb_key = "06 0E 2B 34 02 04 01 01 0E 01 03 01 04 00 00 00"
  misb_tag = 141
  misb_units = "None"
  _code = { 0 : "Automated",
            1 : "Manual"}
  _code_1 = { 0 : "Pre-planned",
              1 : "Ad-hoc"}

  def __init__(self, value: List[int]):
    self.value = value

  @classmethod
  def fromMISB(cls, value: bytes):
    stream = BytesIO(value)
    end = read_len(stream) + stream.tell()
    waypoints = []
    while stream.tell() != end:
      length = read_len(stream)
      wp_id = read_ber_oid(stream)
      order = bytes_to_int(stream.read(2), True)
      info = read_ber_oid(stream)
      mode = cls._code[info & 1]
      source = cls._code[info & 2]

      lat = bytes_to_float(stream.read(4), (0, 2**(8*4)-1), (-90, 90))
      lon = bytes_to_float(stream.read(4), (0, 2**(8*4)-1), (-180, 180))
      hae = bytes_to_float(stream.read(3), (0, 2**(8*3)-1), (-900, 9000))
      location = str(lat) + ', ' + str(lon) + ', ' + str(hae)

      waypoint = str(wp_id) + ', ' + str(order) + ', ' + mode + ', ' + source + ', ' + location
      waypoints.append(waypoint)

    return cls(waypoints)

class ApertureElement(FloatElement):
  name = "aperture"
  names = {"aperture", "Aperture", "f", "F", "fnum", "Fnum"}

  def __init__(self, value: float):
    super().__init__(value)
    try:
      if self.value >= 100:
        self.value /= 100
    except Exception:
      # If init failed to convert to float, just leave as is
      pass

class ShutterSpeedElement(StrElement):
  # Even though this is a number it is often represented as "1/###".
  # There's no real way to know whether a given value without "1/" should actually have that or not
  name = "shutterSpeed"
  names = {"shutterSpeed", "ShutterSpeed", "shutter", "Shutter", "ss", "SS"}

class ISOElement(IntElement):
  name = "ISO"
  names = {"ISO", "iso"}

class EVElement(FloatElement):
  name = "EV"
  names = {"ev", "EV", "exposurevalue", "ExposureValue", "exposure value", "Exposure Value"}

class ColorTemperature(IntElement):
  name = "colorTemperature"
  names = {"colorTemperature", "ColorTemperture", "ct", "CT"}

class FocalLengthElement(IntElement):
  name = "focalLength"
  names = {"focalLength", "FocalLength", "focal_len"}

class ColorProfileElement(StrElement):
  name = "colorProfile"
  names = {"colorProfile", "color_md"}

class HomeLatitudeElement(FloatElement):
  name = "homeLatitude"
  names = {"homeLatitude"}

class HomeLongitudeElement(FloatElement):
  name = "homeLongitude"
  names = {"homeLongitude"}

class HomeAltitudeElement(FloatElement):
  name = "homeAltitude"
  names = {"homeAltitude"}

class DistanceFromHomeElement(FloatElement):
  name = "distanceFromHome"
  names = {"distanceFromHome", "D"}

class HeightAboveHomeElement(FloatElement):
  name = "heightAboveHome"
  names = {"heightAboveHome", "H"}

class IsTakingVideoElement(IntElement):
  name = "isTakingVideo"
  names = {"isTakingVideo", "isVideo"}
