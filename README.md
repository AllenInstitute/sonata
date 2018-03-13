
# SONATA Data Format

The SONATA Data Format is a Scalable Open Data Format for multiscale neuronal network models and simulation output, jointly developed by the Allen Institute for Brain Science (AIBS) and the Blue Brain Project (BBP) of the École polytechnique fédérale de Lausanne (EPFL).

The design and architecture of SONATA  builds on  both organizations’ expertise with large-scale high-performance  network simulation, visualization and analysis. It was designed for memory and computational efficiency, as well as to work across multiple platforms. Even though AIBS and BBP use different approaches to modeling and use different tools, the format allows networks built by one institute to be simulated by the other and vice versa. We provide specification documentation, open-source reference APIs, and model and simulation output examples with the intention of catalyzing support and adoption of the format in the modeling community.

The SONATA Data Format provides:

* Facilities for representing nodes (cells) and edges (synapses/junctions) of a network. It uses table-based data structures, hdf5 and csv, to represent nodes, edges and their respective properties. Furthermore indexing procedures  are specified to enable fast, parallelizable, and efficient partial lookup of individual nodes and edges. The use of hdf5 provides efficiency both in file size and IO time. , The format includes specific properties and naming conventions, but also allows modelers to extend node and edge model properties as they desire, to ensure models can be used with a variety of simulation frameworks and use cases.

* A JSON-based file format for configuring simulations, including specifying variables to record from, and stimuli to apply. 

* A systematic schema for describing simulation output/reports making it easy for users to exchange their simulation output data, and moreover the underlying hdf5 based format permits efficient storage of variables such as spike times, membrane potential, and Ca2+ concentration.

For further details on SONATA, see:

https://github.com/AllenInstitute/sonnet/blob/master/docs/SONATA_DEVELOPER_GUIDE.md

