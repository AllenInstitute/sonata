# 300 Cell network

A network of 300 biophysical cells, 5 cell types, 80% are excitatory and the rest inhibitory. It receives input from an external network of 100 virtual cells.

## Directory structure
* ./network/ - Sonata network files
  * internal_node* - Description of the 300 biophysical cells 
  * internal_internal_edges* - recurrent connections
  * external_node* - Nodes of the 100 external virtual cells
  * external_internal_edges* - Feedforward virtual --> biophysical connections.
  
* ./inputs/external_spike_trains.h5 - An example sonata spike train file, used as the input of the virtual cells

* ./circuit_config.json - sonata configuration containing network and model files used during simulation

* ./simulation_config.json - sonata configuration containing simulation parameters and reporting.

* ./output/ - sonata simulation files containing the results of a full network simulation (ran using bmtk)
  * spikes.h5 - spike times of internal network
  * cell_vars.h5 - recorded biophysical variables of selected cells (see _reports_ section of circuit_config.json)


__*Optional - Generating and running the network*__  
The network was built and simulated using [The Brain Modeling Toolkit](https://github.com/AllenInstitute/bmtk). 
*build_network.py* can be used to build the network (synaptic connections are assigned randomly so every time the script is
executed the network will be slightly different) and *run_bionet.py* can be used to run a simulation. 


