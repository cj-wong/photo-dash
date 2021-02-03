from dataclasses import dataclass
from math import ceil, floor, log10
from pathlib import Path
from textwrap import wrap
from typing import (
    Any, Collection, Dict, List, Mapping, Optional, Sequence, Tuple, Union)

import pendulum
from PIL import Image, ImageDraw, ImageFont

from photo_dash import config


SECTIONS = Sequence[Mapping[str, Any]]

SECTION_SPACING = {
    'text': 1,
    'gauge': 2,
    }

# Spacing: between lines and away from the canvas edges
SPACER = 10
V_SPACER = 5
H_SPACER = 5

# Font-related variables
FONT = 'DejaVuSansMono.ttf'

TEXT_COLOR = '#FFFFFF' # Does not apply to sections
TITLE_SIZE = 20
TITLE_FONT = ImageFont.truetype(font=FONT, size=TITLE_SIZE)

SECTION_SIZE = 16
SECTION_FONT = ImageFont.truetype(font=FONT, size=SECTION_SIZE)
# This ratio depends on the current font, FONT.
SECTION_CHAR = int(16 * 10 / 16)

FOOTER_SIZE = 10
FOOTER_FONT = ImageFont.truetype(font=FONT, size=FOOTER_SIZE)
# For a width of 480, SECTION_SIZE of 16, and using a monospace font,
# 48 chars could fit on one line. As such, MAX_C_PER_LINE can be scaled
# by dividing configured width by 10.
# MAX_C_PER_LINE is then subtracted by 2 H_SPACERs rounded up.
MAX_C_PER_LINE = (
    config.WIDTH
    // SECTION_CHAR
    - ceil(2 * H_SPACER / SECTION_CHAR)
    )

GAUGE_WIDTH = int(0.9 * config.WIDTH)
GAUGE_OFFSET = int(0.05 * config.WIDTH)
GAUGE_VALUE_STROKE = 2
GAUGE_LINE_WIDTH = 5
GAUGE_LINE_COLOR = '#808080'

