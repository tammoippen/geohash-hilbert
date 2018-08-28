setup_cython = {}
try:
    from Cython.Build import cythonize
    setup_cython = {'ext_modules': cythonize('geohash_hilbert/_hilbert_cython.pyx')}
except ImportError:
    pass


def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """
    setup_kwargs.update(setup_cython)
