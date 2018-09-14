# 9 Cell network

A network of 9 biophysical cells (3 different cell types) that are stimulated both inhibitory and excitatory virtual cells. The
virtual cells are stored as two separate networks (one with 10 exc and another with 10 inh) to allow running simulations 
with and without inhibitory inputs.


## Directory structure
* ./network/ - Sonata network files
  * cortex_node* - Description of the 9 biophysical cells (using V1 mouse models) 
  * excvirt_* - excitatory virtual cells and the connections onto the biophysical cells
  * inhvirt_* - excitatory virtual cells and the connections onto the biophysical cells
  
* ./inputs/ - Example sonata spike train file, used as the input of the virtual cells
  * exc_spike_trains.h5 - spike trains for excvirt cells
  * inh_spike_trains.h5 - spike trains for inhvirt cells

* ./circuit_config.json - sonata configuration containing network and model files used during simulation

* ./simulation_config.json - sonata configuration containing simulation parameters and reporting.

* ./output/ - sonata simulation files containing the results of a full network simulation (ran using bmtk)
  * spikes.h5 - spike times of internal network
  * [membrane_potential|calcium_cocentration].h5 - recorded biophysical variables of selected cells (see _reports_ section of circuit_config.json)


__*Optional - Generating and running the network*__  
The network was built and simulated using [The Brain Modeling Toolkit](https://github.com/AllenInstitute/bmtk). 
*build_network.py* can be used to build the network (synaptic connections are assigned randomly so every time the script is
executed the network will be slightly different) and *run_bionet.py* can be used to run a simulation. 

