from .parser import Parser
import os
import json
import logging
import subprocess
from typing import Dict, Tuple, Union, List
JSONType = Dict[str, Union[List[Dict[str, Union[str, int]]], Dict[str,Union[str, int]]]]
logger = logging.getLogger("OTK.detector")

def split_path(src: str) -> Tuple[str, str, str]:
  path, filename = os.path.split(src)

  if filename:
    name, ext = os.path.splitext(filename)
    return (path, name, ext.lower())

  return (path, "", "")

def read_video_metadata(src: str) -> JSONType:
  data_raw = os.popen("ffprobe -v quiet -print_format json -show_format -show_streams " + src).read()
  return json.loads(data_raw)

def read_video_metadata_file(src: str):
  with open(src, 'r') as fl:
    metadata = json.load(fl)
  return metadata

def get_embedded_telemetry_type(metadata: JSONType) -> str:
  if "streams" in metadata:
    for stream in metadata["streams"]:
      if stream["codec_type"] == "subtitle":
        if stream["codec_tag_string"] == "text":
          return "srt"
        elif stream["codec_tag_string"] == "tx3g":
          return "ass"
      elif stream["codec_type"] == "data":
        if "codec_tag_string" in stream and stream["codec_tag_string"] == "KLVA":
          return "klv"
        elif "codec_tag_string" in stream and stream["codec_tag_string"] == "gpmd":
          return "gopro"
        elif "tags" in stream and "handler_name" in stream["tags"]:
          if stream["tags"]["handler_name"] == "ParrotVideoMetadata":
            return "parrot"
      elif stream["codec_type"] == "video":
        if "tags" in stream and "handler_name" in stream["tags"] and \
           stream["tags"]["handler_name"] == "PittaSoft Video Media Handler":
            return "blackvue"

  logger.error("Unsupported embedded telemetry type.")
  return None

# If supported return the extension and bool
#   False: Telemetry is not embedded in video file (in it's own file)
#   True: Telemetry is embedded in video file
# TODO: Rewrite so we're not doing the same search twice.
# Not a huge deal now, but as more types get supported will get worse
def get_telemetry_type(src: str) -> Tuple[str, bool]:
  _, _, ext = split_path(src)
  supported = [cls.tel_type for cls in Parser.__subclasses__()]
  if ext.strip('.') in supported:
    logger.info("Found independent telemetry of type '{}'".format(ext.strip('.')))
    return (ext.strip('.'), False)

  metadata = read_video_metadata(src)
  if metadata:
    tel_type = get_embedded_telemetry_type(metadata)

    if tel_type:
      logger.info("Found embedded telemetry of type '{}'".format(tel_type))
      return (tel_type, True)
  
  logger.error("{} contains an unsupported telemetry type".format(src))
  return (None, False)
    
def create_telemetry_parser(src: str) -> Parser:
  tel_type, embedded = get_telemetry_type(src)

  for cls in Parser.__subclasses__():
    if tel_type == cls.tel_type:
      logger.info("Creating parser objecet: {}".format(cls.__name__))
      if not embedded:
        return cls(src)
      else:
        return cls(src, is_embedded=embedded)

def read_embedded_subtitles(src: str, file_format: str) -> str:
  cmd = "ffmpeg -y -i " + src + " -f " + file_format + " - " 
  subtitles = os.popen(cmd).read()
  return subtitles

def read_klv(src: str, metadata: JSONType) -> bytes:
  klv_idx = None
  if "streams" in metadata:
      for idx, stream in enumerate(metadata["streams"]):
        if stream["codec_type"] == "data" and stream["codec_tag_string"] == "KLVA":
          klv_idx = str(idx)
          break

  cmd = ["ffmpeg", "-loglevel", "quiet", "-i" , src , "-map", "0:" + klv_idx, "-codec", "copy", "-f", "data", "-"]
  klv = subprocess.run(cmd, stdout=subprocess.PIPE).stdout
  return klv