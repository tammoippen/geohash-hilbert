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

from math import floor

from ._int2str import decode_int, encode_int

try:
    from geohash_hilbert._hilbert_cython import hash2xy_cython, MAX_BITS, xy2hash_cython
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False


_LAT_INTERVAL = (-90.0, 90.0)
_LNG_INTERVAL = (-180.0, 180.0)


def encode(lng, lat, precision=10, bits_per_char=6):
    '''Encode a lng/lat position as a geohash using a hilbert curve

    This function encodes a lng/lat coordinate to a geohash of length `precision`
    on a corresponding a hilbert curve. Each character encodes `bits_per_char` bits
    per character (allowed are 2, 4 and 6 bits [default 6]). Hence, the geohash encodes
    the lng/lat coordinate using `precision` * `bits_per_char` bits. The number of
    bits devided by 2 give the level of the used hilbert curve, e.g. precision=10, bits_per_char=6
    (default values) use 60 bit and a level 30 hilbert curve to map the globe.

    Parameters:
        lng: float          Longitude; between -180.0 and 180.0; WGS 84
        lat: float          Latitude; between -90.0 and 90.0; WGS 84
        precision: int      The number of characters in a geohash
        bits_per_char: int  The number of bits per coding character

    Returns:
        str: geohash for lng/lat of length `precision`
    '''
    assert _LNG_INTERVAL[0] <= lng <= _LNG_INTERVAL[1]
    assert _LAT_INTERVAL[0] <= lat <= _LAT_INTERVAL[1]
    assert precision > 0
    assert bits_per_char in (2, 4, 6)

    bits = precision * bits_per_char
    level = bits >> 1
    dim = 1 << level

    x, y = _coord2int(lng, lat, dim)

    if CYTHON_AVAILABLE and bits <= MAX_BITS:
        code = xy2hash_cython(x, y, dim)
    else:
        code = _xy2hash(x, y, dim)

    return encode_int(code, bits_per_char).rjust(precision, '0')


def decode(code, bits_per_char=6):
    '''Decode a geohash on a hilbert curve as a lng/lat position

    Decodes the geohash `code` as a lng/lat position. It assumes, that
    the length of `code` corresponds to the precision! And that each character
    in `code` encodes `bits_per_char` bits. Do not mix geohashes with different
    `bits_per_char`!

    Parameters:
        code: str           The geohash to decode.
        bits_per_char: int  The number of bits per coding character

    Returns:
        Tuple[float, float]:  (lng, lat) coordinate for the geohash.
    '''
    assert bits_per_char in (2, 4, 6)

    if len(code) == 0:
        return 0., 0.

    lng, lat, _lng_err, _lat_err = decode_exactly(code, bits_per_char)
    return lng, lat


def decode_exactly(code, bits_per_char=6):
    '''Decode a geohash on a hilbert curve as a lng/lat position with error-margins

    Decodes the geohash `code` as a lng/lat position with error-margins. It assumes,
    that the length of `code` corresponds to the precision! And that each character
    in `code` encodes `bits_per_char` bits. Do not mix geohashes with different
    `bits_per_char`!

    Parameters:
        code: str           The geohash to decode.
        bits_per_char: int  The number of bits per coding character

    Returns:
        Tuple[float, float, float, float]:  (lng, lat, lng-error, lat-error) coordinate for the geohash.
    '''
    assert bits_per_char in (2, 4, 6)

    if len(code) == 0:
        return 0., 0., _LNG_INTERVAL[1], _LAT_INTERVAL[1]

    bits = len(code) * bits_per_char
    level = bits >> 1
    dim = 1 << level

    code_int = decode_int(code, bits_per_char)
    if CYTHON_AVAILABLE and bits <= MAX_BITS:
        x, y = hash2xy_cython(code_int, dim)
    else:
        x, y = _hash2xy(code_int, dim)

    lng, lat = _int2coord(x, y, dim)
    lng_err, lat_err = _lvl_error(level)  # level of hilbert curve is bits / 2

    return lng + lng_err, lat + lat_err, lng_err, lat_err