# Render instruction type
COORDINATES = Union[int, Tuple[int, int]]
INSTRUCTIONS = List[
    Tuple[
        str,
        Collection[COORDINATES],
        Optional[str],
        Dict[str, Union[str, int]]
        ]
    ]


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
class DashImage:
    """Represents a photo-dash image.

    Attributes:
        module (str): the name of the module the image represents
        title (str): title of the image; goes at the top of the image
        sections (SECTIONS): a response given to the endpoint
        SPACER (int): how much to space rows of elements
        FONT (str): the name of the font to use for all text elements
        TEXT_COLOR (str): color for the title on an image ('#FFFFFF')
        TITLE_SIZE (int): font size of the title (20)
        TITLE_FONT (ImageFont.FreeTypeFont): font & size for the title
        SECTION_SIZE (int): font size for sections (16)
        SECTION_FONT (ImageFont.FreeTypeFont): font & size for sections
        FOOTER_SIZE (int): font size of the footer (20)
        FOOTER_FONT (ImageFont.FreeTypeFont): font & size for the footer
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

    def create(self) -> None:
        """Create a new image given parameters.

        Raises:
            TooManySections: if too many sections are to be rendered

        """
        if not self.sections_fit():
            raise TooManySections(len(self.sections))

        with Image.new('RGB', config.CANVAS) as im:
            self.draw = ImageDraw.Draw(im)

            header = SectionText(self.y, self.title, TEXT_COLOR, TITLE_FONT)
            self.render_instructions(header.get_instructions())
            self.y = header.y

            for section in self.sections:
                try:
                    section_type = section['type']
                    value = section['value']
                    color = section['color']

                    if section_type == 'text':
                        text = SectionText(self.y, value, color, SECTION_FONT)
                        y = text.y
                        instructions = text.get_instructions()
                    elif section_type == 'gauge':
                        colors = section['color']
                        values = section['range']
                        gauge = SectionGauge(self.y, value, values, colors)
                        y = gauge.y
                        instructions = gauge.get_instructions()

                    self.render_instructions(instructions)
                    self.y = y

                except KeyError as e:
                    config.LOGGER.warning(
                        'The section is malformed. Skipping...')
                    config.LOGGER.warning(f'Module: {self.module}')
                    config.LOGGER.warning(f'More info: {e}')
                    continue
                except NameError as e:
                    config.LOGGER.warning(
                        'Could not determine type of section. Skipping...')
                    config.LOGGER.warning(f'Module: {self.module}')
                    config.LOGGER.warning(f'More info: {e}')
                    continue

            footer = SectionFooter(self.y)
            self.render_instructions(footer.get_instructions())

            self.dest = config.DEST / f'{self.module}.jpg'
            im.save(self.dest, quality=85)

    def delete(self) -> None:
        """Delete the image. This is mostly used for quiet hour images."""
        file = Path(self.dest)
        file.unlink()

    def sections_fit(self) -> bool:
        """Check whether the sections fit in the image.

        Returns:
            bool: whether the sections will fit in the image (True)
                or not (False)

        """
        space = 0
        for section in self.sections:
            if section['type'] == 'text':
                lines = len(wrap(section['value'], width=MAX_C_PER_LINE))
                space += lines * SECTION_SPACING[section['type']]
            else:
                space += SECTION_SPACING[section['type']]
            space += SPACER
        space -= SPACER
        free_space = (
            config.LENGTH
            - (TITLE_SIZE + SPACER)
            - (FOOTER_SIZE + 2 * SPACER) # Add extra padding
            - (2 * V_SPACER) # Additional vertical spacers
            )
        return free_space > space

    def render_instructions(self, instructions: INSTRUCTIONS) -> None:
        """Render the instructions onto the image.

        Args:
            instructions (INSTRUCTIONS): a list of instructions

        """
        for instruction in instructions:
            command, coordinates, text, kwargs = instruction
            try:
                method = getattr(self.draw, command)
            except AttributeError:
                config.LOGGER.error(f'No such method {method}.')
                continue
            if command == 'text':
                method(coordinates, text, **kwargs)
            else:
                method(coordinates, **kwargs)


@dataclass
class Section:
    """Represents an image section."""

    # draw: ImageDraw.Draw # the renderer for the image
    y: int

    def __post_init__(self) -> None:
        """After initialization, create a list of rendering instructions.

        An individual instruction is like so:

            1. (str) type of render instruction for ImageDraw.Draw
            2. (Tuple[int, int]) a x, y coordinate for the starting point of
               the render
            3. (str, None) text if required for section
            4. (Dict[str, Union[str, int]]): kwargs for the render instruction

        """
        self.instructions: INSTRUCTIONS = []

    def _next_y(self, delta: int) -> None:
        """Get the next value for y given a delta.

        To prevent vertical clutter, a small value (SPACER) will also pad y.

        Args:
            delta (int): amount to increase y

        """
        self.y += delta + SPACER

    def get_instructions(self) -> INSTRUCTIONS:
        """Return the current instructions.

        Returns:
            INSTRUCTIONS: the instructions to be sent to the renderer

        """
        return self.instructions


@dataclass
class SectionText(Section):
    """Represents a text element on one line.

    Attributes:
        text (str): contents of the string
        color (str): color in hex format
        font (ImageFont.FreeTypeFont): the font & size used for the text

    """

    text: str
    color: str
    font: ImageFont.FreeTypeFont

    def __post_init__(self) -> None:
        """Create text and insert into drawing."""
        super().__post_init__()
        if self.font == TITLE_FONT:
            self.y += V_SPACER
        for line in wrap(self.text, width=MAX_C_PER_LINE):
            self.instructions.append(
                (
                    'text',
                    (H_SPACER, self.y),
                    line,
                    {'fill': self.color, 'font': self.font}
                    )
                )
            self._next_y(self.font.size)


@dataclass
class SectionFooter(Section):
    """Represents a specialized text element at the bottom of the image.

    Currently contains the date.

    Unlike other sections, the vertical offset is not required, because
    the footer is rendered relative to the bottom right corner of the canvas.
    Because of this characteristic, the footer also does not need to inherit
    from the Section parent class.

    """

    def __post_init__(self) -> None:
        """Create footer (text) for this image.

        Footers currently only contain the date and time.

        """
        super().__post_init__()
        dt = pendulum.now()
        message = f'Generated at: {dt.to_datetime_string()}'
        self.instructions.append(
            (
                'text',
                (config.WIDTH - H_SPACER, config.LENGTH - V_SPACER),
                message,
                {'fill': TEXT_COLOR, 'font': FOOTER_FONT, 'anchor': 'rs'}
                )
            )


@dataclass
class SectionGauge(Section):
    """Represents a gauge within an image."""

    value: int
    values: List[int]
    colors: List[str]

    def __post_init__(self) -> None:
        """Create gauge given a value and marks (values).

        Args:
            value (int): the reading to use
            values (List[int]): numeric marks along the gauge
            colors (List[int]): color to paint sections between marks

        """
        # try:
        #     # Delete self.last_gauge_value in case the module creates
        #     # multiple gauges. This is to replicate prior behavior,
        #     # `self.last_gauge_value = None` that mypy did not allow.
        #     del self.last_gauge_value
        #     del self.last_gauge_offset
        # except AttributeError:
        #     pass
        super().__post_init__()

        self.created_gauge_values: Dict = {}

        sort_values = sorted(self.values)
        if self.values != sort_values:
            config.LOGGER.warning('The values were unsorted.')
            # config.LOGGER.warning(f'Module: {self.module}')
            config.LOGGER.warning(f'Values: {self.values}')
        end_a = sort_values[0]
        end_b = sort_values[-1]

        # The first marker will use the default text color.
        self.colors.insert(0, TEXT_COLOR)

        x0 = GAUGE_OFFSET
        y0 = self.y + SECTION_FONT.size + SPACER
        y1 = y0 + SECTION_FONT.size

        last_x0 = x0

        # Draw the gauge first
        for val, color in zip(self.values, self.colors):
            offset = self.get_gauge_offset(val, end_a, end_b)

            if (getattr(self, 'last_gauge_value', None) is None
                    or not self.does_gauge_text_collide(val, offset)):
                self.create_gauge_value(val, offset, color)

            c0 = (last_x0, y0)
            c1 = (offset, y1)

            self.instructions.append(
                ('rectangle', (c0, c1), None, {'fill': color}))

            last_x0 = offset

        offset = self.get_gauge_offset(self.value, end_a, end_b)
        if not self.does_gauge_value_collide(self.value, offset):
            self.instructions.append(
                (
                    'text',
                    (offset, self.y),
                    str(self.value),
                    {
                        'fill': TEXT_COLOR,
                        'font': SECTION_FONT,
                        'anchor': 'mt',
                        'stroke_width': GAUGE_VALUE_STROKE,
                        'stroke_fill': GAUGE_LINE_COLOR,
                        }
                    )
                )

        self.instructions.append(
            (
                'line',
                ((offset, y0), (offset, y1)),
                None,
                {
                    'fill': GAUGE_LINE_COLOR,
                    'width': GAUGE_LINE_WIDTH,
                    }
                )
            )

        self._next_y(2 * SECTION_FONT.size + SPACER)

    def create_gauge_value(self, value: int, offset: int, color: str) -> None:
        """Create a gauge value (mark).

        Args:
            value (int): a gauge value or marker
            offset (int): horizontal offset for this current value
            color (str): color in hex format

        """
        self.instructions.append(
            (
                'text',
                (offset, self.y),
                str(value),
                {
                    'fill': color,
                    'font': SECTION_FONT,
                    'anchor': 'mt',
                    }
                )
            )
        self.last_gauge_value = value
        self.last_gauge_offset = offset
        self.created_gauge_values[value] = offset

    def get_gauge_offset(self, value: int, end_a: int, end_b: int) -> int:
        """Get the current gauge offset.

        end_a <= value <= end_b

        Args:
            value (int): the value to measure in gauge
            end_a (int): the minimum of the gauge
            end_b (int): the maximum of the gauge

        Returns:
            int: horizontal pixel offset

        """
        length = end_b - end_a
        return (
            (value - end_a)
            * GAUGE_WIDTH
            // length
            + GAUGE_OFFSET
            )

    def does_gauge_text_collide(self, value: int, offset: int) -> bool:
        """Determine whether new text will collide with existing text.

        Specifically, check the magnitude (number of digits) for both
        value and last_val and check whether they may possibly overlap
        in bounding box.

        value should always be greater than or equal to
        self.last_gauge_value.

        Args:
            value (int): the current value
            offset (int): the current value's offset

        Returns:
            bool: whether text will collide (True) or not (False)

        """
        width = self.get_number_half_width(value)
        last_width = self.get_number_half_width(self.last_gauge_value)
        config.LOGGER.info(f'value: {value}, last: {self.last_gauge_value}')
        config.LOGGER.info(f'width: {width}, last_width: {last_width}')
        return (offset - width) < (self.last_gauge_offset + last_width)

    def does_gauge_value_collide(self, value: int, offset: int) -> bool:
        """Gauges whether a gauge value may collide with marks.

        Because some marks may not have been rendered,
        self.created_gauge_values is used to ensure collision check with
        only rendered marks.

        Similar to does_gauge_text_collide but checks both closest smallest
        and closest largest values.

        Args:
            value (int): the gauge value
            offset (int): the current value's offset

        Returns:
            bool: whether text will collide (True) or not (False)

        """
        if value in self.created_gauge_values:
            return True
        width = self.get_number_half_width(value)
        # Not to be confused with dict.values(), these are keys.
        values = list(self.created_gauge_values)
        values.append(value)
        values.sort()
        index = values.index(value)
        below = values[index - 1]
        above = values[index + 1]

        below_width = self.get_number_half_width(below)
        if (offset - width) < (self.created_gauge_values[below] + below_width):
            return True
        above_width = self.get_number_half_width(above)
        if (self.created_gauge_values[above] - above_width) < (offset + width):
            return True

        return False

    def get_number_half_width(self, number: float) -> int:
        """Get the pixel width of a number determined by the font.

        Args:
            number (float): the number to convert to half pixel width

        Returns:
            int: half pixel width of a number, rounded up

        """
        symbols = 0
        # Handle negative sign
        if number < 0:
            symbols += 1
            number = abs(number)
        # Handle decimals
        if number != int(number):
            symbols += 1

        if number >= 1:
            digits = floor(log10(number)) + 1
        else:
            digits = 1
        return ceil((digits + symbols) * SECTION_CHAR / 2)
