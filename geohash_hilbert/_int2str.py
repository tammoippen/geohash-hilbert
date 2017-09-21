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


def encode_int(code, bits_per_char=6):
    '''Encode int into a string preserving order

    It is using 2, 4 or 6 bits per coding character (default 6).

    Parameters:
        code: int           Positive integer.
        bits_per_char: int  The number of bits per coding character.

    Returns:
        str: the encoded integer
    '''
    if code < 0:
        raise ValueError('Only positive ints are allowed!')

    if bits_per_char == 6:
        return _encode_int64(code)
    if bits_per_char == 4:
        return _encode_int16(code)
    if bits_per_char == 2:
        return _encode_int4(code)

    raise ValueError('`bits_per_char` must be in {6, 4, 2}')


def decode_int(tag, bits_per_char=6):
    '''Decode string into int assuming encoding with `encode_int()`

    It is using 2, 4 or 6 bits per coding character (default 6).

    Parameters:
        tag: str           Encoded integer.
        bits_per_char: int  The number of bits per coding character.

    Returns:
        int: the decoded string
    '''
    if bits_per_char == 6:
        return _decode_int64(tag)
    if bits_per_char == 4:
        return _decode_int16(tag)
    if bits_per_char == 2:
        return _decode_int4(tag)

    raise ValueError('`bits_per_char` must be in {6, 4, 2}')


# Own base64 encoding with integer order preservation via lexicographical (byte) order.
_BASE64 = (
    '0123456789'  # noqa: E262    #   10    0x30 - 0x39
    '@'                           # +  1    0x40
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # + 26    0x41 - 0x5A
    '_'                           # +  1    0x5F
    'abcdefghijklmnopqrstuvwxyz'  # + 26    0x61 - 0x7A
)                                 # = 64    0x30 - 0x7A
_BASE64_MAP = {c: i for i, c in enumerate(_BASE64)}


def _encode_int64(code):
    code_len = (code.bit_length() + 5) // 6  # 6 bit per code point
    res = ['0'] * code_len
    for i in range(code_len - 1, -1, -1):
        res[i] = _BASE64[code & 0b111111]
        code >>= 6
    return ''.join(res)


def _decode_int64(t):
    code = 0
    for ch in t:
        code <<= 6
        code += _BASE64_MAP[ch]
    return code


def _encode_int16(code):
    code = '' + hex(code)[2:]  # this makes it unicode in py2
    if code.endswith('L'):
        code = code[:-1]
    return code


def _decode_int16(t):
    if len(t) == 0:
        return 0
    return int(t, 16)


def _encode_int4(code):
    _BASE4 = '0123'
    code_len = (code.bit_length() + 1) // 2  # two bit per code point
    res = ['0'] * code_len

    for i in range(code_len - 1, -1, -1):
        res[i] = _BASE4[code & 0b11]
        code >>= 2

    return ''.join(res)


def _decode_int4(t):
    if len(t) == 0:
        return 0
    return int(t, 4)
