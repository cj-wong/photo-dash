# Data Format

## Summary

The data JSON has a specific format with some options in the `"sections"` key. It always contains the name of the module (`"module"`) and title of the data (`"title"`).

For more information, view the [example.json](resources/example.json). The example contains values similar to the accepted values. [example.jpg](resources/example.jpg) is the rendered image equivalent of the JSON and should serve as a reference.

## Detailed Format

### "module"

This value should be in the format `photo-dash-module`.

### "title"

This value should represent the title of the data, not necessarily the name of the module. The title will be present at the top-left of the resulting image.

### "sections"

This should contain all sections (elements) of the image as desired. Sections are created in the order they're read, so first sections begin near the top-left and continue down, aligned to the left border.

## Detailed Section

### "type"

This can be `"text"` (e.g. a sentence or heading) or `"gauge"` (a horizontal bar with a marker).

### "color"

This is in the format `#RRGGBB` and will fill the element in that color.

- If the element is a gauge, `"color"` can be a list of strings; the number of strings must be 1 below the number of elements in `"range"`.
- Otherwise, this must only be a string.

### "range"

**This only applies to gauge elements.** It should be a list of sorted numbers, with the minimum being the leftmost side while the maximum is the rightmost. All other numbers in the middle serve as markers and color partitions.

⚠ **Although the list can be unsorted, note that the program will sort the list destructively. This may negatively affect the color assignment per range.**

### "value"

**This only applies to gauge elements.** It represents the reading within a range. It will create a gray line within the gauge and may label the line with this value, provided that the number doesn't obscure any of the range markers. The value number will have a gray outline to indicate its relation to the gauge.
