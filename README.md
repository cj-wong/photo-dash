# photo-dash

![Example deployment][.header]


## Overview

The `photo-dash` project is a series of modules and an endpoint. This repository specifically is the endpoint which sends images to a dumb digital photo frame.

Each module should be named like so: `photo-dash-module`. Each module should send a put request to the REST API to create or update images. The data format for these images is documented [here](docs/DATA.md).

Although this project focuses on a specific, generic frame ([Leed's] 1690-32BK), it may be possible to adapt the configurations for other dumb digital photo frames. This photo frame in particular has a SD card slot and a USB A input. Both serve only as storage inputs; the frame cannot interact directly with a computer. More specifications are below; use them to adapt other frames for the project.

Similarly, this project focuses on a SBC ([Raspberry Pi Zero W][RPIZ]) to serve as the endpoint. It will connect to the photo frame via USB A (using its `USB` micro USB out plug) and act as a mass storage device. This [guide][USBGUIDE] from [the Raspberry Pi Foundation][RPI] is very helpful for setting up a USB (OTG) gadget to simulate a flash drive. **Although not required, I recommend using this setup for the project.** I also recommend creating a data-only cable (details in the guide), as it means the SBC can be run independently of the photo frame.

## 1690-32BK Specifications

### Images

- Resolution: 480x234
- PNG is not supported *(tested: transparent PNG, JPG)*.
- Images that show are centered on both axes.
- Images smaller than the given resolution aren't scaled, so they are letterboxed on both axes if applicable.
- Images slightly larger than the given resolution *(tested: 1000x1000)* will be scaled down and fitted in full, regardless of aspect ratio. For example, given the 1000x1000 image (aspect ratio 1:1), its resulting image will appear as 480x234 (aspect ratio 80:39 or approximately 2:1).
- Images much larger than the given resolution *(tested: 12000x1000)* will be ignored and not shown. This may also be restricted by image size. Regardless, large images cannot work.

Fixes:

- Images must be JPG. If your frame supports other extensions, feel free to change this in `photo_dash.image.DashImg.create`; the line is `self.dest = config.DEST / f'{self.module}.jpg'`.
- Images output from `photo_dash.image.DashImg` will be constrained to the resolution above (480x234).
- The visible area is a little reduced from its expected image resolution, probably due to the underlying display being partially obscured. To compensate for these cut borders, `photo_dash.image.DashImg` has two attributes that change offset from the outer edge: `H_SPACER` (horizontal) and `V_SPACER` (vertical).

### Functionality

- On boot, if no images are loaded, the photo frame will display a kind of boot screen. After at least one image has been shown, the boot screen will never show until rebooted.
- A slideshow option is available by default. This is required for full functionality, even if not using the exact photo frame.
- Directories are supported. However, `photo_dash.image.DashImg` will not use these unless specified as the destination. Empty directories are skipped.
- FAT32 (for the USB gadget) is well supported, but other file systems have not been tested.
- Images stay in memory on the photo frame. As a result, the endpoint's USB gadget encounters an issue, the images on the photo frame may not be up-to-date. Because of this limitation, you cannot visually debug problems with the endpoint if images are shown.
- During `sync`s (especially if the recommended watchdog from the [guide][USBGUIDE] is installed), the photo frame may display no images or the settings/overview screen. This transition should only last a couple seconds.

Fixes:

- If you are using the guide, in order for the endpoint to properly work after a reboot, I recommend adding the `modprobe` command (without `modprobe`) from the guide into a separate file under `/etc/modules-load.d`. Otherwise, you may have to manually update the kernel module (`g_mass_storage`).
- The USB gadget must be FAT32 to avoid any unforeseen problems. The guide mounts the simulated storage as FAT32.
- Because FAT32 storage does not support sym-linking, files must be copied over or directly written to storage. Specify the output directory in the configuration.
- The output directory in the configuration should point to the root of the mounted volume. If you have followed the guide linked above, this should be `/mnt/usb_share`. Although directories are supported, their behavior has not been tested (specifically, display order).

## Image Caveats

- When creating gauges, some numbers may be omitted if they cannot be rendered. 

## Usage

1. Setup [config.json](config.json.example) by copying the example file and renaming it. `"width"` and `"length"` must be integers. `"destination"` must be a string that can be parsed as a path using `pathlib.Path`. (Both relative and absolute paths can work here.)
2. Run `python photo_dash/app.py`, preferably with `gunicorn` (provided in [requirements.txt](requirements.txt)). The endpoint does not do anything on its own; use modules to send data to convert to a `photo-dash` image.
3. (Optional) Run `python utils_runner.py` for extra utilities. Currently, this includes creating an image with text that describes quiet hours when in effect.

## Requirements

This code is designed around the following:

- Python 3.7+
    - `flask` and `flask-restful` for creating an API endpoint
    - `gunicorn` to run the endpoint
    - `pendulum` to determine when an image is created from data
    - `pillow` for creating dash images
    - other [requirements](requirements.txt)

## Setup

Make sure to fill in all the fields in [config.json](config.json.example).

- `"width"`: integer; width of the digital photo frame display, in pixels
- `"length"`: integer; length of the digital photo frame display, in pixels
- `"destination"`: string; must be a valid path (relative or absolute) that can be parsed by `pathlib.Path`

Optional configuration:

- `"quiet_start"`: integer; when quiet hours should start; requests (except for `GET` `QuietHours`) will not be fulfilled during this time
- `"quiet_end"`: integer; when quiet hours should end; requests will resume

⚠ If you intend to use quiet hours, both quiet hours fields must be defined and not also be the same as each other. You cannot define only one field.

## Disclaimer

This project is not affiliated with or endorsed by [Leed's] or [the Raspberry Pi Foundation][RPI]. See [LICENSE](LICENSE) for more detail.

[Leed's]: https://www.pcna.com/leeds/en-us
[RPI]: https://www.raspberrypi.org/
[RPIZ]: https://www.raspberrypi.org/products/raspberry-pi-zero-w/
[USBGUIDE]: https://magpi.raspberrypi.org/articles/pi-zero-w-smart-usb-flash-drive
[.header]: resources/irl.jpg?raw=true
