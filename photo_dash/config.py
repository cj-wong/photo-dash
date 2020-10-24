import json
import logging
import logging.handlers
from pathlib import Path


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

CONFIG_LOAD_ERRORS = (
    FileNotFoundError,
    KeyError,
    TypeError,
    ValueError,
    json.decoder.JSONDecodeError,
    )


try:
    with open('config.json', 'r') as f:
        CONFIG = json.load(f)
    WIDTH = CONFIG['width']
    LENGTH = CONFIG['length']
    DEST = Path(CONFIG['destination'])
    if not DEST.exists():
        raise RuntimeError
except CONFIG_LOAD_ERRORS as e:
    LOGGER.error('config.json doesn\'t exist or is malformed.')
    LOGGER.error(f'More information: {e}')
    raise e
except RuntimeError as e:
    LOGGER.error(f'{DEST} is not a valid destination. Please specify a path.')
    raise e

CANVAS = (WIDTH, LENGTH)
