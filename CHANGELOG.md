# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.5] - 2020-11-11
### Changed
- Improved docs

## [0.1.4] - 2020-11-04
### Changed
- In reference of issue #1:
    - Added optional fields `"quiet_start"` and `"quiet_end"` in [config.json.example](config.json.example). These should be integers to represent when quiet hours will begin or end.
    - Added another endpoint `/quiet` that will return quiet hours with a `GET` request.
    - During quiet hours, a special image will be generated that indicates images may not be up-to-date. This image will be deleted when quiet hours are over.

### Fixed
- Status codes for `put()` in the API were returned incorrectly.

## [0.1.3] - 2020-10-25
### Changed
- `get_number_half_width()` in [image.py](photo_dash/image.py) should now accept `float` instead of strictly `int`.

## [0.1.2] - 2020-10-25
### Fixed
- The timestamp is now initialized when `DashImg.create()` is called.
- The photo frame is somehow scaling images past their intended borders. This has caused text to go offscreen. Now, text elements (including the footer) will have a small offset. Both title and footer will have a small spacer from the top and bottom. All text elements will have a small spacer from the nearest side.
- Gauge values (marks) should no longer obscure each other. In the case that a number might collide or intersect with a previous number, it will be skipped.
- Following on that, the value for a gauge should also not obscure its closest rendered values (on both sides).

## [0.1.1] - 2020-10-25
### Changed
- In the API, `"data"` was changed to `"sections"` to conform with the existing file.

## [0.1.0] - 2020-10-25
### Added
- Initial version
