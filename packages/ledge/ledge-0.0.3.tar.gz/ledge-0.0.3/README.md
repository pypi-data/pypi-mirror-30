# ledge

[![Build
Status](https://img.shields.io/travis/reichlab/ledge.svg?style=flat-square)](https://travis-ci.org/reichlab/ledge) [![Pypi](https://img.shields.io/pypi/v/ledge.svg?style=flat-square)](https://pypi.python.org/pypi/ledge)

Hedging algorithms with lag.

Besides the regular setting of 'prediction with expert advice', we are
interested in working with truth values with _lags_. This results in a partially
observed truth value for the present (and the past) at each step. In a discrete
time setting with delays in accurate characterization of _final_ truth, a truth
value is specified by:

1. `timepoint`: The time itself
2. `lag`: Time the value was revealed - `timepoint`

## TODO Usage

`ledge` is a composed from a bunch of types (`./ledge/datatypes.org`) and
functions. It works with
[DataArrays](http://xarray.pydata.org/en/stable/generated/xarray.DataArray.html#xarray.DataArray)
for model _predictions_, _losses_ and _truths_.
