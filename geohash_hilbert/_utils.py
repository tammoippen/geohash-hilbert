# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# The MIT License
#
# Copyright (c) 2017 Tammo Ippen, tammo.ippen@posteo.de
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from ._hilbert import decode, decode_exactly, encode
from ._int2str import encode_int


def neighbours(code, bits_per_char=6):
    '''Get the neighbouring geohashes for `code`.

    Look for the north, north-east, east, south-east, south, south-west, west,
    north-west neighbours. If you are at the edge of the grid (lng \in (-180, 180),
    lat \in (-90, 90)), then it wraps around the glob and gets the corresponding neighbor.

    Parameters:
        code: str           The geohash at the center.
        bits_per_char: int  The number of bits per coding character.

    Returns:
        dict: geohashes in the neighborhood of `code`. Keys are 'north', 'north-east',
            'east', 'south-east', 'south', 'south-west', 'west', 'north-west'.
    '''
    lng, lat, lng_err, lat_err = decode_exactly(code, bits_per_char)
    precision = len(code)

    north = lat + 2 * lat_err
    if north > 90:
        north -= 180

    south = lat - 2 * lat_err
    if south < -90:
        south += 180

    east = lng + 2 * lng_err
    if east > 180:
        east -= 360

    west = lng - 2 * lng_err
    if west < -180:
        west += 360

    return {
        'north':      encode(lng,  north, precision, bits_per_char),  # noqa: E241
        'north-east': encode(east, north, precision, bits_per_char),  # noqa: E241
        'north-west': encode(west, north, precision, bits_per_char),  # noqa: E241
        'east':       encode(east, lat,   precision, bits_per_char),  # noqa: E241
        'west':       encode(west, lat,   precision, bits_per_char),  # noqa: E241
        'south':      encode(lng,  south, precision, bits_per_char),  # noqa: E241
        'south-east': encode(east, south, precision, bits_per_char),  # noqa: E241
        'south-west': encode(west, south, precision, bits_per_char),  # noqa: E241
    }


def rectangle(code, bits_per_char=6):
    '''Builds a (geojson) rectangle from `code`

    The center of the rectangle decodes as the lng/lat for code and
    the rectangle corresponds to the error-margin, i.e. every lng/lat
    point within this rectangle will be encoded as `code`, given `precision == len(code)`.

    Parameters:
        code: str           The geohash for which the rectangle should be build.
        bits_per_char: int  The number of bits per coding character.

    Returns:
        dict: geojson `Feature` containing the rectangle as a `Polygon`.
    '''
    lng, lat, lng_err, lat_err = decode_exactly(code, bits_per_char)

    return dict(
        type='Feature',
        properties=dict(
            code=code,
            lng=lng,
            lat=lat,
            lng_err=lng_err,
            lat_err=lat_err,
            bits_per_char=bits_per_char,
        ),
        bbox=(
            lng - lng_err,  # bottom left
            lat - lat_err,
            lng + lng_err,  # top right
            lat + lat_err,
        ),
        geometry=dict(
            type='Polygon',
            coordinates=[[
                (lng - lng_err, lat - lat_err),
                (lng + lng_err, lat - lat_err),
                (lng + lng_err, lat + lat_err),
                (lng - lng_err, lat + lat_err),
                (lng - lng_err, lat - lat_err),
            ]]
        )
    )


def hilbert_curve(precision, bits_per_char=6):
    '''Build the (geojson) `LineString` of the used hilbert-curve

    Builds the `LineString` of the used hilbert-curve given the `precision` and
    the `bits_per_char`. The number of bits to encode the geohash is equal to
    `precision * bits_per_char`, and for each level, you need 2 bits, hence
    the number of bits has to be even. The more bits are used, the more precise
    (and long) will the hilbert curve be, e.g. for geohashes of length 3 (precision)
    and 6 bits per character, there will be 18 bits used and the curve will
    consist of 2^18 = 262144 points.

    Parameters:
        precision: int      The number of characters in a geohash.
        bits_per_char: int  The number of bits per coding character.

    Returns:
        dict: geojson `Feature` containing the hilbert curve as a `LineString`.
    '''
    bits = precision * bits_per_char

    coords = []
    for i in range(1 << bits):
        code = encode_int(i, bits_per_char).rjust(precision, '0')
        coords += [decode(code, bits_per_char)]

    return dict(
        type='Feature',
        properties=dict(),
        geometry=dict(
            type='LineString',
            coordinates=coords
        )
    )
