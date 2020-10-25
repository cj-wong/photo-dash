from photo_dash import config
from photo_dash.app import APP


if __name__ == '__main__':
    config.LOGGER.info('Starting main.py')
    APP.run()
