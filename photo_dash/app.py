from dataclasses import dataclass
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
        img = DashImg(module, title, sections)
        img.create()
        return 201


@dataclass
class DashImg:
    """Represents a photo-dash image.

    Attributes:
        module (str): the name of the module the image represents
        title (str): title of the image; goes at the top of the image
        sections (SECTIONS): a response given to the endpoint
        FONT (str): the name of the font to use for all text elements
        TITLE_COLOR (str): color for the title on an image ('#FFFFF')
        TITLE_SIZE (int): size of the title (20)
        TITLE_FONT (ImageFont.FreeTypeFont): font for the title
        SPACER (int): how much to space rows of elements

    """

    module: str
    title: str
    sections: SECTIONS
    y: int = 0  # This should not be initialized.

    SPACER = 1
    FONT = 'DejaVuSans.ttf'

    TITLE_COLOR = '#FFFFFF'
    TITLE_SIZE = 20
    TITLE_FONT = ImageFont.truetype(font=FONT, size=TITLE_SIZE)

    def _next_y(self, delta: int) -> None:
        """Get the next value for y given a delta.

        To prevent vertical clutter, a small padding value will also apply.

        Args:
            delta (int): amount to increase y

        """
        self.y += delta + self.SPACER

    def create(self) -> None:
        """Create a new image given parameters."""
        with Image.new('RGB', config.CANVAS) as im:
            draw = ImageDraw.Draw(im)
            draw.text(
                (0, 0),
                self.title,
                fill=self.TITLE_COLOR,
                font=self.TITLE_FONT
                )
            self._next_y(self.title_size)
            for section in self.sections:
                pass
            im.save(f'{self.module}.jpg')


API.add_resource(PhotoDash, '/')


if __name__ == '__main__':
    APP.run()
