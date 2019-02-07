# pySONATA

A python library for the SONATA data format

## Installation

```bash
$ python setup.py install

```
*More to come*


## Reading Configuration files
You can parse and validate a config json file using the from_json function in config.py. It will take care of manifest variables, combine links to other parts of the config (simulation.json, circuit.json) and return a completed json in python dictionary.
```python
from config import from_json
cfg = from_json('path/to/config.json')
print(cfg['run']['tstart'])

```
Note:
* You can also pass in a [jsonschema IValidator object](http://python-jsonschema.readthedocs.io/en/latest/validate/#jsonschema.IValidator) which will check if the json file follows the schema. The AIBS BMTK uses our own custom validators, and if desired I can add the code to this repo.


## Reading in Data Files (Nodes and Edges)

* [pySONATA Tutorial](docs/Tutorial\ -\ pySONATA.ipynb)
