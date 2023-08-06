"""
Functions for updating weights
"""

import xarray as xr
import numpy as np
from typing import List
from ledge.datatypes import Loss, Weight
from ledge.utils import uniform_weights


def ftl(losses: List[Loss], init_weights=None) -> Weight:
    """
    Follow the leader update. Give full weight to the model with least loss.
    """

    models = [loss.attrs["model"] for loss in losses]
    best_idx = np.argmin([loss.sum() for loss in losses])

    return xr.DataArray([1 if i == best_idx else 0 for i in range(len(losses))],
                        dims="model", coords={ "model": models })

def nop(losses: List[Loss], init_weights=None) -> Weight:
    """
    Do nothing.
    """

    models = [loss.attrs["model"] for loss in losses]
    if init_weights is None:
        return uniform_weights(models, ones=False)
    else:
        return init_weights


def ftpl(losses: List[Loss]) -> Weight:
    """
    Follow the perturbed leader update.
    """

    raise NotImplementedError()


def fixed_share(losses: List[Loss], eta: float, alpha: float, init_weights=None) -> Weight:
    r"""
    Fixed share update.
    """

    models = [loss.attrs["model"] for loss in losses]
    M = len(models)
    T = len(losses[0])

    if init_weights is None:
        weights = uniform_weights(models, ones=False)
    else:
        weights = init_weights

    # Vectorize this
    for t in range(T):
        vs = weights * np.exp([-eta * loss[t] for loss in losses])
        weights = (alpha * np.sum(vs) / M) + (1 - alpha) * vs

    return weights


def variable_share(losses: List[Loss]) -> Weight:
    r"""
    Variable share update.
    """

    raise NotImplementedError()


def mw(losses: List[Loss], eta: float, init_weights=None) -> Weight:
    r"""
    Multiplicative weight update. :math:`w_i(t + 1) = w_i(t) (1 - \eta m_i(t))`
    """

    models = [loss.attrs["model"] for loss in losses]

    if init_weights is None:
        init_weights = uniform_weights(models)

    updates = [np.prod(1 - eta * loss) for loss in losses]

    return init_weights * updates


def hedge(losses: List[Loss], eta: float, init_weights=None) -> Weight:
    r"""
    Exponential weight update. :math:`w_i(t + 1) = w_i(t) e^{- \eta m_i(t)}`
    """

    models = [loss.attrs["model"] for loss in losses]

    if init_weights is None:
        init_weights = uniform_weights(models)

    updates = [np.exp(-eta * np.sum(loss)) for loss in losses]

    return init_weights * updates
