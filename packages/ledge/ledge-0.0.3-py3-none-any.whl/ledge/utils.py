"""
Utilities
"""

import numpy as np
from typing import Union
from ledge.datatypes import Truth, Loss


def get_lag(series: Union[Truth, Loss]) -> int:
    """
    Parse lag value from the series
    """

    lag = ("lag" in series.attrs and series.attrs["lag"])
    if lag is False:
        return np.inf
    else:
        return lag
