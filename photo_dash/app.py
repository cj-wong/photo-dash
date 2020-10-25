from flask import Flask, request
from flask_restful import Api, Resource

from photo_dash import image


APP = Flask(__name__)
API = Api(APP)


class PhotoDash(Resource):
    """The photo-dash endpoint."""

    def put(self) -> int:
        """Put new data from a request into an image.

        Returns:
            int: HTTP status code 201

        """
        module = request.form['module']
        title = request.form['title']
        sections = request.form['sections']
        img = image.DashImg(module, title, sections)
        try:
            img.create()
        except image.TooManySections:
            return 401
        return 201


API.add_resource(PhotoDash, '/')
