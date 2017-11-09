geohash-hilbert
===============

[![Build Status](https://travis-ci.org/tammoippen/geohash-hilbert.svg?branch=master)](https://travis-ci.org/tammoippen/geohash-hilbert)
[![Coverage Status](https://coveralls.io/repos/github/tammoippen/geohash-hilbert/badge.svg?branch=master)](https://coveralls.io/github/tammoippen/geohash-hilbert?branch=master)
[![Tested CPython Versions](https://img.shields.io/badge/cpython-2.7%2C%203.5%2C%203.6%2C%20nightly-brightgreen.svg)](https://img.shields.io/badge/cpython-2.7%2C%203.5%2C%203.6%2C%20nightly-brightgreen.svg)
[![Tested PyPy Versions](https://img.shields.io/badge/pypy-2.7--5.8.0%2C%203.5--5.8.0-brightgreen.svg)](https://img.shields.io/badge/pypy-2.7--5.8.0%2C%203.5--5.8.0-brightgreen.svg)
[![PyPi version](https://img.shields.io/pypi/v/geohash-hilbert.svg)](https://pypi.python.org/pypi/geohash-hilbert)
[![PyPi license](https://img.shields.io/pypi/l/geohash-hilbert.svg)](https://pypi.python.org/pypi/geohash-hilbert)

Geohash a lng/lat coordinate using hilbert space filling curves.

```python
In [1]: import geohash_hilbert as ghh

In [2]: ghh.encode(6.957036, 50.941291)
Out[2]: 'Z7fe2GaIVO'

In [3]: ghh.decode('Z7fe2GaIVO')
Out[3]: (6.957036126405001, 50.941291032359004)

In [4]: ghh.decode_exactly('Z7fe2GaIVO')
Out[4]:
(6.957036126405001, 50.941291032359004,          # position
 1.6763806343078613e-07, 8.381903171539307e-08)  # errors

In [5]: ghh.encode?
Signature: ghh.encode(lng, lat, precision=10, bits_per_char=6)
Docstring:
Encode a lng/lat position as a geohash using a hilbert curve

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
File:      .../geohash_hilbert/_hilbert.py
Type:      function


In [7]: ghh.decode?
Signature: ghh.decode(code, bits_per_char=6)
Docstring:
Decode a geohash on a hilbert curve as a lng/lat position

Decodes the geohash `code` as a lng/lat position. It assumes, that
the length of `code` corresponds to the precision! And that each character
in `code` encodes `bits_per_char` bits. Do not mix geohashes with different
`bits_per_char`!

Parameters:
    code: str           The geohash to decode.
    bits_per_char: int  The number of bits per coding character

Returns:
    Tuple[float, float]:  (lng, lat) coordinate for the geohash.
File:      .../geohash_hilbert/_hilbert.py
Type:      function


In [8]: ghh.decode_exactly?
Signature: ghh.decode_exactly(code, bits_per_char=6)
Docstring:
Decode a geohash on a hilbert curve as a lng/lat position with error-margins

Decodes the geohash `code` as a lng/lat position with error-margins. It assumes,
that the length of `code` corresponds to the precision! And that each character
in `code` encodes `bits_per_char` bits. Do not mix geohashes with different
`bits_per_char`!

Parameters:
    code: str           The geohash to decode.
    bits_per_char: int  The number of bits per coding character

Returns:
    Tuple[float, float, float, float]:  (lng, lat, lng-error, lat-error) coordinate for the geohash.
File:      .../geohash_hilbert/_hilbert.py
Type:      function
```

Compare to original [geohash](https://github.com/vinsci/geohash/)
-------------------------------------------------------------------

This package is similar to the [geohash](https://github.com/vinsci/geohash/) or the [geohash2](https://github.com/dbarthe/geohash/) package, as it also provides a mechanism to encode (and decode) a longitude/latitude position (WGS 84) to a one dimensional [geohash](https://en.wikipedia.org/wiki/Geohash). But, where the former use [z-order](https://en.wikipedia.org/wiki/Z-order_curve) space filling curves, this package uses [hilbert](https://en.wikipedia.org/wiki/Hilbert_curve) curves. (The kernel for this package was adapted from [wiki](https://en.wikipedia.org/wiki/Hilbert_curve)).

**Note**: The parameter (and returns) order changed from lat/lng in `geohash` to lng/lat. Apart from that this package is a drop-in replacement for the original `geohash`.

Further, the string representation is changed (and modifieable) to compensate for the special requirements of the implementation: `geohash` uses a modified base32 representation, i.e. every character in the geohash encodes 5 bits. Even bits encode longitude and odd bits encode latitude. Every two full bits encode for one level of the z-order curve, e.g. the default precision of 12 use `12*5 = 60bit` to encode one latitude / longitude position using a level 30 z-order curve. The implementation also allows for 'half'-levels, e.g. precision 11 use `11*5 = 55bit` corresponds to a level 27.5 z-order curve.

Geohash representation details
------------------------------

This implementation of the hilbert curve allows only full levels, hence we have
support for base4 (2bit), base16 (4bit) and a custom base64 (6bit, the default)
geohash representations.
All keep the same ordering as their integer value by lexicographical order:

- base4: each character is in `'0123'`
- base16: each character is in `'0123456789abcdef'`
- base64: each character is in `'0123456789@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'`

**Note**: Do not mix geohashes from the original `geohash` and this, and do not mix base4, base16 and base64 geohash representations. Decide for one representation and then stick to it.

The different encodings also give a more fine grain control of the actual encoding precision and the geohash size (maximum lng/lat error around equator):

```
lvl | bits |   error       |    base4   |  base16  |  base64
-------------------------------------------------------------
  0 |   0  |  20015.087 km |   prec  0  |  prec 0  |  prec 0
  1 |   2  |  10007.543 km |   prec  1  |          |
  2 |   4  |   5003.772 km |   prec  2  |  prec 1  |
  3 |   6  |   2501.886 km |   prec  3  |          |  prec 1
  4 |   8  |   1250.943 km |   prec  4  |  prec 2  |
  5 |  10  |    625.471 km |   prec  5  |          |
  6 |  12  |    312.736 km |   prec  6  |  prec 3  |  prec 2
  7 |  14  |    156.368 km |   prec  7  |          |
  8 |  16  |     78.184 km |   prec  8  |  prec 4  |
  9 |  18  |     39.092 km |   prec  9  |          |  prec 3
 10 |  20  |     19.546 km |   prec 10  |  prec 5  |
 11 |  22  |   9772.992  m |   prec 11  |          |
 12 |  24  |   4886.496  m |   prec 12  |  prec  6 |  prec 4
 13 |  26  |   2443.248  m |   prec 13  |          |
 14 |  28  |   1221.624  m |   prec 14  |  prec  7 |
 15 |  30  |    610.812  m |   prec 15  |          |  prec 5
 16 |  32  |    305.406  m |   prec 16  |  prec  8 |
 17 |  34  |    152.703  m |   prec 17  |          |
 18 |  36  |     76.351  m |   prec 18  |  prec  9 |  prec 6
 19 |  38  |     38.176  m |   prec 19  |          |
 20 |  40  |     19.088  m |   prec 20  |  prec 10 |
 21 |  42  |    954.394 cm |   prec 21  |          |  prec 7
 22 |  44  |    477.197 cm |   prec 22  |  prec 11 |
 23 |  46  |    238.598 cm |   prec 23  |          |
 24 |  48  |    119.299 cm |   prec 24  |  prec 12 |  prec 8
 25 |  50  |     59.650 cm |   prec 25  |          |
 26 |  52  |     29.825 cm |   prec 26  |  prec 13 |
 27 |  54  |     14.912 cm |   prec 27  |          |  prec 9
 28 |  56  |      7.456 cm |   prec 28  |  prec 14 |
 29 |  58  |      3.728 cm |   prec 29  |          |
 30 |  60  |      1.864 cm |   prec 30  |  prec 15 |  prec 10
 31 |  62  |      0.932 cm |   prec 31  |          |
 32 |  64  |      0.466 cm |   prec 32  |  prec 16 |
 -------------------------------------------------------------
```

Further features
----------------

If cython is available during install, the cython kernel extension will be installed and used for geohash computations with 64bit or less (timings for MBP 2016, 2.6 GHz Intel Core i7, Python 3.6.2, Cython 0.26.1):

```python
In [1]: import geohash_hilbert as ghh
# Without cython ...
In [2]: ghh._hilbert.CYTHON_AVAILABLE
Out[2]: False

In [3]: %timeit ghh.encode(6.957036, 50.941291, precision=10)
39.4 µs ± 614 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)

In [4]: %timeit ghh.encode(6.957036, 50.941291, precision=11)
43.4 µs ± 421 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
```

```python
In [1]: import geohash_hilbert as ghh
# With cython ...
In [2]: ghh._hilbert.CYTHON_AVAILABLE
Out[2]: True
# almost 6x faster
In [3]: %timeit ghh.encode(6.957036, 50.941291, precision=10)
6.72 µs ± 57.4 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
# more than 64bit will be computed with pure python function.
In [4]: %timeit ghh.encode(6.957036, 50.941291, precision=11)
43.4 µs ± 375 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
```

Get the actual rectangle that is encoded by a geohash, i.e. position +- errors:

```python
# returns a geojson Feature encoding the rectangle as a Polygon
In [9]: ghh.rectangle('Z7fe2G')
Out[9]:
{'bbox': (6.955718994140625,
  50.94085693359375,
  6.95709228515625,
  50.94154357910156),
 'geometry': {'coordinates': [[(6.955718994140625, 50.94085693359375),
    (6.955718994140625, 50.94154357910156),
    (6.95709228515625, 50.94154357910156),
    (6.95709228515625, 50.94085693359375),
    (6.955718994140625, 50.94085693359375)]],
  'type': 'Polygon'},
 'properties': {'bits_per_char': 6,
  'code': 'Z7fe2G',
  'lat': 50.941200256347656,
  'lat_err': 0.00034332275390625,
  'lng': 6.9564056396484375,
  'lng_err': 0.0006866455078125},
 'type': 'Feature'}
```

[![](https://github.com/tammoippen/geohash-hilbert/raw/master/img/rectangle.png)](http://geojson.io/#data=data:application/json,%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2G%22%2C%22lng%22%3A6.9564056396484375%2C%22lat%22%3A50.941200256347656%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.955718994140625%2C50.94085693359375%2C6.95709228515625%2C50.94154357910156%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.955718994140625%2C50.94085693359375%5D%2C%5B6.955718994140625%2C50.94154357910156%5D%2C%5B6.95709228515625%2C50.94154357910156%5D%2C%5B6.95709228515625%2C50.94085693359375%5D%2C%5B6.955718994140625%2C50.94085693359375%5D%5D%5D%7D%7D)

Get the neighbouring geohashes:

```python
In [10]: ghh.neighbours('Z7fe2G')
Out[10]:
{'east': 'Z7fe2T',
 'north': 'Z7fe2H',
 'north-east': 'Z7fe2S',
 'north-west': 'Z7fe2I',
 'south': 'Z7fe2B',
 'south-east': 'Z7fe2A',
 'south-west': 'Z7fe2E',
 'west': 'Z7fe2F'}
```
[![](https://github.com/tammoippen/geohash-hilbert/raw/master/img/neighbors.png)](http://geojson.io/#data=data:application/json,%5B%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2H%22%2C%22lng%22%3A6.9564056396484375%2C%22lat%22%3A50.94188690185547%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.955718994140625%2C50.94154357910156%2C6.95709228515625%2C50.942230224609375%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.955718994140625%2C50.94154357910156%5D%2C%5B6.955718994140625%2C50.942230224609375%5D%2C%5B6.95709228515625%2C50.942230224609375%5D%2C%5B6.95709228515625%2C50.94154357910156%5D%2C%5B6.955718994140625%2C50.94154357910156%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2S%22%2C%22lng%22%3A6.9577789306640625%2C%22lat%22%3A50.94188690185547%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.95709228515625%2C50.94154357910156%2C6.958465576171875%2C50.942230224609375%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.95709228515625%2C50.94154357910156%5D%2C%5B6.95709228515625%2C50.942230224609375%5D%2C%5B6.958465576171875%2C50.942230224609375%5D%2C%5B6.958465576171875%2C50.94154357910156%5D%2C%5B6.95709228515625%2C50.94154357910156%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2I%22%2C%22lng%22%3A6.9550323486328125%2C%22lat%22%3A50.94188690185547%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.954345703125%2C50.94154357910156%2C6.955718994140625%2C50.942230224609375%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.954345703125%2C50.94154357910156%5D%2C%5B6.954345703125%2C50.942230224609375%5D%2C%5B6.955718994140625%2C50.942230224609375%5D%2C%5B6.955718994140625%2C50.94154357910156%5D%2C%5B6.954345703125%2C50.94154357910156%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2T%22%2C%22lng%22%3A6.9577789306640625%2C%22lat%22%3A50.941200256347656%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.95709228515625%2C50.94085693359375%2C6.958465576171875%2C50.94154357910156%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.95709228515625%2C50.94085693359375%5D%2C%5B6.95709228515625%2C50.94154357910156%5D%2C%5B6.958465576171875%2C50.94154357910156%5D%2C%5B6.958465576171875%2C50.94085693359375%5D%2C%5B6.95709228515625%2C50.94085693359375%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2F%22%2C%22lng%22%3A6.9550323486328125%2C%22lat%22%3A50.941200256347656%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.954345703125%2C50.94085693359375%2C6.955718994140625%2C50.94154357910156%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.954345703125%2C50.94085693359375%5D%2C%5B6.954345703125%2C50.94154357910156%5D%2C%5B6.955718994140625%2C50.94154357910156%5D%2C%5B6.955718994140625%2C50.94085693359375%5D%2C%5B6.954345703125%2C50.94085693359375%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2B%22%2C%22lng%22%3A6.9564056396484375%2C%22lat%22%3A50.940513610839844%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.955718994140625%2C50.94017028808594%2C6.95709228515625%2C50.94085693359375%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.955718994140625%2C50.94017028808594%5D%2C%5B6.955718994140625%2C50.94085693359375%5D%2C%5B6.95709228515625%2C50.94085693359375%5D%2C%5B6.95709228515625%2C50.94017028808594%5D%2C%5B6.955718994140625%2C50.94017028808594%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2A%22%2C%22lng%22%3A6.9577789306640625%2C%22lat%22%3A50.940513610839844%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.95709228515625%2C50.94017028808594%2C6.958465576171875%2C50.94085693359375%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.95709228515625%2C50.94017028808594%5D%2C%5B6.95709228515625%2C50.94085693359375%5D%2C%5B6.958465576171875%2C50.94085693359375%5D%2C%5B6.958465576171875%2C50.94017028808594%5D%2C%5B6.95709228515625%2C50.94017028808594%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2E%22%2C%22lng%22%3A6.9550323486328125%2C%22lat%22%3A50.940513610839844%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.954345703125%2C50.94017028808594%2C6.955718994140625%2C50.94085693359375%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.954345703125%2C50.94017028808594%5D%2C%5B6.954345703125%2C50.94085693359375%5D%2C%5B6.955718994140625%2C50.94085693359375%5D%2C%5B6.955718994140625%2C50.94017028808594%5D%2C%5B6.954345703125%2C50.94017028808594%5D%5D%5D%7D%7D%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22code%22%3A%22Z7fe2G%22%2C%22lng%22%3A6.9564056396484375%2C%22lat%22%3A50.941200256347656%2C%22lng_err%22%3A0.0006866455078125%2C%22lat_err%22%3A0.00034332275390625%2C%22bits_per_char%22%3A6%7D%2C%22bbox%22%3A%5B6.955718994140625%2C50.94085693359375%2C6.95709228515625%2C50.94154357910156%5D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B6.955718994140625%2C50.94085693359375%5D%2C%5B6.955718994140625%2C50.94154357910156%5D%2C%5B6.95709228515625%2C50.94154357910156%5D%2C%5B6.95709228515625%2C50.94085693359375%5D%2C%5B6.955718994140625%2C50.94085693359375%5D%5D%5D%7D%7D%5D)

Plot the Hilbert curve:

```python
# returns a geojson Feature encoding the Hilbert curve as a LineString
In [11]: ghh.hilbert_curve(1)  # this is a level 3 Hilbert curve:
                               # 1 char * 6 bits/char = 6 bits => level 3
Out[11]:
{'geometry': {'coordinates': [(-157.5, -78.75),
   (-157.5, -56.25), (-112.5, -56.25), (-112.5, -78.75), (-67.5, -78.75), (-22.5, -78.75),
   (-22.5, -56.25), (-67.5, -56.25), (-67.5, -33.75), (-22.5, -33.75), (-22.5, -11.25),
   (-67.5, -11.25), (-112.5, -11.25), (-112.5, -33.75), (-157.5, -33.75), (-157.5, -11.25),
   (-157.5, 11.25), (-112.5, 11.25), (-112.5, 33.75), (-157.5, 33.75), (-157.5, 56.25),
   (-157.5, 78.75), (-112.5, 78.75), (-112.5, 56.25), (-67.5, 56.25), (-67.5, 78.75),
   (-22.5, 78.75), (-22.5, 56.25), (-22.5, 33.75), (-67.5, 33.75), (-67.5, 11.25),
   (-22.5, 11.25), (22.5, 11.25), (67.5, 11.25), (67.5, 33.75), (22.5, 33.75), (22.5, 56.25),
   (22.5, 78.75), (67.5, 78.75), (67.5, 56.25), (112.5, 56.25), (112.5, 78.75), (157.5, 78.75),
   (157.5, 56.25), (157.5, 33.75), (112.5, 33.75), (112.5, 11.25), (157.5, 11.25), (157.5, -11.25),
   (157.5, -33.75), (112.5, -33.75), (112.5, -11.25), (67.5, -11.25), (22.5, -11.25),
   (22.5, -33.75), (67.5, -33.75), (67.5, -56.25), (22.5, -56.25), (22.5, -78.75),
   (67.5, -78.75), (112.5, -78.75), (112.5, -56.25), (157.5, -56.25), (157.5, -78.75)],
  'type': 'LineString'},
 'properties': {},
 'type': 'Feature'}
```
[![](https://github.com/tammoippen/geohash-hilbert/raw/master/img/hilbert.png)](http://geojson.io/#data=data:application/json,%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%7D%2C%22geometry%22%3A%7B%22type%22%3A%22LineString%22%2C%22coordinates%22%3A%5B%5B-157.5%2C-78.75%5D%2C%5B-157.5%2C-56.25%5D%2C%5B-112.5%2C-56.25%5D%2C%5B-112.5%2C-78.75%5D%2C%5B-67.5%2C-78.75%5D%2C%5B-22.5%2C-78.75%5D%2C%5B-22.5%2C-56.25%5D%2C%5B-67.5%2C-56.25%5D%2C%5B-67.5%2C-33.75%5D%2C%5B-22.5%2C-33.75%5D%2C%5B-22.5%2C-11.25%5D%2C%5B-67.5%2C-11.25%5D%2C%5B-112.5%2C-11.25%5D%2C%5B-112.5%2C-33.75%5D%2C%5B-157.5%2C-33.75%5D%2C%5B-157.5%2C-11.25%5D%2C%5B-157.5%2C11.25%5D%2C%5B-112.5%2C11.25%5D%2C%5B-112.5%2C33.75%5D%2C%5B-157.5%2C33.75%5D%2C%5B-157.5%2C56.25%5D%2C%5B-157.5%2C78.75%5D%2C%5B-112.5%2C78.75%5D%2C%5B-112.5%2C56.25%5D%2C%5B-67.5%2C56.25%5D%2C%5B-67.5%2C78.75%5D%2C%5B-22.5%2C78.75%5D%2C%5B-22.5%2C56.25%5D%2C%5B-22.5%2C33.75%5D%2C%5B-67.5%2C33.75%5D%2C%5B-67.5%2C11.25%5D%2C%5B-22.5%2C11.25%5D%2C%5B22.5%2C11.25%5D%2C%5B67.5%2C11.25%5D%2C%5B67.5%2C33.75%5D%2C%5B22.5%2C33.75%5D%2C%5B22.5%2C56.25%5D%2C%5B22.5%2C78.75%5D%2C%5B67.5%2C78.75%5D%2C%5B67.5%2C56.25%5D%2C%5B112.5%2C56.25%5D%2C%5B112.5%2C78.75%5D%2C%5B157.5%2C78.75%5D%2C%5B157.5%2C56.25%5D%2C%5B157.5%2C33.75%5D%2C%5B112.5%2C33.75%5D%2C%5B112.5%2C11.25%5D%2C%5B157.5%2C11.25%5D%2C%5B157.5%2C-11.25%5D%2C%5B157.5%2C-33.75%5D%2C%5B112.5%2C-33.75%5D%2C%5B112.5%2C-11.25%5D%2C%5B67.5%2C-11.25%5D%2C%5B22.5%2C-11.25%5D%2C%5B22.5%2C-33.75%5D%2C%5B67.5%2C-33.75%5D%2C%5B67.5%2C-56.25%5D%2C%5B22.5%2C-56.25%5D%2C%5B22.5%2C-78.75%5D%2C%5B67.5%2C-78.75%5D%2C%5B112.5%2C-78.75%5D%2C%5B112.5%2C-56.25%5D%2C%5B157.5%2C-56.25%5D%2C%5B157.5%2C-78.75%5D%5D%7D%7D)
