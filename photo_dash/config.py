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

# Required configuration

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

CANVAS = (WIDTH, LENGTH)

# Optional configuration

try:
    QUIET_START = CONFIG['quiet_start']
    QUIET_END = CONFIG['quiet_end']
    if (QUIET_START == QUIET_END
            or type(QUIET_START) is not int
            or type(QUIET_END) is not int):
        raise ValueError

    QUIET_HOURS = {
        period: CONFIG[period]
        for period in _QUIET_KEYS
        }
except (KeyError, ValueError):
    LOGGER.info('Quiet hours are disabled.')
    LOGGER.info('They may have been malformed or missing.')
    QUIET_HOURS = None
