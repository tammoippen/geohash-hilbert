# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from random import random

from geohash_hilbert import _hilbert as hilbert
import pytest


def rand_lng():
    return random() * 360 - 180


def rand_lat():
    return random() * 180 - 90


@pytest.mark.parametrize('bpc', (2, 4, 6))
def test_decode_empty(bpc):
    assert (0, 0) == hilbert.decode('', bits_per_char=bpc)
    assert (0, 0, 180, 90) == hilbert.decode_exactly('', bits_per_char=bpc)


@pytest.mark.parametrize('prec', range(1, 15))
@pytest.mark.parametrize('bpc', (2, 4, 6))
def test_encode_decode(bpc, prec):
    for _i in range(100):
        lng, lat = rand_lng(), rand_lat()
        code = hilbert.encode(lng, lat, precision=prec, bits_per_char=bpc)
        lng_code, lat_code, lng_err, lat_err = hilbert.decode_exactly(code, bits_per_char=bpc)

        assert lng == pytest.approx(lng_code, abs=lng_err)
        assert lat == pytest.approx(lat_code, abs=lat_err)

        assert (lng_code, lat_code) == hilbert.decode(code, bits_per_char=bpc)


@pytest.mark.parametrize('bpc', (2, 4, 6))
def test_bench_encode(benchmark, bpc):
    prec = 60 // bpc
    lng, lat = rand_lng(), rand_lat()
    benchmark(hilbert.encode, lng, lat, precision=prec, bits_per_char=bpc)


@pytest.mark.parametrize('bpc', (2, 4, 6))
def test_bench_decode(benchmark, bpc):
    prec = 60 // bpc
    lng, lat = rand_lng(), rand_lat()
    code = hilbert.encode(lng, lat, precision=prec, bits_per_char=bpc)
    benchmark(hilbert.decode_exactly, code, bits_per_char=bpc)


def test_lvl_error():
    # lvl 0 is whole world -> lng/lat error is half of max lng/lat
    assert (180, 90) == hilbert._lvl_error(0)

    # every level halves the error
    lng_err, lat_err = 180, 90
    for lvl in range(1, 30):
        lng_err /= 2
        lat_err /= 2
        assert (lng_err, lat_err) == hilbert._lvl_error(lvl)


def test_coord2int():
    # we want a dim x dim grid, i.e. we want dim cells in every direction and have coding points 0 ... dim-1
    # minimum dim is 1 => whole world in one coding point
    with pytest.raises(AssertionError):
        hilbert._coord2int(0, 0, 0)

    assert (0, 0) == hilbert._coord2int(rand_lng(), rand_lat(), 1)

    # lvl 2 is 4 cells: 2 in every direction
    assert (0, 0) == hilbert._coord2int(-180, -90, 2)
    assert (1, 0) == hilbert._coord2int(180, -90, 2)
    assert (0, 1) == hilbert._coord2int(-180, 90, 2)
    assert (1, 1) == hilbert._coord2int(180, 90, 2)

    # lvl 3 is 9 cells: 3 in every direction
    assert (0, 0) == hilbert._coord2int(-180, -90, 3)
    assert (1, 0) == hilbert._coord2int(0, -90, 3)
    assert (2, 0) == hilbert._coord2int(180, -90, 3)
    assert (0, 1) == hilbert._coord2int(-180, 0, 3)
    assert (0, 2) == hilbert._coord2int(-180, 90, 3)

    assert (1, 1) == hilbert._coord2int(0, 0, 3)
    assert (1, 2) == hilbert._coord2int(0, 90, 3)
    assert (2, 1) == hilbert._coord2int(180, 0, 3)
    assert (2, 2) == hilbert._coord2int(180, 90, 3)

    for dim in range(3, 200):
        for i in range(100):
            x, y = hilbert._coord2int(rand_lng(), rand_lat(), dim)
            assert 0 <= x < dim
            assert 0 <= y < dim


def test_int2coord():
    with pytest.raises(AssertionError):
        hilbert._int2coord(0, 0, 0)
    # we always get lower left corner of coding cell
    # only one coding cell
    assert (-180, -90) == hilbert._int2coord(0, 0, 1)

    # lvl 2 is 4 cells: 2 in every direction
    assert (-180, -90) == hilbert._int2coord(0, 0, 2)
    assert (0, -90) == hilbert._int2coord(1, 0, 2)
    assert (-180, 0) == hilbert._int2coord(0, 1, 2)
    assert (0, 0) == hilbert._int2coord(1, 1, 2)


def test_coord2int2coord():
    for lvl in range(1, 30):
        lng_err, lat_err = hilbert._lvl_error(lvl)
        dim = 1 << lvl

        for _i in range(1000):
            lng, lat = rand_lng(), rand_lat()

            x, y = hilbert._coord2int(lng, lat, dim)

            lng_x, lat_y = hilbert._int2coord(x, y, dim)

            # we always get lower left corner of coding cell
            # hence add error and then we have +- error
            assert lng == pytest.approx(lng_x + lng_err, abs=lng_err)
            assert lat == pytest.approx(lat_y + lat_err, abs=lat_err)
