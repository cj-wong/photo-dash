from typing import Dict, Union

from flask import Flask, request
from flask_restful import Api, Resource

from photo_dash import config, image, utils


APP = Flask(__name__)
API = Api(APP)


class PhotoDash(Resource):
    """The photo-dash endpoint."""

    def put(self) -> int:
        """Put new data from a request into an image.

        Returns:
            int: HTTP status codes
                201: no errors occurred
                401: too many sections were requested
                503: request was sent during quiet hours

        """
        config.LOGGER.info('Got a request')
        try:
            if utils.in_quiet_hours():
                config.LOGGER.info('Request was sent during quiet hours')
                return 503
        except AttributeError:
            pass

        r = request.get_json()
        module = r['module']
        title = r['title']
        sections = r['sections']
        img = image.DashImg(module, title, sections)
        try:
            config.LOGGER.info('Attempting image creation')
            img.create()
        except image.TooManySections:
            return 401
        return 201


class QuietHours(Resource):
    """Quiet hours for when photo-dash should not receive input."""

    def get(self) -> Union[Dict[str, int], None]:
        """Get quiet hours: quiet_start and quiet_end.

        Returns:
            Dict[str, int]: if quiet hours were set

        """
        try:
            return config.QUIET_HOURS
        except AttributeError:
            return


API.add_resource(PhotoDash, '/')
API.add_resource(QuietHours, '/quiet', '/quiet-hours')
