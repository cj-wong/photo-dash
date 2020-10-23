from typing import Any, Dict, List, Union

import pendulum
from flask import Flask, request
from flask_restful import API, Resource
from PIL import Image, ImageDraw, ImageFont

from photo_dash import config


APP = Flask(__name__)
API = API(APP)

SECTIONS = Dict[str, Union[str, List[Dict[str, Any]]]]


class PhotoDash(Resource):
    """The photo-dash endpoint."""

    def put(self) -> int:
        """Put new data from a request into an image.

        Returns:
            int: HTTP status code 201

        """
        pendulum.now()
        module = request.form['module']
        title = request.form['title']
        sections = request.form['data']
        y = 0
        with Image.new('RGB', config.CANVAS) as im:
            draw = ImageDraw.Draw(im)
            title_size = 20
            title_font = ImageFont.truetype(font=FONT, size=title_size)
            draw.text((0, 0), title, fill='#FFFFFF', font=title_font)
            y = next_y(y, title_size)
            for section in sections:
                pass
            im.save(f'{module}.jpg')
        return 201


class DashImg:
    """Represents a photo-dash image."""

    SPACER = 1
    FONT = 'DejaVuSans.ttf'

    TITLE_COLOR = '#FFFFFF'
    TITLE_SIZE = 20
    TITLE_FONT = ImageFont.truetype(font=FONT, size=TITLE_SIZE)

    def __init__(self) -> None:
        """Initialize parameters for DashImg."""
        self.y = 0

    def next_y(self, delta: int) -> None:
        """Get the next value for y given a delta.

        To prevent vertical clutter, a small padding value will also apply.

        Args:
            delta (int): amount to increase y

        """
        self.y += delta + self.SPACER

    def create(self, module: str, title: str, sections: SECTIONS) -> None:
        """Create a new image given parameters."""
        with Image.new('RGB', config.CANVAS) as im:
            draw = ImageDraw.Draw(im)
            draw.text((0, 0), title, fill=self.TITLE_COLOR, font=self.TITLE_FONT)
            self.next_y(self.title_size)
            for section in sections:
                pass
            im.save(f'{module}.jpg')


API.add_resource(PhotoDash, '/')


if __name__ == '__main__':
    APP.run()
