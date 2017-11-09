# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from setuptools import find_packages, setup

setup_cython = dict()
try:
    from Cython.Build import cythonize
    setup_cython = dict(ext_modules=cythonize('geohash_hilbert/_hilbert_cython.pyx'))
except ImportError:
    pass

try:
    long_description = open('README.rst').read()
except IOError:
    long_description = open('README.md').read()

version = '1.2'

setup(
    name='geohash-hilbert',
    version=version,
    packages=find_packages(),
    install_requires=[],
    author='Tammo Ippen',
    author_email='tammo.ippen@posteo.de',
    description='Geohash a lng/lat coordinate using the hilbert curve.',
    long_description=long_description,
    license='MIT',
    url='https://github.com/tammoippen/geohash-hilbert',
    download_url='https://github.com/tammoippen/geohash-hilbert/archive/v{}.tar.gz'.format(version),
    keywords=['geohash', 'hilbert', 'space filling curve', 'geometry'],
    include_package_data=True,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    **setup_cython
)
