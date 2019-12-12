# pySONATA

A python library for the SONATA data format

## Installation

Using pip:
```bash
$ pip install sonata
```

Install from source:
```bash
$ python setup.py install

```


## Usage

### Reading Configuration files
You can parse and validate a config json file using the from_json function in config.py. It will take care of manifest variables, combine links to other parts of the config (simulation.json, circuit.json) and return a completed json in python dictionary.
```python
from config import from_json
cfg = from_json('path/to/config.json')
print(cfg['run']['tstart'])

```
Note:
* You can also pass in a [jsonschema IValidator object](http://python-jsonschema.readthedocs.io/en/latest/validate/#jsonschema.IValidator) which will check if the json file follows the schema. The AIBS BMTK uses our own custom validators, and if desired I can add the code to this repo.


### Reading in circuit (nodes and edges) files

See [tutorial](https://github.com/AllenInstitute/sonata/blob/master/tutorials/pySonata/circuit-files.ipynb)


### Reading and writing compartment reports

See [tutorial](https://github.com/AllenInstitute/sonata/blob/master/tutorials/pySonata/compartment-reports.ipynb)


### Reading and writing spike train reports

See [tutorial](https://github.com/AllenInstitute/sonata/blob/master/tutorials/pySonata/spike-reports.ipynb)


