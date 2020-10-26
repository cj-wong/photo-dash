# photo-dash

![Example deployment][.header]


## Overview

The `photo-dash` project is a series of modules and an endpoint. The endpoint sends images to a dumb digital photo frame.

Each module should be named like so: `photo-dash-module`. Each module should send a put request to the REST API to create or update images. The data format for these images is documented [here](docs/DATA.md).

Although this project focuses on a specific, generic frame ([Leed's] 1690-32BK), it may be possible to adapt the configurations for other dumb digital photo frames. This photo frame in particular has a SD card slot and a USB A input. Both serve only as storage inputs; the frame cannot interact directly with a computer. More specifications are below.

Similarly, this project focuses on a SBC ([Raspberry Pi Zero W][RPI]) to serve as the endpoint. It will connect to the photo frame via USB A and act as a mass storage device. [This][USBGUIDE] guide is very helpful for setting up the USB gadget for mounting. Although not required, I recommend using this setup for the project. I also recommend creating a data-only cable, as it means the SBC can be run independently of the photo frame.

## 1690-32BK Specifications

- **Resolution:** 480x234
- Does not appear to support PNG *(tested: transparent PNG, JPG)*.
- Images smaller than the given resolution are centered on both axes.
- Images slightly larger than the given resolution *(tested: 1000x1000)* will be scaled down and possibly stretched along one axis if not the same aspect ratio.
- Images much larger than the given resolution *(tested: 12000x1000)* will be ignored. This may also be restricted by image size.
- A slideshow option is available by default. This is required for full functionality, even if not using the exact photo frame.
- Directories seem to be supported. As FAT32 systems do not support sym-linking, files must be copied over. Specify the output directory in the configuration.
- Images appear to stay in memory on the photo frame, especially during syncs. If a problem occurs with the gadget, the photo frame will not remove the old images. This may be important for debugging.

## Usage

1. Setup [config.json](config.json.example) by copying the example file and renaming it. `"width"` and `"length"` must be integers. `"destination"` must be a string that can be parsed as a path using `pathlib.Path`. (Both relative and absolute paths can work here.)
2. Run `python photo_dash/app.py`. The endpoint does not do anything on its own; use modules to send data to convert to a `photo-dash` image.

## Requirements

This code is designed around the following:

- Python 3.7+
    - `flask` and `flask-restful` for creating an API endpoint
    - `gunicorn` to run the API
    - `pendulum` to determine when an image is created from data
    - `pillow` for creating dash images
    - other [requirements](requirements.txt)

## Setup

Make sure to fill in all the fields in [config.json](config.json.example).

- `"width"`: integer; width of the digital photo frame display, in pixels
- `"length"`: integer; length of the digital photo frame display, in pixels
- `"destination"`: string; must be a valid path (relative or absolute) that can be parsed by `pathlib.Path`

## Disclaimer

This project is not affiliated with or endorsed by [Leed's] or [the Raspberry Pi Foundation][RPI]. See [LICENSE](LICENSE) for more detail.

[Leed's]: https://www.pcna.com/leeds/en-us
[RPI]: https://www.raspberrypi.org/
[USBGUIDE]: https://magpi.raspberrypi.org/articles/pi-zero-w-smart-usb-flash-drive
[.header]: resources/irl.jpg?raw=true
