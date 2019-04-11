#!/bin/bash

set -e

rm -rf output
rm -rf __pycache__
# python -m trace --trace ../shared_components/scripts/run_bionet.py ../input/config.json
python ../../../shared_components/scripts/run_bionet.py NEURON ../input/config.json

pytest -vvs
