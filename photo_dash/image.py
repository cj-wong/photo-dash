from dataclasses import dataclass
from typing import Any, Dict, List, Union

from PIL import Image, ImageDraw, ImageFont

from photo_dash import config


SECTIONS = Dict[str, Union[str, List[Dict[str, Any]]]]


@dataclass
class DashImg:
    """Represents a photo-dash image.

    Attributes:
        module (str): the name of the module the image represents
        title (str): title of the image; goes at the top of the image
        sections (SECTIONS): a response given to the endpoint
        FONT (str): the name of the font to use for all text elements
        TITLE_COLOR (str): color for the title on an image ('#FFFFF')
        TITLE_SIZE (int): font size of the title (20)
        TITLE_FONT (ImageFont.FreeTypeFont): font & size for the title
        SPACER (int): how much to space rows of elements

    """

    module: str
    title: str
    sections: SECTIONS
    y: int = 0  # This should not be initialized.

    SPACER = 1
    FONT_NAME = 'DejaVuSans.ttf'

    TITLE_COLOR = '#FFFFFF'
    TITLE_SIZE = 20
    FONT = ImageFont.truetype(font=FONT_NAME)

    SECTION_SIZE = 16

    def _next_y(self, delta: int) -> None:
        """Get the next value for y given a delta.

        To prevent vertical clutter, a small padding value will also apply.

        Args:
            delta (int): amount to increase y

        """
        self.y += delta + self.SPACER

    def create(self) -> None:
        """Create a new image given parameters."""
        with Image.new('RGB', config.CANVAS) as self.im:
            self.draw = ImageDraw.Draw(self.im)
            self.create_text(self.title, self.TITLE_COLOR, self.TITLE_SIZE)
            for section in self.sections:
                try:
                    section_type = section['type']
                    if section_type == 'text':
                        color = section['color']
                        text = section['value']
                        self.create_text(text, color, self.SECTION_SIZE)
                except KeyError as e:
                    config.LOGGER.warning(
                        'Could not determine type of section. Skipping.'
                        )
                    config.LOGGER.warning(f'Module: {self.module}')
                    config.LOGGER.warning(f'More info: {e}')
                    continue
            self.im.save(f'{self.module}.jpg')

    def create_text(self, text: str, color: str, font_size: int) -> None:
        """Create text and insert into drawing."""
        self.FONT.size = font_size
        self.draw.text(
            (0, self.y),
            text,
            fill=color,
            font=self.FONT,
            )
        self._next_y(font_size)
