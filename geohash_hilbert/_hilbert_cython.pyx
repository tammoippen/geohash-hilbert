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


ctypedef unsigned long long ghh_uint
MAX_BITS = sizeof(ghh_uint) * 8

cdef ghh_uint cy_xy2hash_cython(ghh_uint x, ghh_uint y, const ghh_uint dim):
    cdef ghh_uint d = 0
    cdef ghh_uint lvl = dim >> 1
    cdef ghh_uint rx, ry

    while (lvl > 0):
        rx = <ghh_uint>((x & lvl) > 0)
        ry = <ghh_uint>((y & lvl) > 0)
        d += lvl * lvl * ((3 * rx) ^ ry)
        _rotate(lvl, &x, &y, rx, ry)
        lvl >>= 1
    return d

def xy2hash_cython(x: long, y: long, dim: long) -> long:
    '''Convert (x, y) to hashcode.

    Based on the implementation here:
        https://en.wikipedia.org/w/index.php?title=Hilbert_curve&oldid=797332503

    Cython implementation.

    Parameters:
        x: int        x value of point [0, dim) in dim x dim coord system
        y: int        y value of point [0, dim) in dim x dim coord system
        dim: int      Number of coding points each x, y value can take.
                      Corresponds to 2^level of the hilbert curve.

    Returns:
        int: hashcode \in [0, dim**2)
    '''
    return cy_xy2hash_cython(x, y, dim)


cdef void cy_hash2xy_cython(ghh_uint hashcode, const ghh_uint dim, ghh_uint* x, ghh_uint* y):
    cdef ghh_uint lvl = 1
    cdef ghh_uint rx, ry
    x[0] = y[0] = 0

    while (lvl < dim):
        rx = 1 & (hashcode >> 1)
        ry = 1 & (hashcode ^ rx)
        _rotate(lvl, x, y, rx, ry)
        x[0] += lvl * rx
        y[0] += lvl * ry
        hashcode >>= 2
        lvl <<= 1


cpdef hash2xy_cython(ghh_uint hashcode, const ghh_uint dim):
    '''Convert hashcode to (x, y).

    Based on the implementation here:
        https://en.wikipedia.org/w/index.php?title=Hilbert_curve&oldid=797332503

    Cython implementation.

    Parameters:
        hashcode: int  Hashcode to decode [0, dim**2)
        dim: int       Number of coding points each x, y value can take.
                       Corresponds to 2^level of the hilbert curve.

    Returns:
        Tuple[int, int]: (x, y) point in dim x dim-grid system
    '''
    cdef unsigned long long x, y
    x = y = 0

    cy_hash2xy_cython(hashcode, dim, &x, &y)

    return x, y


cdef void _rotate(ghh_uint n, ghh_uint* x, ghh_uint* y, ghh_uint rx, ghh_uint ry):
    if ry == 0:
        if rx == 1:
            x[0] = n - 1 - x[0]
            y[0] = n - 1 - y[0]
        # swap x, y
        x[0] ^= y[0]
        y[0] ^= x[0]
        x[0] ^= y[0]
