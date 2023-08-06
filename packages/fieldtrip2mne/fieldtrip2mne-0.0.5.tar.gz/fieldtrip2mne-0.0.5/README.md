# fieldtrip2mne

A Python module facilitating data conversion between MEG/EEG analysis toolboxes FieldTrip in MATLAB and MNE in Python. It works by reading FieldTrip data structures stored in .mat files and reassinging them to equivalent MNE structures. Several functions are provided to convert from different data types.

## How to use
```python
from fieldtrip2mne import read_raw

data = read_raw(filename)
```
```python
from fieldtrip2mne import read_epoched

data = read_epoched(filename)
```
```python
from fieldtrip2mne import read_avg

data = read_avg(filename)
```
## License
This module is developed by Thomas Hartmann & Dirk Gütlin at the Universität Salzburg. You are free to use, copy, modify, distribute it under the terms of the BSD 2 clause license.