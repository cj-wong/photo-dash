from photo_dash import config, app
from app import APP


if __name__ == '__main__':
    config.LOGGER.info('Starting main.py')
    APP.run()
