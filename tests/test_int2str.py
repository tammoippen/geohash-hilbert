# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from random import randint

from geohash_hilbert._int2str import decode_int, encode_int
import pytest
import six


def test_parameters():
    for bpc in (2, 4, 6):
        assert '1' == encode_int(1, bpc)
        assert 1 == decode_int('1', bpc)

    for nbpc in [1, 3, 5] + list(range(7, 100)) + list(range(0, -50, -1)):
        with pytest.raises(ValueError):
            encode_int(1, nbpc)

        with pytest.raises(ValueError):
            decode_int(1, nbpc)


def test_invalid():
    for bpc in (2, 4, 6):
        with pytest.raises(ValueError):
            encode_int(-1, bpc)


def test_empty():
    for bpc in (2, 4, 6):
        assert 0 == decode_int('', bpc)


@pytest.mark.parametrize('bpc', (2, 4, 6))
def test_randoms(bpc):
    prev_code = None
    for _i in range(100):
        i = randint(0, six.MAXSIZE)
        code = encode_int(i, bpc)
        assert isinstance(code, six.text_type)
        assert code != i
        assert i == decode_int(code, bpc)

        if prev_code is not None:
            assert code != prev_code

        prev_code = code
