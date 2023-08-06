"""
Utilities
"""

import numpy as np
import xarray as xr
from typing import Union, List
from ledge.datatypes import Truth, Loss, Weight


def get_lag(series: Union[Truth, Loss]) -> int:
    """
    Parse lag value from the series
    """

    lag = ("lag" in series.attrs and series.attrs["lag"])
    if lag is False:
        return np.inf
    else:
        return lag


def uniform_weights(models: List[str], ones=True) -> Weight:
    weights = xr.DataArray(np.ones(len(models)))

    if not ones:
        weights /= len(models)

    return xr.DataArray(weights, dims="model", coords={ "model": models })
