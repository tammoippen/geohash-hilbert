# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from random import random

import pytest

from geohash_hilbert import _utils as utils
from geohash_hilbert import decode_exactly, encode
from geohash_hilbert._int2str import decode_int


def rand_lng():
    return random() * 360 - 180


def rand_lat():
    return random() * 180 - 90


@pytest.mark.parametrize('bpc', (2, 4, 6))
@pytest.mark.parametrize('prec', range(2, 7))
def test_neighbours(bpc, prec):
    for _i in range(100):
        code = encode(rand_lng(), rand_lat(), bits_per_char=bpc, precision=prec)
        lng, lat, lng_err, lat_err = decode_exactly(code, bits_per_char=bpc)
        neighbours = utils.neighbours(code, bpc)

        expected_directions = {'east', 'west'}
        if lat + lat_err < 90:  # more earth to the north
            expected_directions.update({'north', 'north-west', 'north-east'})
        if lat - lat_err > -90:  # more earth to the south
            expected_directions.update({'south', 'south-west', 'south-east'})

        assert expected_directions == set(neighbours.keys())

        # no duplicates (depends on level)
        assert len(neighbours) == len(set(neighbours.values()))

        for v in neighbours.values():
            n_lng, n_lat, n_lng_err, n_lat_err = decode_exactly(v, bits_per_char=bpc)

            # same level
            assert len(code) == len(v)
            assert lng_err == n_lng_err
            assert lat_err == n_lat_err

            # neighbour is in disc 4x error
            assert (lng == n_lng or  # east / west
                    lng - 2 * lng_err == n_lng or lng - 2 * lng_err + 360 == n_lng or  # south
                    lng + 2 * lng_err == n_lng or lng + 2 * lng_err - 360 == n_lng)  # north

            assert (lat == n_lat or  # north / south
                    lat - 2 * lat_err == n_lat or lat - 2 * lat_err + 180 == n_lat or  # west
                    lat + 2 * lat_err == n_lat or lat + 2 * lat_err - 180 == n_lat)  # east


@pytest.mark.parametrize('bpc', (2, 4, 6))
@pytest.mark.parametrize('prec', range(1, 7))
def test_rectangle(bpc, prec):
    code = encode(rand_lng(), rand_lat(), bits_per_char=bpc, precision=prec)
    lng, lat, lng_err, lat_err = decode_exactly(code, bits_per_char=bpc)

    rect = utils.rectangle(code, bits_per_char=bpc)

    assert isinstance(rect, dict)
    assert rect['type'] == 'Feature'
    assert rect['geometry']['type'] == 'Polygon'
    assert rect['bbox'] == (lng - lng_err, lat - lat_err,
                            lng + lng_err, lat + lat_err)
    assert rect['properties'] == {
        'code': code,
        'lng': lng,
        'lat': lat,
        'lng_err': lng_err,
        'lat_err': lat_err,
        'bits_per_char': bpc,
    }

    coords = rect['geometry']['coordinates']
    assert 1 == len(coords)  # one external ring
    assert 5 == len(coords[0])  # rectangle has 5 coordinates

    # ccw
    assert (lng - lng_err, lat - lat_err) == coords[0][0]  # lower left
    assert (lng + lng_err, lat - lat_err) == coords[0][1]  # lower right
    assert (lng + lng_err, lat + lat_err) == coords[0][2]  # upper right
    assert (lng - lng_err, lat + lat_err) == coords[0][3]  # upper left
    assert (lng - lng_err, lat - lat_err) == coords[0][4]  # lower left


@pytest.mark.parametrize('bpc', (2, 4, 6))
@pytest.mark.parametrize('prec', range(1, 4))
def test_hilbert_curve(bpc, prec):
    hc = utils.hilbert_curve(prec, bpc)
    bits = bpc * prec

    assert isinstance(hc, dict)
    assert hc['type'] == 'Feature'
    assert hc['geometry']['type'] == 'LineString'

    coords = hc['geometry']['coordinates']
    assert 1 << bits == len(coords)

    for i, coord in enumerate(coords):
        code = encode(*coord, precision=prec, bits_per_char=bpc)
        assert i == decode_int(code, bpc)
