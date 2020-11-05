from datetime import timedelta
from time import sleep

import pendulum

from photo_dash import config, image


_SECTIONS = [
    {
        'type': 'text',
        'color': '#909090',
        'value': f'Quiet hours are in effect. Images won\'t be updated.'
        },
    {
        'type': 'text',
        'color': '#909090',
        'value': f'Start time: {config.QUIET_START}:00'
        },
    {
        'type': 'text',
        'color': '#909090',
        'value': f'End time: {config.QUIET_END}:00'
        }
    ]


def in_quiet_hours() -> bool:
    """Check whether the current time is within quiet hours.

    Returns:
        bool: True if within quiet hours

    Raises:
        AttributeError: if quiet hours weren't defined in config

    """
    now = pendulum.now()
    hour = now.hour
    if config.QUIET_START > config.QUIET_END:
        if hour >= config.QUIET_START or hour < config.QUIET_END:
            return True
    elif hour in range(config.QUIET_START, config.QUIET_END):
        return True

    return False


def create_quiet_hours_image() -> image.DashImg:
    """Create an image for quiet hours.

    This is in case the photo-dash display is turned on before
    intended wake-up.

    Returns:
        image.DashImg: the image created

    """
    img = image.DashImg('quiet_hours', 'Quiet Hours', _SECTIONS)
    img.create()
    return img


def setup_quiet_hours() -> None:
    """Set up quiet hours; prepare special image for photo-dash.

    Raises:
        ValueError: if next_hour is chronologically before now

    """
    try:
        if in_quiet_hours():
            pass
    except AttributeError:
        return

    while True:
        now = pendulum.now()

        if in_quiet_hours():
            img = create_quiet_hours_image()
        else:
            # Because quiet hours are no longer in effect, delete the image
            # that references the quiet hours.
            try:
                img.delete()
            except NameError:
                pass

        start_diff = config.QUIET_START - now.hour
        end_diff = config.QUIET_END - now.hour

        delta = timedelta(0)

        # Case: now one day before next period (quiet hours will start)
        if start_diff < 0 and end_diff < 0:
            hour = config.QUIET_START
            delta = timedelta(days=1)
        # Case: after quiet hours started
        elif start_diff <= 0:
            hour = config.QUIET_END
            if config.QUIET_START > config.QUIET_END:
                delta = timedelta(days=1)
        # Case: after quiet hours ended
        else:
            hour = config.QUIET_START

        next_hour = pendulum.datetime(
            now.year, now.month, now.day, hour, 0, tz=now.tz
            )
        next_hour += delta

        if next_hour < now:
            config.LOGGER.error(f'{next_hour} is earlier than now ({now})')
            raise ValueError

        diff = next_hour - now
        sleep(diff.seconds)
