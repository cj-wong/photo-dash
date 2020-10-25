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
        GAUGE_WIDTH (int): how long the gauge bar should be
        GAUGE_OFFSET (int): how far from the left should the bar start;
            this number ideally should be (1 - ratio) // 2, where
            ratio is the decimal that was used to create GAUGE_WIDTH
        SECTION_SPACING (Dict[str, int]): how much spacing each section
            creates; e.g. text only needs 1 spacing per line

    """

    # dataclass attributes

    module: str
    title: str
    sections: SECTIONS
    # y should not be initialized.
    y: int = 0

    # Other attributes

    SPACER = 10
    V_SPACER = 5
    H_SPACER = 5
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

    GAUGE_WIDTH = int(0.9 * config.WIDTH)
    GAUGE_OFFSET = int(0.05 * config.WIDTH)
    GAUGE_VALUE_STROKE = 2
    GAUGE_LINE_WIDTH = 5
    GAUGE_LINE_COLOR = '#808080'

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

        self.dt = pendulum.now()

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
                    elif section_type == 'gauge':
                        colors = section['color']
                        values = section['range']
                        value = section['value']
                        self.create_gauge(value, values, colors)
                except KeyError as e:
                    config.LOGGER.warning(
                        'Could not determine type of section. Skipping.'
                        )
                    config.LOGGER.warning(f'Module: {self.module}')
                    config.LOGGER.warning(f'More info: {e}')
                    continue
            self.create_footer()
            self.im.save(config.DEST / f'{self.module}.jpg', quality=85)

    def sections_fit(self) -> bool:
        """Check whether the sections fit in the image.

        Returns:
            bool: whether the sections will fit in the image or not

        """
        space = 0
        for section in self.sections:
            if section['type'] == 'text':
                lines = len(wrap(section['value'], width=self.MAX_C_PER_LINE))
                space += lines * self.SECTION_SPACING[section['type']]
            else:
                space += self.SECTION_SPACING[section['type']]
            space += self.SPACER
        space -= self.SPACER
        free_space = (
            config.LENGTH
            - (self.TITLE_SIZE + self.SPACER)
            - (self.FOOTER_SIZE + 2 * self.SPACER) # Add extra padding
            - (2 * self.V_SPACER) # Additional vertical spacers
            )
        return free_space > space

    def create_text(self, text: str, color: str, font: T_FONT) -> None:
        """Create text and insert into drawing.

        Args:
            text (str): contents of the string
            color (str): color in hex format
            font (T_FONT): the font & size used for the text

        """
        if font == self.TITLE_FONT:
            self.y += self.V_SPACER
        for line in wrap(text, width=self.MAX_C_PER_LINE):
            self.draw.text(
                (self.H_SPACER, self.y),
                line,
                fill=color,
                font=font,
                )
            self._next_y(font.size)

    def create_gauge(
        self, value: int, values: List[int], colors: List[str]
            ) -> None:
        """Create gauge given a value and marks (values).

        Args:
            value (int): the reading to use
            values (List[int]): numeric marks along the gauge
            colors (List[int]): color to paint sections between marks

        """
        sort_values = sorted(values)
        if values != sort_values:
            config.LOGGER.warning('The values were unsorted.')
            config.LOGGER.warning(f'Module: {self.module}')
            config.LOGGER.warning(f'Values: {values}')
        end_a = sort_values[0]
        end_b = sort_values[-1]

        # The first marker will use the default text color.
        colors.insert(0, self.TEXT_COLOR)

        x0 = self.GAUGE_OFFSET
        y0 = self.y + self.SECTION_FONT.size + self.SPACER
        y1 = y0 + self.SECTION_FONT.size

        last_x0 = x0

        # Draw the gauge first
        for val, color in zip(values, colors):
            offset = self.get_gauge_offset(val, end_a, end_b)
            self.draw.text(
                (offset, self.y),
                str(val),
                fill=color,
                font=self.SECTION_FONT,
                anchor='mt',
                )
            self.draw.rectangle(
                [(last_x0, y0), (offset, y1)],
                fill=color,
                )
            last_x0 = offset

        offset = self.get_gauge_offset(value, end_a, end_b)
        self.draw.text(
            (offset, self.y),
            str(value),
            fill=self.TEXT_COLOR,
            font=self.SECTION_FONT,
            anchor='mt',
            stroke_width=self.GAUGE_VALUE_STROKE,
            stroke_fill=self.GAUGE_LINE_COLOR,
            )
        self.draw.line(
            [(offset, y0), (offset, y1)],
            fill=self.GAUGE_LINE_COLOR,
            width=self.GAUGE_LINE_WIDTH,
            )

        self._next_y(2 * self.SECTION_FONT.size + self.SPACER)

    def get_gauge_offset(self, value: int, end_a: int, end_b: int) -> int:
        """Get the current gauge offset.

        end_a <= value <= end_b

        Args:
            value (int): the value to measure in gauge
            end_a (int): the minimum of the gauge
            end_b (int): the maximum of the gauge

        """
        length = end_b - end_a
        return (
            (value - end_a)
            * self.GAUGE_WIDTH
            // length
            + self.GAUGE_OFFSET
            )

    def create_footer(self) -> None:
        """Create footer (text) for this image.

        Footers currently only contain the date and time.

        """
        message = f'Generated at: {self.dt.to_datetime_string()}'
        self.draw.text(
            (config.WIDTH - self.H_SPACER, config.LENGTH - self.V_SPACER),
            message,
            fill=self.TEXT_COLOR,
            font=self.FOOTER_FONT,
            anchor='rs',
            )
