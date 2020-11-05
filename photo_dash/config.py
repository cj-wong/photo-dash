import json
import logging
import logging.handlers
from pathlib import Path


_LOGGER_NAME = 'photo-dash'

LOGGER = logging.getLogger(_LOGGER_NAME)
LOGGER.setLevel(logging.DEBUG)

_FH = logging.handlers.RotatingFileHandler(
    f'{_LOGGER_NAME}.log',
    maxBytes=40960,
    backupCount=5,
    )
_FH.setLevel(logging.DEBUG)

_CH = logging.StreamHandler()
_CH.setLevel(logging.WARNING)

_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
_FH.setFormatter(_FORMATTER)
_CH.setFormatter(_FORMATTER)

LOGGER.addHandler(_FH)
LOGGER.addHandler(_CH)

_CONFIG_LOAD_ERRORS = (
    FileNotFoundError,
    KeyError,
    TypeError,
    ValueError,
    json.decoder.JSONDecodeError,
    )

_QUIET_KEYS = (
    'quiet_start',
    'quiet_end',
    )


try:
    with open('config.json', 'r') as f:
        CONFIG = json.load(f)
    WIDTH = CONFIG['width']
    LENGTH = CONFIG['length']
    DEST = Path(CONFIG['destination'])
    if not DEST.exists():
        raise RuntimeError
except _CONFIG_LOAD_ERRORS as e:
    LOGGER.error('config.json doesn\'t exist or is malformed.')
    LOGGER.error(f'More information: {e}')
    raise e
except RuntimeError as e:
    LOGGER.error(f'{DEST} is not a valid destination. Please specify a path.')
    raise e

try:
    QUIET_HOURS = {
        period: hour
        for period, hour in CONFIG.items()
        if period in _QUIET_KEYS and type(hour) is int
        }
    if not QUIET_HOURS or len(set(QUIET_HOURS.values())) == 1:
        raise ValueError
except ValueError:
    LOGGER.info(
        'Quiet hours were not set. They are either not present or malformed.'
        )
    del QUIET_HOURS


CANVAS = (WIDTH, LENGTH)
