# This file is not meant for public use and will be removed in SciPy v2.0.0.
# Use the `scipy.sparse` namespace for importing the functions
# included below.

import warnings
from . import _data


__all__ = [  # noqa: F822
    'isscalarlike',
    'matrix',
    'name',
    'npfunc',
    'spmatrix',
    'validateaxis',
]


def __dir__():
    return __all__


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(
            "scipy.sparse.data is deprecated and has no attribute "
            f"{name}. Try looking in scipy.sparse instead.")

    warnings.warn(f"Please use `{name}` from the `scipy.sparse` namespace, "
                  "the `scipy.sparse.data` namespace is deprecated.",
                  category=DeprecationWarning, stacklevel=2)

    return getattr(_data, name)
