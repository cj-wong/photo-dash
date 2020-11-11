# Data Format

## Summary

The data JSON has a specific format with some options in the `"sections"` key. It always contains the name of the module (`"module"`) and title of the data (`"title"`).

For more information, view the [example.json](../resources/example.json). The example contains values similar to the accepted values. [example.jpg](../resources/example.jpg) is the rendered image equivalent of the JSON and should serve as a reference.

## Detailed Format

### "module"

This is the name of the module and should be in the format `photo-dash-module`. The format is not enforced. This only serves as the filename of the generated image.

### "title"

The title should be representative of the data, not necessarily the name of the module; it will be present, aligned left, at the top-left of the resulting image, as a header.

### "sections"

Sections are elements that fit between the header ([title](#title)) and the footer (date and time). They are created in the order they're read, aligned left, so the first sections begin near the top-left and continue down, aligned to the left border. Every section must contain a [type](#type) and [color(s)](#color). Each section is spaced vertically given the attribute `SPACER` in `photo_dash.image.DashImg`.

## Detailed Section

### "type"

The following types are valid:

- `"text"`: e.g. a sentence or heading
- `"gauge"`: two lines, representing a range/gauge (a line graph);
    - the top line contains markers that correspond to the gauge plus its value
    - the bottom line contains the gauge with each partition colored sequentially

### "color"

Colors are in the format `#RRGGBB` and will fill the element in that color.

- If the element is a gauge, `"color"` must be a list of strings, even if only 1 partition is available; the number of colors must be 1 below the number of elements in `"range"`.
- Otherwise, this must only be a string.

### "range"

**This only applies to gauge elements.** It should be a list of sorted numbers, with the minimum being the leftmost side while the maximum is the rightmost. All other numbers in the middle serve as markers and color partitions.

⚠ **Although the list can be unsorted, note that the program will sort the list destructively. This may negatively affect the color assignment per range.**

### "value"

- If the element is text, this is the text itself.
- If the element is a gauge, this represents the reading within a range. It will create a gray line within the gauge and may label the line with this value, provided that the number doesn't obscure any of the range markers. The value number will have a gray outline to indicate its relation to the gauge.
