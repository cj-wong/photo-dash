from photo_dash import config, utils


if __name__ == '__main__':
    config.LOGGER.info('Starting utils.py')
    utils.setup_quiet_hours()
