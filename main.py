from photo_dash import config, app


if __name__ == '__main__':
    config.LOGGER.info('Starting main.py')
    app.APP.run()
