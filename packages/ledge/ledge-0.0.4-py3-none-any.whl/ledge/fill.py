"""
Imputation functions for dataset
"""

import xarray as xr
import numpy as np
from typing import List, Union
from functools import partial, wraps
from ledge.datatypes import Truth, Loss


Series = Union[Truth, Loss]


def window_linear(size, alpha=1):
    """
    Return arithmetically increasing weights.
    Value of alpha doesn't matter if using normalization.
    """

    return np.linspace(alpha, alpha * size, size)


def window_geometric(size, gamma):
    """
    Geometrically increasing weights
    """

    return np.geomspace(gamma, gamma ** size, num=size)[::-1]


def window_uniform(size):
    """
    Uniform weights
    """

    return np.ones(size)


def normalize(window_fn):
    """
    Decorator for normalizing the window function output
    """

    @wraps(window_fn)
    def _wrapper(*args, **kwargs):
        weights = window_fn(*args, **kwargs)
        return weights / np.sum(weights)

    return _wrapper


def lookback(window_size):
    """
    Decorator for clipping the lookback size to a limit.
    """

    def lookback_dec(window_fn):
        @wraps(window_fn)
        def _wrapper(size, *args, **kwargs):
            if window_size is None:
                return window_fn(size, *args, **kwargs)
            else:
                if window_size < size:
                    pad_len = size - window_size
                    return np.pad(window_fn(window_size, *args, **kwargs), (pad_len, 0), "constant")
                else:
                    return window_fn(size, **kwargs)
        return _wrapper
    return lookback_dec


def diff_window(series_list: List[Series], window_fn, inc=False) -> List[Series]:
    """
    Fill in the series using weighted mean of the diff between a `base` series.
    If incremental is true, the base series is the previous series. If false,
    the base is the first series.
    """

    if len(series_list) < 2:
        raise ValueError("At least 2 series needed")

    base_series = series_list[0]
    output = [base_series]

    for i in range(1, len(series_list)):
        if inc:
            base_series = output[i - 1]

        diffs = series_list[i] - base_series
        fallback = base_series + np.dot(diffs, window_fn(len(diffs)))

        output.append(series_list[i].combine_first(fallback))

    return output


"""
Weigh the past by taking mean of all
"""
diff_mean = partial(diff_window, window_fn=normalize(window_uniform))


"""
Fill in values by weighing the past linearly
"""
diff_linear = partial(diff_window, window_fn=normalize(window_linear))


def diff_geometric(series_list: List[Series], gamma: float, inc=False) -> List[Series]:
    """
    Fill in values by weighing the past geometrically using gamma
    """

    window_fn = normalize(partial(window_geometric, gamma=gamma))
    return diff_window(series_list, window_fn=window_fn, inc=inc)
