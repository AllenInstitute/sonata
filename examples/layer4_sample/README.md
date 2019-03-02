# Layer 4 (subsampled) network

Based on the mouse V1 layer4 network as described in [Arkhipov 2018](https://www.biorxiv.org/content/10.1101/292839v1).
Includes a ~450 cells (1% of the original 45,000) recurrently connected V1 network with mixed compartmental and point-process
models. Plus a network of feedforward LGN virtual cells that is used to drive network activity

## Directory structure
* ./network/ - V1/L4 and LGN SONATA network files
* [simulation|circuit]_config.json - SONATA configuration files that specifies simulation parameters
* run_bionet.py - BMTK script for running a simulation
* generate_spikes.py - A script to generate LGN spike trains to drive the network.
* build_l4.py - BMTK script to generate SONATA V1/L4 network files
* build_lgn.py - BMTK script to generate SONATA LGN network files


### To run a simulation
Install BMTK with the NEURON and run the following
```python
$ python run_bionet.py config.json
```

### To rebuild the network
The easiest way to regenerate or rebuild the network is to change and rerun the ```build_l4.py``` and ``build_lgn.py```
scripts. Running them will overwrite the _network_ directory so be careful. Also the rules use a bit or randomness
when determining the number/placement of synapses so don't expect the same results every time you rebuild and rerun
the network.

To make the simulation capable easier to run the network was built with only 1% of the actual 45,000 cells. If you want
to try the full network you can open up ```build_l4.py``` and change the *PERCENTAGE_CELLS* variable. However be warned,
expect at least 4+ hours to build and save the network. And simulating the full network will usually not work without
access to a HPC cluster.
