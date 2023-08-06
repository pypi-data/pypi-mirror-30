larpix-geometry
===============

Handle pixel and TPC geometry for LArPix

Overview
---------

Pixel geometry and channel assignments are stored in YAML configuration
files. pixelplane.py will read a configuration file and allow easy
access to channel-to-(x,y) conversion and other convenient
relationships.

patterngenerator.py contains code for generating arbitrary
configurations of pixel planes. Individual python scripts are needed per
pixel/chip geometry.

draw_plane.py reads in a YAML configuration file and draws the pixel
plane and channel connections in a PDF file for easy visual inspection
and reference.

Usage
---------

The scripts can be executed with no arguments.

Here is how to use the pixelplane module.

```python
from pixelplane import *
import yaml

with open('pixel_geometry.yaml', 'r') as f:
    board = PixelPlane.fromDict(yaml.load(f))

chipids = list(board.chips.keys())
chip0 = board.chips[chipids[0]]
print('Retrieving %d' % chip0.chipid)
# print list of (x, y) for each channel
print('Channel ID |     Position\n-----------|-------------')
for channel, pixel in enumerate(chip0.channel_connections):
    print('  %02d       | (%.1f, %.1f)' % (channel, pixel.x, pixel.y))

# Find which channel corresponds to pixel 100
pixel100 = board.pixels[100]
chip, channel = pixel100.channel_connection
print('Pixel 100 is connected to chip %d, channel %d' %
        (chip.chipid, channel))

# Find which channels correspond to pixels with x locations greater than 100
connection_list = board.channels_where(lambda pixel:pixel.x > 100)
for chip, channel in connection_list:
    print('Chip %d, channel %d' % (chip.chipid, channel))
```
