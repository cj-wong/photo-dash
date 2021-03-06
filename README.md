# photo-dash

![Example deployment][.header]

##### *[photo-dash-sds011](https://github.com/cj-wong/photo-dash-sds011), live*


## Overview

The `photo-dash` project is a series of modules and an endpoint. This repository specifically is the endpoint which sends images to a dumb digital photo frame.

Each module should be named like so: `photo-dash-module`. Each module should send a put request to the REST API to create or update images. The data format for these images is documented [here](docs/DATA.md).

Although this project focuses on a specific, generic frame ([Leed's] 1690-32BK), it may be possible to adapt the configurations for other dumb digital photo frames. This photo frame in particular has a full SD card slot and a USB A input slot. Both serve only as storage inputs; the frame can't directly interact or be modified with a computer. Other specifications to this frame are below; use them to adapt other frames for the project as necessary.

Similarly, this project focuses on a SBC ([Raspberry Pi Zero W][RPIZ]) to serve as the endpoint. It will connect to the photo frame via USB A (using its `USB` receptacle, not its `PWR` receptacle) and act as a mass storage device. This [guide][USBGUIDE] from [the Raspberry Pi Foundation][RPI] is very helpful for setting up a USB (OTG) gadget to simulate a flash drive.

### Recommendations

- **Although not required, I recommend following the guide and using the above setup for the project.**
- I recommend creating a data-only cable (detailed in the guide), as it means the SBC can be run independently of the photo frame.
- Because this project is a net-accessible endpoint that automatically generates images, you do not need to follow step 11 (Samba setup) in the guide.
- Regarding kernel updates (if applicable), e.g. through `apt upgrade`, make sure to restart the device after upgrading to reload the module, or **the endpoint won't work**.

## 1690-32BK specifications

### Images

- Image resolution: 480 x 234
- PNG is not supported. *(Test image formats: transparent PNG, JPG)*
- Images that can render successfully are centered on both axes.
- Images smaller than the given resolution on at least one axis aren't scaled, so they are letterboxed the axes longer than the image.
- Images slightly larger than the given resolution will be scaled down and fitted in full, regardless of aspect ratio. For example, given the 1000 x 1000 image (aspect ratio 1:1), its resulting image will appear as 480 x 234 (aspect ratio 80:39 or approximately 2:1). *(Test image resolution: 1000 x 1000)*
- Images much larger than the given resolution will be ignored and not shown. It is unclear whether image resolution or file size (or both) are responsible for this mechanism. Regardless, large images cannot work. *(Test image resolution: 12000 x 1000)*

### Functionality

- On boot, if no images are loaded, the photo frame will display a kind of boot screen. After at least one image has been shown (or the buttons have been pressed), the boot screen will never show until rebooted.
- A slideshow option is available by default. Slideshow order seems to be similar or identical to that of file order in Linux. ***This may need some investigation.***
- Directories are supported. However, `photo_dash.image.DashImg` will not use these unless specified as the destination. Empty directories are skipped.
- FAT32 (for the USB gadget) is well supported, but other file systems have not been tested.
- Images stay in memory on the photo frame. As a result, if the endpoint's USB gadget encounters an issue, the images on the photo frame may not be up-to-date. Because of this limitation, you cannot easily visually debug problems with the endpoint if images are shown.
- During `sync`s (especially if the recommended watchdog from the [guide][USBGUIDE] is installed), the photo frame may display no images or the settings/overview screen. This transition should only last a couple seconds, even on the aforementioned *Raspberry Pi Zero W*.

## Mitigations to limitations

- Images must be JPG. If your frame supports other extensions, feel free to change this in `photo_dash.image.DashImg.create`; the line is `self.dest = config.DEST / f'{self.module}.jpg'`.
- Images output from `photo_dash.image.DashImg` will be constrained to the resolution configured (default: 480 x 234).
- The visible area is a little reduced from its expected image resolution, probably due to the underlying display being partially obscured by the enclosure. To compensate for these cut borders, `photo_dash.image.DashImg` has two attributes that change offset from the outer edge: `H_SPACER` (horizontal) and `V_SPACER` (vertical). Both spacers will apply on two sides each: top and bottom for `V_SPACER` and left and right for `H_SPACER`. **If your frame does not have this issue, feel free to leave both spacers at 0.**
- A slideshow option is required for full functionality, even when not using the exact photo frame described above.
- Regarding images staying in memory, consequently when quiet hours are enabled and active, images from the last update will still be present. To mitigate this issue (or rather, make its quiet hours status known) when the frame may be on, you may run [utils_runner.py](utils_runner.py). See [Usage](#usage) for more details.
- The font must be monospace. It is difficult to determine pixel width for characters (and hence, a line of characters) in a non-monospace font, and sections become unwieldy to calculate without assuming monospace. If you replace the font, create a test image with more than the expected maximum number of characters per line with the font size `SECTION_SIZE` (in `photo_dash.image.DashImg`), count the maximum rendered characters, and change `SECTION_CHAR` to this value. *A test image creator may be developed later to accommodate this setup process.*
- Another reason why a monospace font is required: When rendering gauges, some numbers may be omitted if they cannot be rendered without obscuring an existing number. Since gauge markers are sorted from lowest to highest and their anchors are mid-aligned, each marker must check how far it is from its closest left neighbor (with half of its neighbor's width calculated). If the marker does not have enough space, it will not be rendered. Gauge values are also subject to this (including space from its nearest right neighbor), although gauge value lines will still be rendered regardless.
- If you are using the guide (specifically the kernel module `g_mass_storage`), in order for the endpoint to properly work after a reboot, I recommend adding the `modprobe` command (without `modprobe`) from the guide into a separate file under `/etc/modules-load.d`. Otherwise, you may have to manually update the kernel module (`g_mass_storage`).
- The USB gadget must be FAT32 to avoid any unforeseen problems. The *Raspberry Pi Foundation* guide mounts the simulated storage as FAT32.
- Because FAT32 storage does not support sym-linking, files must be copied over or directly written to storage. Specify the output directory in the configuration.
- The output directory in the configuration should point to the root of the mounted volume. If you have followed the guide linked above, this should be `/mnt/usb_share`. Although directories are supported, their behavior has not been tested (specifically, display order).

## Usage

0. Clone the project. A virtual environment is highly recommended for managing the project and isolating its dependencies.
1. [Setup](#setup) [config.json](config.json.example) by copying the example file and renaming it. `"width"` and `"length"` must be integers. `"destination"` must be a string that can be parsed as a path using `pathlib.Path`. (Both relative and absolute paths can work here.)
2. Run [photo_dash/app.py](photo_dash/app.py), preferably with `gunicorn` (provided in [requirements.txt](requirements.txt)). The endpoint does not do anything on its own; use modules to send data to convert to a `photo-dash` image.
3. (Optional) Run [utils_runner.py](utils_runner.py) for extra utilities. Currently, this includes creating an image with text that describes quiet hours when in effect. The script should be run in background, preferably with any init system provided by the operating system.

After everything has been set up, I recommend setting firewalls to restrict external access. Preferably, use something like `ufw` and restrict incoming connections to a subnet or even individual addresses.

## Creating Modules

Modules should be cloned (and forked) from the [base modules](https://github.com/cj-wong/photo-dash-base) to provide some universal functionality. More details are within each language's directory.

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

### Optional configuration

**Quiet Hours**

- `"quiet_start"`: integer; when quiet hours should start; requests (except for `GET` `QuietHours`) will not be fulfilled during this time
- `"quiet_end"`: integer; when quiet hours should end; requests will resume

⚠ If you intend to use quiet hours, both quiet hours fields must be defined and not also be the same as each other. You cannot define only one field.

**Stale File Check**

- `"stale_check"`: boolean; whether to enable stale file checking (default: `false`)
- `"stale_threshold"`: integer; how long time in hours must pass since the last file update (default: `0`)
- `"stale_follow_quiet_hours"`: boolean; whether quiet hours should affect the check (see note below) (default: `false`)

⚠ If you intend to use the stale file check, both `"stale_check"` and `stale_threshold"` must be set and not their respective default values.

⚠ If `"stale_follow_quiet_hours"` is set to `true`, the file check will subtly change: it will no longer run when quiet hours are in effect, and the threshold will subtract the quiet hours that have elapsed since the last file update.

## Disclaimer

This project is not affiliated with or endorsed by [Leed's] or [the Raspberry Pi Foundation][RPI]. See [LICENSE](LICENSE) for more detail.

[Leed's]: https://www.pcna.com/leeds/en-us
[RPI]: https://www.raspberrypi.org/
[RPIZ]: https://www.raspberrypi.org/products/raspberry-pi-zero-w/
[USBGUIDE]: https://magpi.raspberrypi.org/articles/pi-zero-w-smart-usb-flash-drive
[.header]: images/example.jpg?raw=true
[base.py]: https://github.com/cj-wong/photo-dash-base.py
