from dataclasses import dataclass
from textwrap import wrap
from typing import Any, Dict, List, Union

import pendulum
from PIL import Image, ImageDraw, ImageFont

from photo_dash import config


SECTIONS = Dict[str, Union[str, List[Dict[str, Any]]]]
T_FONT = ImageFont.FreeTypeFont

class TooManySections(BufferError):
    """Too many sections were provided. The image cannot be rendered."""

    def __init__(self, n_sections: int) -> None:
        """Initialize the error with number of sections.

        Args:
            n_sections (int): number of sections that triggered error

        """
        super().__init__(
            f'You have too many ({n_sections}) sections to render. '
            'Try picking fewer sections to send.'
            )


@dataclass
class DashImg:
    """Represents a photo-dash image.

    Attributes:
        module (str): the name of the module the image represents
        title (str): title of the image; goes at the top of the image
        sections (SECTIONS): a response given to the endpoint
        SPACER (int): how much to space rows of elements
        FONT (str): the name of the font to use for all text elements
        TEXT_COLOR (str): color for the title on an image ('#FFFFFF')
        TITLE_SIZE (int): font size of the title (20)
        TITLE_FONT (T_FONT): font & size for the title
        SECTION_SIZE (int): font size for sections (16)
        SECTION_FONT (T_FONT): font & size for sections
        FOOTER_SIZE (int): font size of the footer (20)
        FOOTER_FONT (T_FONT): font & size for the footer
        MAX_C_PER_LINE (int): maximum characters allowed per line
        SECTION_SPACING (Dict[str, int]): how much spacing each section
            creates; e.g. text only needs 1 spacing per line

    """

    # dataclass attributes

    module: str
    title: str
    sections: SECTIONS
    # The following should not be initialized.
    y: int = 0
    dt: pendulum.datetime = pendulum.now()

    # Other attributes

    SPACER = 5
    FONT = 'DejaVuSansMono.ttf'

    TEXT_COLOR = '#FFFFFF' # Does not apply to sections
    TITLE_SIZE = 20
    TITLE_FONT = ImageFont.truetype(font=FONT, size=TITLE_SIZE)
    SECTION_SIZE = 16
    SECTION_FONT = ImageFont.truetype(font=FONT, size=SECTION_SIZE)
    FOOTER_SIZE = 10
    FOOTER_FONT = ImageFont.truetype(font=FONT, size=FOOTER_SIZE)
    # For a width of 480, SECTION_SIZE of 16, and using a monospace font,
    # 48 chars could fit on one line. As such, MAX_C_PER_LINE can be scaled
    # by dividing configured width by 10.
    MAX_C_PER_LINE = config.WIDTH // 10

    SECTION_SPACING = {
        'text': 1,
        'gauge': 2,
        }

    def _next_y(self, delta: int) -> None:
        """Get the next value for y given a delta.

        To prevent vertical clutter, a small value will also pad y.

        Args:
            delta (int): amount to increase y

        """
        self.y += delta + self.SPACER

    def create(self) -> None:
        """Create a new image given parameters.

        Raises:
            TooManySections: if too many sections are to be rendered

        """
        if not self.sections_fit():
            raise TooManySections(len(self.sections))

        with Image.new('RGB', config.CANVAS) as self.im:
            self.draw = ImageDraw.Draw(self.im)
            self.create_text(self.title, self.TEXT_COLOR, self.TITLE_FONT)
            for section in self.sections:
                try:
                    section_type = section['type']
                    if section_type == 'text':
                        color = section['color']
                        text = section['value']
                        self.create_text(text, color, self.SECTION_FONT)
                except KeyError as e:
                    config.LOGGER.warning(
                        'Could not determine type of section. Skipping.'
                        )
                    config.LOGGER.warning(f'Module: {self.module}')
                    config.LOGGER.warning(f'More info: {e}')
                    continue
            self.create_footer()
            self.im.save(f'{self.module}.jpg', quality=85)

    def sections_fit(self) -> bool:
        """Check whether the sections fit in the image.

        Returns:
            bool: whether the sections will fit in the image or not

        """
        space = sum(
            [
                self.SECTION_SPACING[section['type']]
                for section in self.sections
                ]
            ) + self.SPACER * (len(self.sections) - 1)
        free_space = (
            config.LENGTH
            - (self.TITLE_SIZE + self.SPACER)
            - (self.FOOTER_SIZE + 2 * self.SPACER) # Add extra padding
            )
        return free_space > space

    def create_text(self, text: str, color: str, font: T_FONT) -> None:
        """Create text and insert into drawing.

        Args:
            text (str): contents of the string
            color (str): color in hex format
            font (T_FONT): the font & size used for the text

        """
        for line in wrap(text, width=self.MAX_C_PER_LINE):
            self.draw.text(
                (0, self.y),
                line,
                fill=color,
                font=font,
                )
            self._next_y(font.size)

    def create_footer(self) -> None:
        """Create footer (text) for this image.

        Footers currently only contain the date and time.

        """
        message = f'Generated at: {self.dt.to_datetime_string()}'
        self.draw.text(
            (config.WIDTH, config.LENGTH),
            message,
            fill=self.TEXT_COLOR,
            font=self.FOOTER_FONT,
            anchor='rs',
            )
