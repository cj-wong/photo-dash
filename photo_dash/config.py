import json
import logging
import logging.handlers


LOGGER = logging.getLogger('photo-dash')
LOGGER.setLevel(logging.DEBUG)

FH = logging.handlers.RotatingFileHandler(
    'photo-dash.log',
    maxBytes=40960,
    backupCount=5,
    )
FH.setLevel(logging.DEBUG)

CH = logging.StreamHandler()
CH.setLevel(logging.WARNING)

FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
FH.setFormatter(FORMATTER)
CH.setFormatter(FORMATTER)

LOGGER.addHandler(FH)
LOGGER.addHandler(CH)

CONFIG_ERRORS = (KeyError, TypeError, ValueError)

DEFAULT_WIDTH = 480
DEFAULT_LENGTH = 234


try:
    with open('config.json', 'r') as f:
        CONFIG = json.load(f)
    WIDTH = CONFIG['width']
    LENGTH = CONFIG['length']
except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
    LOGGER.error('config.json doesn\'t exist or is malformed.')
    LOGGER.error(f'More information: {e}')
    raise e
except CONFIG_ERRORS:
    WIDTH = DEFAULT_WIDTH
    LENGTH = DEFAULT_LENGTH
    LOGGER.warning(
        f'Could not load width or length. Defaulting to {WIDTH}x{LENGTH}'
        )

CANVAS = (WIDTH, LENGTH)