def _lvl_error(level):
    '''Get the lng/lat error for the hilbert curve with the given level

    On every level, the error of the hilbert curve is halved, e.g.
    - level 0 has lng error of +-180 (only one coding point is available: (0, 0))
    - on level 1, there are 4 coding points: (-90, -45), (90, -45), (-90, 45), (90, 45)
      hence the lng error is +-90

    Parameters:
        level: int  Level of the used hilbert curve

    Returns:
        Tuple[float, float]: (lng-error, lat-error) for the given level
    '''
    error = 1 / (1 << level)
    return 180 * error, 90 * error


def _coord2int(lng, lat, dim):
    '''Convert lon, lat values into a dim x dim-grid coordinate system.

    Parameters:
        lng: float    Longitude value of coordinate (-180.0, 180.0); corresponds to X axis
        lat: float    Latitude value of coordinate (-90.0, 90.0); corresponds to Y axis
        dim: int      Number of coding points each x, y value can take.
                      Corresponds to 2^level of the hilbert curve.

    Returns:
        Tuple[int, int]:
            Lower left corner of corresponding dim x dim-grid box
              x      x value of point [0, dim); corresponds to longitude
              y      y value of point [0, dim); corresponds to latitude
    '''
    assert dim >= 1

    lat_y = (lat + _LAT_INTERVAL[1]) / 180.0 * dim   # [0 ... dim)
    lng_x = (lng + _LNG_INTERVAL[1]) / 360.0 * dim  # [0 ... dim)

    return min(dim - 1, int(floor(lng_x))), min(dim - 1, int(floor(lat_y)))


def _int2coord(x, y, dim):
    '''Convert x, y values in dim x dim-grid coordinate system into lng, lat values.

    Parameters:
        x: int        x value of point [0, dim); corresponds to longitude
        y: int        y value of point [0, dim); corresponds to latitude
        dim: int      Number of coding points each x, y value can take.
                      Corresponds to 2^level of the hilbert curve.

    Returns:
        Tuple[float, float]: (lng, lat)
            lng    longitude value of coordinate [-180.0, 180.0]; corresponds to X axis
            lat    latitude value of coordinate [-90.0, 90.0]; corresponds to Y axis
    '''
    assert dim >= 1
    assert x < dim
    assert y < dim

    lng = x / dim * 360 - 180
    lat = y / dim * 180 - 90

    return lng, lat


# only use python versions, when cython is not available
def _xy2hash(x, y, dim):
    '''Convert (x, y) to hashcode.

    Based on the implementation here:
        https://en.wikipedia.org/w/index.php?title=Hilbert_curve&oldid=797332503

    Pure python implementation.

    Parameters:
        x: int        x value of point [0, dim) in dim x dim coord system
        y: int        y value of point [0, dim) in dim x dim coord system
        dim: int      Number of coding points each x, y value can take.
                      Corresponds to 2^level of the hilbert curve.

    Returns:
        int: hashcode \in [0, dim**2)
    '''
    d = 0
    lvl = dim >> 1
    while (lvl > 0):
        rx = int((x & lvl) > 0)
        ry = int((y & lvl) > 0)
        d += lvl * lvl * ((3 * rx) ^ ry)
        x, y = _rotate(lvl, x, y, rx, ry)
        lvl >>= 1
    return d


def _hash2xy(hashcode, dim):
    '''Convert hashcode to (x, y).

    Based on the implementation here:
        https://en.wikipedia.org/w/index.php?title=Hilbert_curve&oldid=797332503

    Pure python implementation.

    Parameters:
        hashcode: int  Hashcode to decode [0, dim**2)
        dim: int       Number of coding points each x, y value can take.
                       Corresponds to 2^level of the hilbert curve.

    Returns:
        Tuple[int, int]: (x, y) point in dim x dim-grid system
    '''
    assert(hashcode <= dim * dim - 1)
    x = y = 0
    lvl = 1
    while (lvl < dim):
        rx = 1 & (hashcode >> 1)
        ry = 1 & (hashcode ^ rx)
        x, y = _rotate(lvl, x, y, rx, ry)
        x += lvl * rx
        y += lvl * ry
        hashcode >>= 2
        lvl <<= 1
    return x, y


def _rotate(n, x, y, rx, ry):
    '''Rotate and flip a quadrant appropriately

    Based on the implementation here:
        https://en.wikipedia.org/w/index.php?title=Hilbert_curve&oldid=797332503

    '''
    if ry == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        return y, x
    return x, y
