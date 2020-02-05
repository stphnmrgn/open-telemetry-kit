# Open Telemetry Kit

![Image of Open Telemetry Kit](https://raw.githubusercontent.com/Hivemapper/open-telemetry-kit/master/OTK.jpg)

The Open Telemetry Kit (OTK) is an open source package for extracting and parsing telemetry associated with video streams and converting to common formats.
It comes out of a need for a singular API that can be used for multiple different video telemetry formats.

Telemetry that can be parsed includes: GPS, time, camera information, speed

Features:
- Automatically detect telemetry format
- Manipulate telemetry with ease
- Write telemetry to a new format

## Getting Started
### Dependencies
Python version: `>=3.6`

`ffmpeg` and `ffprobe`.

On Debian systems these can be installed with:
>$ sudo apt install ffmpeg

`dateutil`

On Debian systems this can be installed with:
>$ pip3 install python-dateutil

### Installation
>$ pip3 install open-telemetry-kit

### Importing
The OTK package can be imported into your python3 project with:
>import open_telemetry_kit as otk

### Quick Start

#### Download the OTK Quickstart package with sample data

Download the OTK quickstart package (~90 MB).
(Mac users can install `wget` using [these instructions](https://www.maketecheasier.com/install-wget-mac/))

>$ wget https://hivemapper-sample-videos.s3-us-west-2.amazonaws.com/OTK/OTK_quickstart.tgz

This includes a sample `.csv`, `.srt`, and `.mov` with embedded telemetry.
It also contains `quickstart.py` which you can use to extract the telemetry from the sample files.

Extract the package:

>$ tar xzvf OTK_quickstart.tgz

This will extract everything into a new directory called `OTK_quickstart/`

The `quickstart.py` script accepts a standalone `.csv` or `.srt` or a video file with an embedded `.srt`. 
It will read in the data, convert it to JSON, and write it to the provided destination. 

#### Telemetry extraction and conversion example

In your terminal go to the new `OTK_quickstart` directory.

Extract telemetry from the sample video:

>$ python3 quickstart.py embedded_srt_example.mov embedded_srt_example.json

Extract telemetry from the sample `srt` or `csv` files respectively:

>$ python3 quickstart.py srt_example.srt srt_example.json

>$ python3 quickstart.py csv_example.csv csv_example.json


_Note: This process will create a new JSON file containing the telemetry extracted from the sample file.
The data is organized into an array of objects (or, in python terminology, a list of dictionaries)_


#### Data manipulation example

For an example of simple data manipulation, open `quickstart.py` and uncomment the lines:

```
# gps = Telemetry()
# for packet in telemetry:
#   gps.append({ k:v for k, v in packet.items() if k in ['latitude', 'longitude', 'altitude']})

# write.telemetryToJson(gps, dest)
```

Rerun the script with one of the provided commands above.

### Current Functionality
#### Input Formats
The OTK currently supports the following forms of telemetry:
- `.csv` files
- `.srt` files
- Most videos file with embedded telemetry encoded as a `.srt` (e.g. video taken with some DJI drone models)
- `.gpx` files
- `.kml` files
- KLV/MISB embedded data
- Open Camera `.srt`

#### Output Formats
- JSON
- CSV

### Future Releases
Planned expansions and updates for the OTK include:

#### Input Formats

#### Output Formats
- geoJSON

#### Other
- Unit Tests
