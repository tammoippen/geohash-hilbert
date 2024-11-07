# The MIT License
#
# Copyright (c) 2017 - 2024 Tammo Ippen, tammo.ippen@posteo.de
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

from typing import Any, Literal

from ._hilbert import decode, decode_exactly, encode
from ._int2str import BitsPerChar, encode_int


Directions = Literal[
    "north",
    "north-east",
    "east",
    "south-east",
    "south",
    "south-west",
    "west",
    "north-west",
]


def neighbours(code: str, bits_per_char: BitsPerChar = 6) -> dict[Directions, str]:
    """Get the neighbouring geohashes for `code`.

    Look for the north, north-east, east, south-east, south, south-west, west,
    north-west neighbours. If you are at the east/west edge of the grid
    (lng ∈ (-180, 180)), then it wraps around the globe and gets the corresponding
    neighbor.

    Parameters:
        code: str           The geohash at the center.
        bits_per_char: int  The number of bits per coding character.

    Returns:
        dict: geohashes in the neighborhood of `code`. Possible keys are 'north',
            'north-east', 'east', 'south-east', 'south', 'south-west',
            'west', 'north-west'. If the input code covers the north pole, then
            keys 'north', 'north-east', and 'north-west' are not present, and if
            the input code covers the south pole then keys 'south', 'south-west',
            and 'south-east' are not present.
    """
    lng, lat, lng_err, lat_err = decode_exactly(code, bits_per_char)
    precision = len(code)

    north = lat + 2 * lat_err

    south = lat - 2 * lat_err

    east = lng + 2 * lng_err
    if east > 180:
        east -= 360

    west = lng - 2 * lng_err
    if west < -180:
        west += 360

    neighbours_dict: dict[Directions, str] = {
        "east": encode(east, lat, precision, bits_per_char),  # noqa: E241
        "west": encode(west, lat, precision, bits_per_char),  # noqa: E241
    }

    if north <= 90:  # input cell not already at the north pole
        neighbours_dict.update(
            {
                "north": encode(lng, north, precision, bits_per_char),  # noqa: E241
                "north-east": encode(east, north, precision, bits_per_char),  # noqa: E241
                "north-west": encode(west, north, precision, bits_per_char),  # noqa: E241
            }
        )

    if south >= -90:  # input cell not already at the south pole
        neighbours_dict.update(
            {
                "south": encode(lng, south, precision, bits_per_char),  # noqa: E241
                "south-east": encode(east, south, precision, bits_per_char),  # noqa: E241
                "south-west": encode(west, south, precision, bits_per_char),  # noqa: E241
            }
        )

    return neighbours_dict


def rectangle(code: str, bits_per_char: BitsPerChar = 6) -> dict[str, Any]:
    """Builds a (geojson) rectangle from `code`

    The center of the rectangle decodes as the lng/lat for code and
    the rectangle corresponds to the error-margin, i.e. every lng/lat
    point within this rectangle will be encoded as `code`, given `precision == len(code)`.

    Parameters:
        code: str           The geohash for which the rectangle should be build.
        bits_per_char: int  The number of bits per coding character.

    Returns:
        dict: geojson `Feature` containing the rectangle as a `Polygon`.
    """
    lng, lat, lng_err, lat_err = decode_exactly(code, bits_per_char)

    return {
        "type": "Feature",
        "properties": {
            "code": code,
            "lng": lng,
            "lat": lat,
            "lng_err": lng_err,
            "lat_err": lat_err,
            "bits_per_char": bits_per_char,
        },
        "bbox": (
            lng - lng_err,  # bottom left
            lat - lat_err,
            lng + lng_err,  # top right
            lat + lat_err,
        ),
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    (lng - lng_err, lat - lat_err),
                    (lng + lng_err, lat - lat_err),
                    (lng + lng_err, lat + lat_err),
                    (lng - lng_err, lat + lat_err),
                    (lng - lng_err, lat - lat_err),
                ]
            ],
        },
    }


def hilbert_curve(precision: int, bits_per_char: BitsPerChar = 6) -> dict[str, Any]:
    """Build the (geojson) `LineString` of the used hilbert-curve

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
    """
    bits = precision * bits_per_char

    coords = []
    for i in range(1 << bits):
        code = encode_int(i, bits_per_char).rjust(precision, "0")
        coords += [decode(code, bits_per_char)]

    return {
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "LineString", "coordinates": coords},
    }
