NETWORK
=======
Sonata network of 5 biophysical cells (each a different model). No synaptic connections, no virtual cells.

./network/* - nodes file.


SIMULATION
==========
Simulated with input from current clamp injected at the soma. Uses a series of three increasing step currents, each with 
a 500 ms injection followed by another 500 ms rest.

./config - sonata circuit and simulation json configuration.
./output/* - Output from bmtk.BioNet simulator.

