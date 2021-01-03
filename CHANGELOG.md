# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.7] - 2021-01-02
### Changed
- The project has now been linted additionally by `mypy` on top of `Flake8`.
    - As a result, several functions had their type-hints and/or return values corrected.
    - `SECTIONS` in [image.py] was incorrectly typed and now should accurately represent the list of sections allowed.
    - `T_FONT` in [image.py] could not be used as an alias and was dropped entirely.
    - If `QUIET_HOURS` couldn't be set up in [config.py]

## [0.1.6] - 2020-12-10
### Changed
- When sending a JSON to the endpoint, the module name no longer needs to include `photo-dash-` at the beginning. If the prefix is missing, it will be automatically added to the module name.

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
- `get_number_half_width()` in [image.py] should now accept `float` instead of strictly `int`.

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

[config.py]: photo_dash/config.py
[image.py]: photo_dash/image.py
