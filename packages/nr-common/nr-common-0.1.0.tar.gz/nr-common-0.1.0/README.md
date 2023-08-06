# nr-common
[![Build Status](https://travis-ci.org/nitred/nr-common.svg?branch=master)](https://travis-ci.org/nitred/nr-common)

Common python functionalities aimed to be at least compatible with Python3.

#### Current Stable Version
```
0.1.0
```


# Installation

### pip
```
pip install nr-common
```


### Development Installation

* Clone the project.
* Install in Anaconda3 environment
```
$ conda env create --force -f dev_environment.yml
$ source activate nr-common
$ pip install -e .
```


# Test
To run the tests:
```
make test
```


# Usage
```python
from nr_common.pickler import read_pickle, write_pickle
from nr_common.mproc import mproc_func, mproc_async
from nr_common.configreader import config_from_path, config_from_env

from nr_common.blueprints.job_status import job_status_handler, db
```


# Examples
```
$ python examples/simple.py
```


# License
MIT
