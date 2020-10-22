# photo-dash

## Overview

The `photo-dash` project is a series of modules and an endpoint. The endpoint sends images to a dumb digital photo frame.

Each module should be named like so: `photo-dash-module`. Each module should send a put request to the REST API to create or update images. The data format for these images is documented [here](docs/DATA.md).

Although this project focuses on a specific, generic frame ([Leed's] 1690-32BK), it may be possible to adapt the configurations for other dumb digital photo frames. This photo frame in particular has a SD card slot and a USB A input. Both serve only as storage inputs; the frame cannot interact directly with a computer. More specifications are below.

Similarly, this project focuses on a SBC ([Raspberry Pi Zero W][RPI]) to serve as the endpoint. It will connect to the photo frame via USB A and act as a mass storage device. [This][USBGUIDE] guide is very helpful for setting up the USB gadget for mounting. Although not required, I recommend using this setup for the project. I also recommend creating a data-only cable, as it means the SBC can be run independently of the photo frame.

## 1690-32BK Specifications

- **Resolution:** 480x234
- Does not appear to support PNG *(tested: transparent PNG, JPG)*.
- Images slightly larger than the given resolution *(tested: 1000x1000)* will be scaled down and possibly stretched along one axis if not the same aspect ratio.
- Images much larger than the given resolution *(tested: 12000x1000)* will be ignored. This may also be restricted by image size.

## Usage

TODO

## Requirements

This code is designed around the following:

- Python 3.7+
    - TODO
    - other [requirements](requirements.txt)

## Setup

1. TODO

## Disclaimer

This project is not affiliated with or endorsed by [Leed's] or [the Raspberry Pi Foundation][RPI]. See [LICENSE](LICENSE) for more detail.

[Leed's]: https://www.pcna.com/leeds/en-us
[RPI]: https://www.raspberrypi.org/
[USBGUIDE]: https://magpi.raspberrypi.org/articles/pi-zero-w-smart-usb-flash-drive
