'''
Generate pixel plane patterns.

'''

from itertools import product
import numpy as np

def pixels_plain_grid(pixel_pitch, nblocksx, nblocksy, startx, starty, start_index):
    '''
    A plain grid of no-pad no-focus pixels, numbered in batches of 4x4.

    '''
    pixels = []
    pixels_per_grid = 16
    repetition_period = 4*pixel_pitch
    x, y, = np.meshgrid(pixel_pitch*np.arange(4),
            pixel_pitch*np.arange(4))
    subgrid = np.array(list(zip(x.reshape(-1), y.reshape(-1))))
    # This line forms the list of blocks going along rows. Without this
    # nonsense (just using product(range, range) goes down columns).
    blocklist = np.array(list(product(range(nblocksy), range(nblocksx))))[:, ::-1]
    for block_index, (xblock, yblock) in enumerate(blocklist):
        pixelids = range(block_index*pixels_per_grid + start_index,
                (block_index+1)*pixels_per_grid + start_index)
        offset = np.array([xblock*repetition_period + startx,
            yblock*repetition_period + starty])
        pixel_locations = subgrid + offset
        for pixelid, (x, y) in zip(pixelids, pixel_locations):
            pixels.append([pixelid, float(x), float(y), [], []])
    return pixels

def pixels_triangle_grid(repetition_period, nblocksx, nblocksy, startx,
        starty, start_index):
    '''
    A grid of triangle pixels specific to the LArPix sensor board.

    '''
    pixels = []
    unit = repetition_period / 8.0
    subgrid = np.array(  # Laid out here in the orientation on the board
              [[2*unit, unit],                [6*unit, unit],
        [unit, 2*unit], [3*unit, 2*unit], [5*unit, 2*unit], [7*unit, 2*unit],
               [2*unit, 10/3.*unit],          [6*unit, 10/3.*unit],
               [2*unit, 14/3.*unit],          [6*unit, 14/3.*unit],
        [unit, 6*unit], [3*unit, 6*unit], [5*unit, 6*unit], [7*unit, 6*unit],
               [2*unit, 7*unit],              [6*unit, 7*unit]])
    pixels_per_grid = len(subgrid)
    # This line forms the list of blocks going along rows. Without this
    # nonsense (just using product(range, range) goes down columns).
    blocklist = np.array(list(product(range(nblocksy), range(nblocksx))))[:, ::-1]
    for block_index, (xblock, yblock) in enumerate(blocklist):
        pixelids = range(block_index*pixels_per_grid + start_index,
                (block_index+1)*pixels_per_grid + start_index)
        offset = np.array([xblock*repetition_period + startx,
            yblock*repetition_period + starty])
        pixel_locations = subgrid + offset
        for pixelid, (x, y) in zip(pixelids, pixel_locations):
            pixels.append([pixelid, float(x), float(y), [], []])
    return pixels

grid_4x4_assignments = [14, 13, 15, 12, 10, 9, 11, 8, 7, 4, 6, 5, 3, 0, 2, 1]
'''
Index in flattened ``pixelids`` list (from the chip side)::

0  1  2  3
4  5  6  7
8  9  10 11
12 13 14 15

Channel assignments (right side up) (from the chip side)::

13 15 14 12     29 31 30 28
9  11 10 8  or  25 27 26 24
7  5  4  6      23 21 20 22
3  1  0  2      19 17 16 18

'''

triangle_assignments = [15, 14, 12, 11, 13, 10, 9, 8, 7, 6, 5, 2, 4, 3, 1, 0]
'''
Index in flattened ``pixelids`` list (from the chip side)::

   0           1
2     3     4     5
   6           7
   8           9
10    11    12    13
   14          15

Channel assignments (right-side up) (from the chip side)::

   15          14              31          30
11    13    12    10        27    29    28    26
   9           8       or      25          24
   7           6               23          22
5     3     2     4         21    19    18    20
   1           0               17          16

'''

def assign_pixels(pixelids, assignments, right_side_up=True):
    '''
    Return a list assigning the given pixelids to a chip's channels
    using the provided assignment array.

    The right-side up configuration (``right_side_up=True``) of the chip
    is (viewed from above), channels 0-15 on the left and channels 16-31
    on the right. The upside-down configuration is reversed: channels
    16-31 on the left, and channels 0-15 on the right.

    Since the convention is that channel id is given by position in the
    list, this function always returns assignments to channels 0-15.
    If the given grid should be assigned to channels 16-31, just
    concatenate it with the assignments for 0-15.

    ``assignments[i]`` gives the index in the final list of
    ``pixelids[i]``.

    '''
    if not right_side_up:
        assignments = assignments[::-1]
    channel_connections = []
    for channel_id, pixelid in enumerate(pixelids):
        channel_connections.append(pixelids[assignments[channel_id]])
    return channel_connections
