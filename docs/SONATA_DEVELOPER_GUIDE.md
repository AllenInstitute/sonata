# SONATA Data Format: A common data model for representing biophysical and point neuron circuits proposed by the AIBS and BBP

Contributors: Eilif Muller, Sergey Gratiy, Werner Van Geit, Jean-Denis Courcol, Anton Arkhipov, Mike Gevaert, Adrien Devresse, Yazan Billeh, Kael Dai, James King, Juan Hernando …

Version 0.1

Date: Q1-2018

## Abstract

The need has arisen at both the Blue Brain Project (BBP) and the Allen Institute for Brain Science (AIBS) for efficient ways of representing circuits of neurons (composed of biophysically detailed neuron and point-neuron models) and the output of simulation thereof for analysis and visualization.  Such representations are not generally available as open-source tools in the computational neuroscience community, so both the BBP and AIBS have developed internally their own representations to meet these needs.  As the public release of these circuits is on both the AIBS and BBP roadmaps, it is desirable to converge on a data model to release these circuits, so as to provide a foundation to foster an emerging ecosystem of tools around the data model, developed by the AIBS, BBP and the community at large.

The objective of this document is to specify a common data model for neural circuits and simulation output which can be used and supported in the future by both AIBS and BBP.  The data model will be novel compared to other community approaches (e.g. NeuroML) in that it will be optimized for performance for simulation, analysis and visualization of large-scale circuits. This document is accompanied by an example network in the presented data format.

## Mission Statement

This document is intended to present the rationale and outcomes of discussions and analysis towards convergence.  It is a high-level document which can guide the development and public release of a standard "performance representation" data model and associated specifications, including user and developer documentation by the BBP and AIBS.  It is understood that such a data model is complementary, and should co-exist with and leverage existing model representation efforts, such as NeuroML, wherever performance considerations allow.  The latter focuses on flexible and open exchange, cross-simulator reproducibility, and rigorous declarative representation.  In contrast, the present effort focuses on representing a curated subset of models expressible in NeuroML, in compact and efficient representations leveraging existing technologies such as hdf5, SQLite, graph databases, spatial indexing, etc. to enable an ecosystem of performant simulation, analysis and visualization tools.  An import-export bridge between these two approaches will ensure a complementary and mutual benefit.

## Common conventions

This specification is supported by several file syntax/container formats, the
most important being HDF5, JSON and CSV. Some conventions apply to how these
formats are used in the specification.

### HDF5

The following conventions apply to all SONATA h5 files:

* Data sets are described by their shape and data type (dtype).
* Datatypes are declared using the following nomenclature:
    * **str**: a H5T_C_S1 type string with UTF-8 encoding
    * **float**: H5T_IEEE_F32LE
    * **double**: H5T_IEEE_F64LE
    * **bool**: H5T_STD_I8LE with value 1 or 0
    * **int32**: H5T_STD_I32LE
    * **uint32**: H5T_STD_U32LE
    * **int64**: H5T_STD_I64LE
    * **uint64**: H5T_STD_U64LE
* Each h5 file must contain the following two top level attributes:
    * **version** A 2-element uint32 dataset containing the spec version which
      the file conforms.
    * **magic** A uint32 with the value 0x0A7A

### CSV

The CSV dialect is the following:

* ASCII encoded text files with UNIX line terminators.
* Columns are separated by one or multiple spaces
* Fields containing spaces can be quoted using ". To include the quoting
  character inside a field it must appear twice.

## Representing Circuits

The common circuit representation format is described in subsequent subsections as follows:

* [Representing biophysical neuron morphologies](#biophysical_morphologies)

* [Representing ion channels, point neuron and synapse models](#ion_channels)

* [Representing biophysical neuron channel distribution and composition](#biophysical_neuron_channels)

* [Representing networks of neurons](#neuron_networks)

    * [The node table](#neuron_networks_nodes)

    * [The edge table](#neuron_networks_edges)

* [Tying it all together - the circuit config file](#network_config)

### <a name="biophysical_morphologies"></a>Representing biophysical neuron morphologies

The format used is SWC ( [http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html) ) with additional requirements as described below.

#### SWC Format additional requirements:

* Comment lines begin with character '#'.

* Subsequent non-empty lines each represent a single neuron sample point with seven data items:

<table>
  <tr>
    <td>Column</td>
    <td>Interpretation</td>
  </tr>
  <tr>
    <td>1</td>
    <td>ID ('Sample Number')</td>
  </tr>
  <tr>
    <td>2</td>
    <td>Type ('Structure Identifier')</td>
  </tr>
  <tr>
    <td>3</td>
    <td>X Position (um)</td>
  </tr>
  <tr>
    <td>4</td>
    <td>Y Position (um)</td>
  </tr>
  <tr>
    <td>5</td>
    <td>Z Position (um)</td>
  </tr>
  <tr>
    <td>6</td>
    <td>Radius (um)</td>
  </tr>
  <tr>
    <td>7</td>
    <td>Parent ID ('Parent Sample Number')</td>
  </tr>
</table>


* Point soma, interpreted as a sphere with radius from column 6 (**Cylindrical somas are not used**)

   	Point soma will be interpreted in NEURON as cylinder with L=radius

* Types: The following types are currently used.

  1 - soma
  2 - axon
  3 - basal dendrite
  4 - apical dendrite

* IDs must start at 1

* IDs must increase without 'jumps' or 'gaps'

* All neurites must be connected to the soma (no 'floating'/unconnected trees)

* A chain of connected sample points where the end points are either terminal
  points of bifurcating points are called a section. Points from sections
  connected to the same first order section (emanating from the soma) must have
  the same sample type.

* A sample point is the end-point of a segment. It's previous sample is the
  start point of the segment

* All segments of a section must be sequential and contiguous

* All parent sample points must exist before children sample points

* For the purpose of mapping information to morphologies, each section has a
  designated section ID, which is a integer in [0, #sections - 1]. The soma is
  always section 0. The rest of the sections are first grouped by section
  type in this order: 1 = axon, 2 = basal and 3 = apical. All sections in a
  group are given IDs incrementally, starting at the last ID from the previous
  section plus 1. The order in which sections are assigned an ID is the order
  in which their first segment appears in the file.

It is not required that the soma is located at 0,0,0 in the SWC file, but in cases where the morphology has a soma, the soma will be re-centered to 0,0,0 upon loading into the circuit.  Node translations will then be applied to this recentered morphology. This behavior can be overridden by the optional reserved attribute "recenter" for nodes and node_types.  See "Representing networks of neurons" for more details.

It is recommended, but not required, that morphologies in a network have a standardized orientation, so that their orientation vectors in the network can be inferred from node rotation angles.  For circuits for which this is true, the circuit producer can declare it with the "standardized_morphology_orientation" entry in the circuit_config.json, so downstream users can safely assume it.  See "Tying it all together - the circuit_config file" for more details.

### <a name="ion_channels">Representing ion channel, point neuron and synapse models

To represent point neuron models, synapses and ion channels NEURON MOD files are used.  Models provided as standard by NEURON are also valid, such as ExpSyn, IntFire1.

To support reproducible random numbers in NEURON, it is required to define conventions for the configuration of random number generators, and how they are assigned to channel models, synapses random number generators.  To this end, NEURON mechanisms should follow idioms in the MOD files, so that a uniform and automated approach to random number configuration can be employed.  Such an approach was out of scope of the current format specification, and will be the subject of future versions.

The forthcoming NeuroML/LEMS format shows promise for representing synapses and ion channels.  Adopting such representations promises simulator independence, and significant improvements for modernizing code-generation pipelines for NEURON, coreNEURON and NEST, and exotic compute architectures, such as GPU, SpiNNaker. However, this issue is recommended to be left to a later date, when LEMS has matured enough to represent stochastic synapses.

### <a name="biophysical_neuron_channels">Representing biophysical neuron channel distribution and composition

For representing the parameterization and distribution of ion channels and passive properties of neurons three formats will be supported: 1), an xml file using a NeuroML "biophysicalProperties" and “concentrationModel” block schema (cf [https://github.com/NeuroML/NeuroML2/blob/master/Schemas/NeuroML2/NeuroML_v2beta4.xsd](https://github.com/NeuroML/NeuroML2/blob/master/Schemas/NeuroML2/NeuroML_v2beta4.xsd) ) 2) a JSON file using Allen Cell Types Data Base schema. 3) a HOC template.

#### NeuroML

Channel names (the "id" attribute) and parameter name attributes are expected to map one-to-one with the MOD files used.

Valid values for "segmentGroup" attributes are {“soma”,”axon”,”dend”,"apic"} corresponding to the SWC type column definitions as follows 1 - soma,  2 - axon,  3 - basal dendrite,  4 - apical dendrite.

The current model format does not yet specify how users can define their own segmentGroup types, and associated type column ids.  This feature will be developed in future versions.

Units will be ignored, i.e. they will not be interpreted or converted, and should correspond to the units in the MOD files.

Restrictions on NeuroML file names

1. one and only one cell element in the file

2. All elements must have unique "id"s

3. We allow arbitrary valid filenames,as long as tools such as Python csv parser, or pandas can process these file names from, e.g., a csv file (inside of which these file names may be surrounded by quote marks, if necessary -- e.g., if the filename contains spaces).

It is worth noting that the scope of the current work was with neuron models which had uniform ion channel distributions.  For future versions of the common format, an example with non-uniform channel distributions should also be considered.

How specific NeuroML files are combined with specific morphology files to represent a neuron in a population of neurons is described below in the section "Representing neuron populations".

An example:

    <neuroml xmlns="http://www.neuroml.org/schema/neuroml2" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.neuroml.org/schema/neuroml2 https://raw.github.com/NeuroML/NeuroML2/development/Schemas/NeuroML2/NeuroML_v2beta5.xsd" id="NeuroML2_file_exported_from_NEURON">

        <concentrationModel id="CaDynamics" type="CaDynamics" minCai="1e-4 mM" decay="991.140696832 ms" depth="0.1 um" gamma="0.0040218816981199999" ion="ca"/>

        <cell id="473863510">

            <notes>
    Export of a cell model (473863510) obtained from the Allen Institute Cell Types Database into NeuroML2

    Electrophysiology on which this model is based: http://celltypes.brain-map.org/mouse/experiment/electrophysiology/314804042

    ******************************************************
    *  This export to NeuroML2 has not yet been fully validated!!
    *  Use with caution!!
    ******************************************************
            </notes>

            <biophysicalProperties id="biophys">
                <membraneProperties>
                    <channelDensity id="gbar_Im" ionChannel="Im" condDensity="0.00043788364247700001 S_per_cm2" erev="-107.0 mV" segmentGroup="soma" ion="k"/>
                    <channelDensity id="gbar_Ih" ionChannel="Ih" condDensity="0.0019922075246600001 S_per_cm2" erev="-45 mV" segmentGroup="soma" ion="hcn"/>
                    <channelDensity id="gbar_NaTs" ionChannel="NaTs" condDensity="0.71282189194800005 S_per_cm2" erev="53.0 mV" segmentGroup="soma" ion="na"/>
                    <channelDensity id="gbar_Nap" ionChannel="Nap" condDensity="0.0012493753876800001 S_per_cm2" erev="53.0 mV" segmentGroup="soma" ion="na"/>
                    <channelDensity id="gbar_K_P" ionChannel="K_P" condDensity="0.034836377263399998 S_per_cm2" erev="-107.0 mV" segmentGroup="soma" ion="k"/>
                    <channelDensity id="gbar_K_T" ionChannel="K_T" condDensity="0.0166428509042 S_per_cm2" erev="-107.0 mV" segmentGroup="soma" ion="k"/>
                    <channelDensity id="gbar_SK" ionChannel="SK" condDensity="0.00024972209054299998 S_per_cm2" erev="-107.0 mV" segmentGroup="soma" ion="k"/>
                    <channelDensity id="gbar_Kv3_1" ionChannel="Kv3_1" condDensity="0.28059766435600003 S_per_cm2" erev="-107.0 mV" segmentGroup="soma" ion="k"/>
                    <channelDensity id="g_pas_soma" ionChannel="pas" condDensity="0.00092865666454699993 S_per_cm2" erev="-85.6125717163 mV" segmentGroup="soma" ion="non_specific"/>
                    <channelDensity id="g_pas_axon" ionChannel="pas" condDensity="0.000914230933548999861 S_per_cm2" erev="-85.6125717163 mV" segmentGroup="axon" ion="non_specific"/>
                    <channelDensity id="g_pas_dend" ionChannel="pas" condDensity="3.8264043188599994e-06 S_per_cm2" erev="-85.6125717163 mV" segmentGroup="dend" ion="non_specific"/>
                    <channelDensity id="g_pas_apic" ionChannel="pas" condDensity="2.11145615996e-06 S_per_cm2" erev="-85.6125717163 mV" segmentGroup="apic" ion="non_specific"/>
                    <channelDensityNernst id="gbar_Ca_HVA" ionChannel="Ca_HVA" condDensity="0.00015339031713199999 S_per_cm2" segmentGroup="soma" ion="ca"/>
                    <channelDensityNernst id="gbar_Ca_LVA" ionChannel="Ca_LVA" condDensity="0.0033469316039000004 S_per_cm2" segmentGroup="soma" ion="ca"/>
                    <specificCapacitance value="1.0 uF_per_cm2" segmentGroup="soma"/>
                    <specificCapacitance value="1.0 uF_per_cm2" segmentGroup="axon"/>
                    <specificCapacitance value="2.19 uF_per_cm2" segmentGroup="dend"/>
                    <specificCapacitance value="2.19 uF_per_cm2" segmentGroup="apic"/>
                </membraneProperties>

                <intracellularProperties>
                    <species segmentGroup="soma" id="ca" concentrationModel="CaDynamics" ion="ca" initialConcentration="0.0001 mM" initialExtConcentration="2 mM"/>
                    <resistivity value="35.64 ohm_cm"/>
                </intracellularProperties>

            </biophysicalProperties>
        </cell>
    </neuroml>

#### Allen Cell Types Database JSON

Example:

    {
        "passive": [
        	{
          	    "ra": 113.558283035,
          	    "cm": [
            	    {
              	        "section": "soma",
              	        "cm": 2.99126584079
            	    },
            	    {
              	        "section": "axon",
              	        "cm": 2.99126584079
            	    },
            	    {
              	        "section": "dend",
              	        "cm": 2.99126584079
            	    }
          	    ],
          	    "e_pas": -77.77002716064453
        	}
        ],
        "fitting": [
        	{
          	    "junction_potential": -14.0,
          	    "sweeps": [
            	    29
          	    ]
        	}
        ],
        "conditions": [
        	{
          	    "celsius": 34.0,
          	    "erev": [
            	    {
              	        "ena": 53.0,
              	        "section": "soma",
              	        "ek": -107.0
            	    }
          	    ],
          	    "v_init": -77.77002716064453
        	}
        ],
        "genome": [
        	{
          	    "section": "soma",
          	    "name": "gbar_Ih",
          	    "value": 0.0007483146089529596,
          	    "mechanism": "Ih"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_NaV",
          	    "value": 0.056101742007372987,
          	    "mechanism": "NaV"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_Kd",
          	    "value": 0.00017519914026510974,
          	    "mechanism": "Kd"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_Kv2like",
          	    "value": 3.9813942512016004e-05,
          	    "mechanism": "Kv2like"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_Kv3_1",
          	    "value": 0.14292671428791784,
          	    "mechanism": "Kv3_1"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_K_T",
          	    "value": 6.2099957475404229e-07,
          	    "mechanism": "K_T"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_Im_v2",
          	    "value": 0.0025519715891636685,
          	    "mechanism": "Im_v2"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_SK",
          	    "value": 0.02123536247580915,
          	    "mechanism": "SK"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_Ca_HVA",
          	    "value": 0.00029467875153102062,
          	    "mechanism": "Ca_HVA"
        	},
        	{
          	    "section": "soma",
          	    "name": "gbar_Ca_LVA",
          	    "value": 0.0032854032146529648,
          	    "mechanism": "Ca_LVA"
        	},
        	{
          	    "section": "soma",
          	    "name": "gamma_CaDynamics",
          	    "value": 0.0001916236273002056,
          	    "mechanism": "CaDynamics"
        	},
        	{
          	    "section": "soma",
          	    "name": "decay_CaDynamics",
          	    "value": 533.54574062570703,
          	    "mechanism": "CaDynamics"
        	},
        	{
          	    "section": "soma",
          	    "name": "g_pas",
          	    "value": 0.00079694107853819723,
          	    "mechanism": ""
        	},
        	{
          	    "section": "axon",
          	    "name": "g_pas",
          	    "value": 0.00059005234857028601,
          	    "mechanism": ""
        	},
        	{
          	    "section": "dend",
          	    "name": "g_pas",
          	    "value": 3.5492496289639374e-07,
          	    "mechanism": ""
        	}
        ]
    }

#### HOC template

Parameters may be specified inside the HOC template in an arbitrary manner.

Example:

https://senselab.med.yale.edu/modeldb/ShowModel.cshtml?model=139653&file=/L5bPCmodelsEH/models/L5PCbiophys2.hoc#tabs-2

### <a name="neuron_networks">Representing networks of neurons

#### Overview

We consider a network of neurons as a graph made up of of nodes (neurons) and edges (connections between the neurons). Nodes of a network can be arranged into multiple populations of neurons. For instance, a population may correspond to a brain region or a particular cell type.   The connectivity between a source population and a target population is defined by an edge population.  Nodes and edges in their respective populations are also assigned respective node and edge *types.  *Parameters assigned to node or edge types are inherited for all nodes or edges of the respective type. * *A given node or edge can be associated with one and only one node or edge type, respectively.

All nodes and edges, and likewise node and edge types can have be assigned  attributes which define various aspects, such as position, rotation, type, modelparameters, etc. Nodes and edges inherit attributes from their respective types, but also override them. Some attributes are required, some are optional with reserved meaning, and others are entirely optional.  The entirely optional attributes can be added by the user for their own specific needs , and are typically ignored by the simulator software.  These optional attributes may be added by users simply for convenience to help them maintain the workflow through model building, simulation, and analysis.

The details of how node and edge populations are defined and represented are described in the following sections.

#### <a name="neuron_networks_nodes">Representing nodes

In general, populations of neurons are heterogeneous in the  types of cell models describing each node, implying heterogeneousequations and sets of parameters.  We define a node group  as a set of nodes with a homogeneous parameter namespace implying a uniform tabular layout. A population is defined as the union of one or more groups, which need not have uniform tabular layout among them, and further defines some indexing datasets.  A population provides then a uniform view on a collection of nodes which have heterogeneous parameterization namespaces.

A model_type attribute allows nodes to be configured as "biophysical", “point_soma”, etc. and also “virtual” one may be provided to specify external (or “virtual”) nodes that are not explicitly simulated but provide inputs to the network.

A typical network may include multiple simulated populations as well as multiple populations of external input nodes.

Each node in a population has a node type.  Attributes can be assigned to nodes and node types, whereby a node assumes attributes of itsnode type, and can override them at the individual node level.  Below, attributes which have specified interpretation and expected units (where applicable) are defined, and are either "required" or “optional reserved”.

Node types are defined in node types CSV files containing named columns, one for each attribute of a node type. First, the node_type_id column is required, and defines the node_type_id of each row. To allowmultiple populations define their own node_type_id’s independently, a population column is also required to resolve collisions between node_type_id’s among different populations.  Other "required" attributes must either be defined by the population (see below), or be defined in a column in the associated node types CSV.  The node types CSV may also include “optional reserved” columns names.  Apart from these reserved names, the user is free to define any number of additional named columns to suit their needs.  Node type columns will be assigned to node attributes with the column name as the key and the value coming from the row with a node’s assigned node_type_id.

Populations are serialized in nodes HDF5 files, and have a single  associated node types CSV file to define the valid node_type_ids for the populations in the HDF5 file, and assign attributes applying to all nodes in with a given node_type_id.  A node_types CSV file may be shared by multiple population HDF5 files. Node groups are represented as HDF5 groups (with population as parent) containing a dataset for each parameter of length equal to the number of  nodes in the group. In the case a node attribute is defined in both the node types CSV and the nodes HDF5, the value in the nodes HDF5 overrides the node types CSV value.



The HDF5 nodes file layout is designed to store multiple named populations that each may have multiple node groups, but each population with all of its node groups must be self-contained within one HDF5 file..  For each population, the node_id and node_type_id datasets are required because they uniquely identify nodes within a population irrespective of a model_type used. The node_group and node_group_index are required because they identify the location of the group specific data for each node.The model_type attribute is required, but may be defined only in the node_types CSV. The layout of the nodes HDF5 is as shown in Table 1.

<table>
  <tr>
    <td>/nodes</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/node_type_id</td>
    <td>Dataset{N_total_nodes}</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/node_id</td>
    <td>Dataset{N_total_nodes}</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/node_group_id</td>
    <td>Dataset{N_total_nodes}</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/node_group_index</td>
    <td>Dataset{N_total_nodes}</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id1&gt;/</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id1&gt;/my_attribute</td>
    <td>Dataset {M_nodes}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {M_nodes}</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id1&gt;/dynamics_params</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id1&gt;/dynamics_params/neuron_param1</td>
    <td>Dataset {M_nodes}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {M_nodes}</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id2&gt;/</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id2&gt;/my_other_attribute</td>
    <td>Dataset {K_nodes}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {K_nodes}</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id2&gt;/dynamics_params</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/nodes/&lt;population_name&gt;/&lt;group-id2&gt;/dynamics_params/neuron_param2</td>
    <td>Dataset {K_nodes}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {K_nodes}</td>
  </tr>
</table>


Table 1: The Layout  of the HDF5 file format for describing nodes.

##### Nodes - Required Attributes

**/nodes** - The top-level group that will contain populations.  This group must always be present.

**/nodes/<population_name>** - defines a node population with the given name, which is also the node population name that will be used in edge files to specify the source or target node populations of an edge population (see below).  Multiple populations may be defined in one HDF5 file.

**node_type_id** -  This is a unique integer for every node type used to associate a node to a node type.  A node type has associated attributes, and a node inherits attributes from its node type.  Attributes associated with a node override attributes inherited from the node type CSV. node_type_id is a unique integer associated with each node type and is used to index all the node type properties associated with a given node with known node_type_id.  These need not be ordered or contiguous, but must be unique.

**model_type** - Has four valid values: , "biophysical"”,“virtual”, “single_compartment”, “point_process”.  In the future, more model_types may be defined. The meaning of each of these model types is as follows.

The model_type=*"single_compartment"”* is a single-compartment model of a neuron.   A cylindrical compartment is created with length equal to diameter, and the diameter being defined by an additional expected dynamics_param “D”, which if not specified defaults to 1 micron.  The voltage of the neuron is defined by the voltage of the compartment.  Further, the passive mechanism is inserted, and the additional mechanism named in the “model_template” required attribute. Note that a single compartment of length = diameter has the same effective area as that of a sphere of the same diameter (see [NEURON documentation](https://www.neuron.yale.edu/neuron/static/docs/help/neuron/neuron/geometry.html)).

The model_type=*"point_process"* results in a point process neuron, i.e. a NEURON artificial cell.  The point process model is named in the “model_template” required attribute.

The model_type=*"virtual"* results in a placeholder neuron, which is not otherwise simulated, but can be the source of spikes which result in post-synaptic events.

The model_type=*"biophysical"* results in a compartmental neuron.  The attribute **morphology** must be defined, either via the node or node_type.

**model_template** - Used to reference a template or class describing the electrophysical properties and mechanisms of the node(s). Its value and interpretation is context-dependent on the corresponding ‘model_type’. When there is no applicable model template for a given model type (i.e. model_type=virtual) it is assigned a value of NULL. Otherwise it uses a colon-separated string-pair with the following syntax:

*<schema>*:*<resource>*

*<schema>* is a keyword used to identify the type of template being specified. Reserved options include:

nml: Template is described by a NeuroML file. Valid for biophysical model types.

actdb: Template is described using a pre-generated hoc template specifically designed to run AIBS cell type models. Valid for both biophysical and single_compartment model types

hoc: Template is described using a customized hoc file. Valid for both biophysical and single_compartmentmodel types

nrn: Valid for both point_process and single_compartment model types. For a point_process model type, <resource> should specify the name of NEURON simulator point_process (i.e. IntFire1, IntFire2).  For a single_compartment type, <resource> should specify the name of the mechanism to insert.

*<resource>* is a reference to the template file-name or class. For file names if a full-path or url is not specified the interpreter is expected to use the "components" in the config file to find the full path (see below).

**node_group_id** - Assigns each node to a specific group of nodes.

**node_group_index** - After determining the node_group_id of a specific node, the node_group_index indicates the index within that <node-group-id> that contains all the attributes for a particular node under consideration.

#### Nodes - Optional Reserved Attributes

**node_id** - Assigns a key to uniquely identify and lookup a node within a population.  It is primarily used to specify the source and target of an edge (connection). If not provided, node_ids are implicitly contiguous starting from zero.

**model_processing** - A string to specify alternative processing approaches in the model construction behaviour of biophysical neurons. For valid model_processing values, and their meanings, see the Appendix *Valid Values for "model_processing"*.   It is currently not valid to specify this attribute for model_type != ”biophysical”.

Example:

For model_processing=*"fullaxon"*, the biophysical neuron will construct and simulate the full axon. This is the default behaviour if model_processing is undefined for a given node.

**x, y, z** - position of the soma in world coordinates.

**rotation_angle_zaxis [FLOAT], rotation_angle_yaxis[FLOAT], rotation_angle_xaxis[FLOAT]** - rotation of the morphology around the soma.

Each morphology is first moved from its original coordinates in SWC to such a location that the soma is at (0, 0, 0).  Then, three rotations are applied to each morphology, in exactly the following sequence: (1) rotation around the z-axis; (2) rotation around the y-axis; (3) rotation around the x-axis; all rotations are around the axes of the global coordinate system.  Then, each morphology is shifted to such a location that its soma is at (x, y, z) coordinates specified in the node/node_type files.  The angles for the three rotations are also provided in the nodes/node_types files, in radians.  If a column is not provided, it is assumed that the rotation angle around that axis is 0 (that is, no rotation around that axis is applied).

**morphology** [TEXT] - Name of the detailed morphology for a given node or node type. For name `foo`, the corresponding SWC file would be found at `$morphologies_dir/foo.swc`, where `$morphologies_dir` is specified in the [network config](#network_config).

**recenter** [INT8] - Optional reserved attribute, if the value is set to 0, morphology would _not_ be moved to (0, 0, 0) prior to rotation / translation.

**dynamics_params** - Define parameter overrides for nodes. This attribute can exist in the node_types.csv file in which case a .json file is referenced, which should contain a dictionary of keys and values.  A key should be a valid name in the namespace of parameters of the model, and the value specifies the assigned parameter override. Alternatively, dynamics_params overrides can be specified for each individual node in a group, in the corresponding nodes HDF5.  In this case,  a dynamics_params HDF5 group contains datasets named according to the parameter of the model to override in the namespace of parameters of the model (see Table 1). The length of such datasets is the number of nodes in the group.

Note that if an override is defined  for a given name in both the nodes HDF5 file and the nodes_types CSV file, then the HDF5 file will override the latter.

The namespace of parameters depends on model_type, and are defined as follows.

**For point_soma models**, it is the namespace of the NEURON Section containing the "pas" and user requested soma mechanism.

**For point_process models**, it is the namespace of the point_process/artificial cell mechanism.

**For biophysical models** defined according to the *nml *schema (see above), names take the form "<id>.<attribute>", where <id> is the id of an element and <attribute> an attribute of said element in the nml file defining the biophysical model.  For example “g_pas_apic.erev” refers to the “erev” attribute of the “g_pas_apic” element of the nml biophysics block defining the channel composition of the model.  It is worth noting that namespaces defined in this way apply equally to dynamics_params overrides at the node_types and node levels for all model types.

**For biophysical models** defined according to the *bmtk *(see above), the namespace definition is to be filled in by the Allen folks.

**For biophysical models** defined according to the *hoc *(see above), the namespace definition is to be filled in by the Allen folks.

For a conceptual schematic of the architecture relating node attributes *model_type*,* model*, and *dynamics_params* overrides and their namespaces at the node_type and nodes level, see Table 2.

<table>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td>Model Type</td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>point_process</td>
    <td>point_soma</td>
    <td>biophysical</td>
  </tr>
  <tr>
    <td>Parameter
Override</td>
    <td>Node
level</td>
    <td>dynamics_params HDF5 group</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td></td>
    <td>Node_type
level</td>
    <td>dynamics_params .json</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Model
Object</td>
    <td>Parameter
Namespace</td>
    <td>point process</td>
    <td>Section ∪ pas ∪
user mechanism</td>
    <td><id>.<attr>
∈ .nml file</td>
  </tr>
  <tr>
    <td></td>
    <td>Model</td>
    <td>point process name</td>
    <td>mechanism name</td>
    <td>.nml file</td>
  </tr>
</table>


Table 2: A conceptual schematic of the architecture relating node attributes* model*, and *dynamics_params* overrides at the node_type and nodes level for each model_type.  The namespace of both node_type and node level parameter overrides are given uniquely by the model object parameter namespace.  Node level parameter overrides take precedence over node_type level parameter overrides.

#### <a name="neuron_networks_edges">Representing Edges

Analogous to nodes, edges are defined in populations stored in HDF5 files containing attributes for each edge. Each edge population is composed on one or moreedge groups. Like nodes, edge groups have a uniform tabular layout, i.e. a homogeneous attribute namespace. Each HDF5 file is associated with an edge types CSV file containing attributes applied to all edges in the HDF5 file with a given edge_type_id.

The edge_types file is a CSV file of named columns. The edge_type_id column is required, and defines the edge_type_id of each row. To handle edges h5 files with multiple populations, a population column is also required to resolve collisions between edge_type_id’s among different populations. "Required" attributes must either appear in the HDF5 representation, or be defined in a column in the associated edges types CSV file.  The edge types CSV file may also include “optional reserved” column names which have specified interpretation and expected units. Apart from these reserved names, the user is free to define any number of additional named columns to suit their needs.  Columns will be assigned to edge attributes with the column name as the key and the value coming from the row with an edge’s assigned edges_type_id.

In the edges HDF5 file, edge populations are defined as HDF5 groups. Every edge in an edge population connecting two node populations is stored, only if it exists, in two datasets: source_node_id and target_node_id. These two datasets have an associated attribute "node_population" that specifies the node population for resolving the node_ids of the source or target.

The edge population has has three more required datasets. First is the edge_group_id dataset that indicates what edge group the simulator should search for the properties of a specific edge. Second is the edge_group_index that provides the index within that edge_group where the parameters exist. Finally, the edge_type_id, as mentioned above, links the edges HDF5 file with the edge_types CSV files for repeated parameters among specific edges.

The HDF5 edges file layout is designed to store multiple populations of multiple edge groups. The layout of the edges HDF5 is as follows.

<table>
  <tr>
    <td>/edges</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/edge_type_id</td>
    <td>Dataset{N_total_edges}</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/source_node_id</td>
    <td>Dataset{N_total_edges} - with attribute specifying source population name</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/target_node_id</td>
    <td>Dataset{N_total_edges} - with attribute specifying target population name</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/edge_group_id</td>
    <td>Dataset{N_total_edges}</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/edge_group_index</td>
    <td>Dataset{N_total_edges}</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id1&gt;/</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id1&gt;/my_attribute</td>
    <td>Dataset {M_edges}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {M_edges}</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id1&gt;/dynamics_params</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id1&gt;/dynamics_params/edge_param1</td>
    <td>Dataset {M_edges}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {M_edges}</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id2&gt;/</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id2&gt;/my_other_attribute</td>
    <td>Dataset {K_edges}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {K_edges}</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id2&gt;/dynamics_params</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>/edges/&lt;population_name&gt;/&lt;group-id2&gt;/dynamics_params/edge_param2</td>
    <td>Dataset {K_edges}</td>
  </tr>
  <tr>
    <td>...</td>
    <td>Dataset {K_edges}</td>
  </tr>
</table>


Table 2: Layout of the file format for describing edges.

##### Edges - Required Attributes

**edge_type_id** -  Like the node_type_id, this is a unique integer to associate an edge to an edge type.  An edge type has associated attributes, and an edge inherits attributes from its edge type.  Attributes associated to an edge override attributes inherited from the edge type.  edge_type_ids need not be ordered or contiguous, but must be unique.  A reference implementation might be to use a id-value store, such as a dictionary to associate a edge_type_id with its associated attribute values.

**source_node_id** - Specifies the sender node id of the connection. The "node_population" attribute of this dataset specifies the name of the source node population in which the node is valid.

**target_node_id** - Specifies the receiver node id of the connection. The "node_population" attribute of this dataset specifies the name of the target node population in which the node is valid.

**edge_group_id** - Assigns each edge to a specific group of edges.

**edge_group_index** - After determining the edge_group_id of a specific edge, the edge_group_index indicates the index within that <edge-group-id> that contains all the attributes for a particular edge under consideration.

**edge_id** - Assigns a key to uniquely identify and look up an edge within a population. If If not provided, edge_ids are implicitly contiguous starting from zero.

#### Edges - Optional Reserved Attributes

**delay** - Axonal delay when the synaptic event begins relative to a spike from the presynaptic source.  Units depend on the application; for example, in NEURON-based simulations, the expected units are milliseconds (ms).

**syn_weight** - Strength of the connection between the source and target nodes. The units depend on the requirements of the target mechanism. For example, if the target mechanism is NEURON's Exp2Syn, then the syn_weight is interpreted as a peak conductance measured in microSiemens (uS)

**afferent_section_id**- The specific section on the target node where a synapse is placed.

**afferent_section_pos** - Given the section of where a synapse is placed on the target node, the position along the length of that section a (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section).

**efferent_section_id** - Same as **afferent_section_id**, but for source node.

**efferent_section_pos** - - Same as **afferent_section_pos**, but for source node.

**dynamics_params** - Contains the dynamic parameter overrides for edges. This can exist in the edge types CSV file in which case a .json file is referenced. Alternatively, it can be in the edges HDF5 file for each edge group as a dynamics_params HDF5 group containing datasets, one for each parameter  (see Table 2).  The namespace of parameters is defined as the namespace of the template.  Overrides specified at the level of the HDF5 file take precedence over overrides specified at the edge_type level.

**model_template** - String name of the template to create an object from parameters in dynamics_params. Can have NULL entries.

**afferent_center_position** - For edges that represent synapses in morphologically detailed networks, this attributes specified the x, y, z position in network global spatial coordinates of the synapse along the dendrite axis of the post-synaptic neuron. For synapses on the soma this location is at the soma center.

**afferent_surface_position** - Same as afferent_center_position, but the for the synapse location on the soma or dendrite surface.

**efferent_center_position** - Same as afferent_center_position but for the synapse position at the axon of the presynaptic cell.

**efferent_surface_position** - Same as efferent_center_position, but the for the synapse location on the axon surface

Note, that similar to the nodes description, if a variable exists in both the edges HDF5 file and the edge_types CSV file, then the HDF5 file will override the latter.

##### Edges - Optional indexing

The edge populations as defined above only allow fast enumeration of the edges from one node population to another population, but finding out the target nodes of a given source node or vice-versa cannot be performed in sublinear time. This optional extension of an edge file provides an indexing scheme that allows to query the source or target nodes of a given node more efficiently. This specification is based on the Syn2 proposal from BBP (NOTE:  https://github.com/adevress/syn2_spec).

The indexing has been designed for networks where if two nodes are connected, they tend to have multiple edges connecting them (multi-synapse connections in detailed morphology networks). For single edge networks this index has excessive overhead. For maximum space and time efficiency, edges connecting two nodes should be contiguous in the edge population. In any case, the index allows edges between different nodes to be placed in any order in the population datasets.

The indexing is rooted at a single group called indices which is a subgroup of an edge population group. For convenience, the prefix /edges/*<population_name>*/indices/ is stripped from the following layout description:

<table>
  <tr>
    <td>source_to_target</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>source_to_target/node_id_to_ranges</td>
    <td>Dataset {N_source_nodes x 2}, 64-bit integer</td>
  </tr>
  <tr>
    <td>source_to_target/range_to_edge_id</td>
    <td>Dataset {N_source_nodes x 2}, 64-bit integer</td>
  </tr>
  <tr>
    <td>target_to_source</td>
    <td>Group</td>
  </tr>
  <tr>
    <td>target_to_source/node_id_to_ranges</td>
    <td>Dataset {N_target_nodes x 2}, 64-bit integer</td>
  </tr>
  <tr>
    <td>target_to_source/range_id_edge_id</td>
    <td>Dataset {N_nodes x 2}, 64-bit integer</td>
  </tr>
</table>


The dataset source_to_target/node_id_to_ranges is indexed by source node_id, for each node_id it contains 2 columns that represent a slice in the source_to_target/range_to_edge_id dataset. The first value is the start index of the slice, and the second one is the non-inclusive end index. If the start index is a negative value, it means that there are no edges for the associated node_id.

The source_to_target/range_to_edge_id dataset defines ranges of edges in the edge population where each range contains edges whose source node is the same (the target node should also be the same for compactness). This dataset is meant to be indexed with the indices from node_id_to_range. For each row the two values define the start index of the range and the non-inclusive end index.

The datasets from the target_to_source group are defined symmetrically. From this symmetry is easy to infer that edges should be grouped by source, target pairs, otherwise an important overhead will be incurred in one or both of the indices.

### <a name="neuron_config">Tying it all together - the network/circuit config file

The config file is a .json file that defines the relative location of each part of the network:

    {
        "target_simulator":"NEURON",

target_simulator can be "NEURON", “PyNN”, “NEST”, etc.  It specifies the intended target simulator of the circuit description.  For now, this field is intended as a declaration, and an implementation may decide to throw an error for unsupported targets.  In practice, mechanism and parameter names are tailored to the given target simulator.  For model_type=biophysical NEURON is supported, but not PyNN or NEST.

The "manifest" section of the config file provides a convenient handle on setting variables that point to base paths.  These variables can be then used in the rest of the config file to point to various directories that share the first portion of the path.

        "manifest": {
            "$BASE_DIR": "/path/to/my/workspace",
            "$NETWORK_DIR": "$BASE_DIR/networks",
            "$COMPONENT_DIR": "$BASE_DIR/components"
        },
        "components": {

The directory in which to find the neuronal morphology files:

            "morphologies_dir": "$COMPONENT_DIR/morphologies",

The directory in which to find the edge_types and point neuron node_types dynamics_params .json files, respectively:

            "synaptic_models_dir": "$COMPONENT_DIR/synapse_dynamics",
            "point_neuron_models_dir": "$COMPONENT_DIR/point_neuron_dynamics",

Mechanisms may need to be compiled in advance, depending on implementation.  This field is optional, and is relevant for NEURON networks:

            "mechanisms_dir":"$COMPONENT_DIR/mechanisms",

Where to find the .nml for biophysical neuron model types:

            "biophysical_neuron_models_dir": "$COMPONENT_DIR/biophysical_neuron_dynamics",

Where to find the hoc templates for the edges:

           "templates": "$COMPONENT_DIR/hoc_templates",
        },

The network is defined by nodes and edges. In the example below, a V1 model is being simulated (with recurrent connections) that receives input from virtual LGN source nodes. Each population of nodes should contain "nodes" and “node_types” while each population of edges should “edges”, “edge_types”.  Gids are assigned to nodes in advance (using another tool) or during the simulation, depending on implementation, and are global across all  populations in the network (see the (gid mapping)[#gid_mapping] section for details)

        "networks": {
            "nodes": [
                {
                    "nodes_file":       "$NETWORK_DIR/V1/v1_nodes.h5",
                    "node_types_file":  "$NETWORK_DIR/V1/v1_node_types.csv"
                },
                {
                    "nodes_file":       "$NETWORK_DIR/LGN/lgn_nodes.h5",
                    "node_types_file":  "$NETWORK_DIR/LGN/lgn_node_types.csv"
                }
            ],
            "edges":[
                {
                    "edges_file":       "$NETWORK_DIR/V1/v1_edges.h5",
                    "edge_types_file":  "$NETWORK_DIR/V1/v1_edge_types.csv"
                },
                {
                    "edges_file":       "$NETWORK_DIR/LGN/lgn_v1_edges.h5",
                    "edge_types_file":  "$NETWORK_DIR/LGN/lgn_v1_edge_types.csv"
                }
            ]
        }
    }

## <a name="simulations">Representing Simulations

The simulation config file is a json file which ties together the definition of a simulation on a circuit.  It specifies the circuit to be used, simulator parameters, load balancing and time stepping information, stimuli (simulation input), reports (simulation output), and the specification of neuron targets (sub groups of neurons) in a node_sets_file.  Like the circuit_config.json, the simulation_config.json may contain a "manifest" block which defines paths to be re-used elsewhere in the .json file:

    "manifest": {
        "$BASE_DIR": "/path/to/my/workspace",
        "$OUTPUT_DIR": "$BASE_DIR/output",
        "$INPUT_DIR": "$BASE_DIR/input",
        "$NETWORK_DIR": "$BASE_DIR/network",
        "$COMPONENT_DIR": "$BASE_DIR/components"
    },

### Specifying the Circuit/Network to Simulate

The circuit to simulate is specified by including a key "network", with value pointing to the circuit_config.json for which the simulation should be performed.

Example:

    "network": "${BASE_DIR}/circuit_config.json"

### Time Stepping Parameters

The "run" block specifies some global parameters of the simulation run, such as total duration

    "run": {
        "tstop": 3000.0,
        "dt": 0.1,
        "dL": 20,
        "spike_threshold": -15,
    },

### Conditions Configuration

This block specifies optional global parameters with reserved meaning associated with manipulation of the "in silico preparation".

Example:

    "conditions": {
        "celsius": 34.0,
        "v_init": -80
      },

### Output Configuration

The "output" block configures the location where output reports should be
written. An optional attribute named "overwrite_output_dir" provides a hint
to simulators to let them know if already existing output files must be
overwritten.

The default behaviour is for simulators to produce spike data (a series of
gid, timestamp pairs). By default the name of the file is "spikes.h5" and it
is written to <output_dir>. The name of the output file for spikes can be
configured with the optional attribute "spikes_file" (using a relative or
absolute path in spikes_file has undefined behaviour)

Example
    "output": {
        "log_file": "$OUTPUT_DIR/log.txt",
        "output_dir": "$OUTPUT_DIR",
        "overwrite_output_dir": true,
        "spikes_file": "run0.h5",
    },


### Implementation Specific Parameters

Implementations of software interpreting the simulation config may need to embed additional sections defined by key:dict so long as the key does not collide with any keys with reserved meaning in the simulation config.  Some examples may include simulator or implementation specific parameters, such as load balancing hints, numerical methods, parallelization approaches, etc.

### Specifying Targets - Sub-groups of Neurons

    "node_sets_file": "<node_sets_file>"

See below "Node Sets File".

### Simulation input - Stimuli

The "inputs" block of the simulation config allows the definition of inputs to the simulation. There can be one or more inputs defined in this block.ells Cells in the circuit may receive multiple inputs and others may receive no input.

    {
        "inputs": {
            "<input_name_1>": {
                "<Key1>": <Value1>,
                "<Key2>": <Value2>,
                ...
            },
            "input_name_2>": {
                "<Key1>": <ValueN>,
                ...
            }
        }
    }

<table>
  <tr>
    <td>Key</td>
    <td>Description</td>
    <td>Type</td>
    <td>Required</td>
    <td>Default</td>
  </tr>
  <tr>
    <td>input_type</td>
    <td>Defines the type of the input with the reserved values :
"spikes",
”extracellular_stimulation”,
”current_clamp”,
”voltage_clamp”</td>
    <td>string </td>
    <td>True</td>
    <td> </td>
  </tr>
  <tr>
    <td>input_file</td>
    <td>Name of the file containing the time course of the data</td>
    <td>string</td>
    <td>False</td>
    <td></td>
  </tr>
  <tr>
    <td>trial</td>
    <td>Name of the trial from the “input_file”</td>
    <td>string</td>
    <td>False</td>
    <td></td>
  </tr>
  <tr>
    <td>module</td>
    <td>The module that is used to process the “input_file” to create the input.</td>
    <td>string</td>
    <td>True</td>
    <td> </td>
  </tr>
  <tr>
    <td>electrode_file</td>
    <td>The name of the file describing properties of the stimulating electrode(s)</td>
    <td>string</td>
    <td>False</td>
    <td></td>
  </tr>
  <tr>
    <td>node_set</td>
    <td>The name of the  node_set defining the input.  In some cases, such as spike input types, all members of the node_set should be model_type=“virtual”.  </td>
    <td>string</td>
    <td>False</td>
    <td></td>
  </tr>
  <tr>
    <td><model_specific_key></td>
    <td>Each module can define their own optional or required key:value pairs</td>
    <td>Model specific</td>
    <td>Module specific</td>
    <td></td>
  </tr>
</table>

The source_file may point to either the nodes file ( type:"spikes”) or the electrode file ( type:”extracellular stimulation”,”current_clamp”,”voltage_clamp”.) The input from the sources may be defined as a set of parameters (e.g., amplitude, tstart, tstop) or as a collection of  time courses (e.g., a time trace of a current). In the former, the parameters are specified in the source file, in the latter they are specified in the time_course_file.

Examples:

        "inputs": {
            "LGN_spikes_from_nwb":
            {
                "input_type": "spikes",
                "module": "nwb",
                "input_file": "$INPUT_DIR/lgn_spikes.nwb",
                "node_set": ”LGN”
                "trial": "trial_0"
            },
            "background_spikes_poisson":
            {
                "input_type": "spikes",
                "module": "poisson"
                "input_file":"$INPUT_DIR/BKG/bkg_input.csv",
                "node_set": ”BKG”
            },
            "V1_input_current_from_nwb":
            {
                "input_type": "voltage_clamp"
                "module": "SEClamp",
                "electrode_file": "el2.csv",
                "input_file": "el2.nwb",
                "trial": "trial_0"
            },
            "V1_input_current_parametric":
            {
                "input_type": "current_clamp",
                "module": "IClamp",
                "electrode_file": "el1.csv"
                "input_file": "el1_input_trial01.csv"
            },
            "V1_extracellular_current_from_h5":
            {
                "input_type": "extracellular_current",
                "module": "extra_stim_h5",
                "electrode_file": "exel.csv",
                "input_file": "exel_time_course.h5",
                "trial": "trial_0"
            }
        },

Examples of the electrode_file for current clamp stimulation (column names):

* electrode_id
* node_id
* population
* sec_id
* seg_x

Example of the corresponding input_file (column names):

* electrode_id
* dur
* amp
* delay
* i

### Simulation output - Reports

The output of the simulation is reported based on the specifications of the
output variables described in the simulation configuration file under the
"reports" block.

There can be one or more reports in the block, each one identified by a unique name:

        "reports": {
            "<report_name_1>": {
                "<Key1>": <Value1>,
                "<Key2>": <Value2>,
                ...
            },
            "<report_name_2>": {
                "<Key1>": <ValueN>,
                ...
            }
        }

Simulators are expected to create a file for each specified report under the
output directory using the file name <report_name>.<ext>, where ext is the
file extension specific to the report configuration. The file name can be
overriden with the attribute "file_name".

Some reserved attributes are the following:

<table>
  <tr>
    <td>Key</td>
    <td>Description</td>
    <td>Type</td>
    <td>Required</td>
    <td>Default</td>
  </tr>
  <tr>
    <td>cells</td>
    <td>Defines what cells will be reported. The value is a reference to a cell-group found in the cell-groups json file, which is used to resolve which subset of gids will be included in the report. </td>
    <td>string (cell-group)</td>
    <td>True</td>
    <td> </td>
  </tr>
  <tr>
    <td>start_time</td>
    <td>Time to start reporting in milliseconds</td>
    <td>float</td>
    <td>False</td>
    <td>'run'/'tstart' or 0</td>
  </tr>
  <tr>
    <td>format</td>
    <td>ASCII, HDF5 or Bin defining report output format</td>
    <td>string</td>
    <td>False</td>
    <td>HDF5</td>
  </tr>
  <tr>
    <td>variable_name</td>
    <td>The Simulation variable to access</td>
    <td>string</td>
    <td>True</td>
    <td> </td>
  </tr>
  <tr>
    <td>dt</td>
    <td>Frequency of reporting in milliseconds</td>
    <td>float</td>
    <td>False</td>
    <td>'run'/'dt'</td>
  </tr>
  <tr>
    <td>end_time</td>
    <td>Time to stop reporting in milliseconds</td>
    <td>float</td>
    <td>False</td>
    <td>'run'/'tstop'</td>
  </tr>
  <tr>
    <td>sections</td>
    <td>For compartment reporting, specify a given section to report – dependent on the model setup. To report on all sections, use the keyword 'all'.</td>
    <td>string</td>
    <td>False</td>
    <td>'soma'</td>
  </tr>
  <tr>
    <td>electrode_channels</td>
    <td>For extracellular recording, specify a list of channels or 'all'.</td>
    <td>channels</td>
    <td>False</td>
    <td>'all'</td>
  </tr>
  <tr>
    <td>unit</td>
    <td>String to output as descriptive test for unit recorded. Not validated for correctness</td>
    <td>string</td>
    <td>False</td>
    <td>Simulator default</td>
  </tr>
  <tr>
    <td>file_name</td>
    <td>Report file name including extension. Reports are always written to the
      output directory given in the output configuration block</td>
    <td>string</td>
    <td>False</td>
    <td>-</td>
  </tr>

</table>


#### **Example**

        "reports": {
            "calcium_bio": {
                "cells": "biophysical",
                "variable_name": "cai",
                "module": "membrane_report",
                "sections": "all",
                "start_time": 0.0,
                "end_time": 500.0,
                "dt": 0.25
            },
            "membrane_voltage": {
                "cells":  "all_cells",
                "variable_name": "v",
                "module": "membrane_report",
                "sections": "soma"
            },
            "extracellular_potential": {
                "cells": "all_cells",
                "variable_name": "ecp",
                "module": "extracellular",
                "sections": "all",
                "electrode_channels": "all"
            },
            "voltage_clamp": {
                "cells": "biophysical",
                "variable_name": "i",
                "module": "SEClamp",
                "sections": "soma"
            },
        },


#### **Node Sets** File

A Node Sets json file contains subsets of cells that act as targets for
different reports or stimulations, or can also be used to name and define the
target subpopulation to simulate. The top level element in the json schema
is a dictionary with one entry per node set. The keys are the node set names
and the values and depends on whether a node set is basic or compound.

The general schema is as follows.

    {
        "<Basic_Node_Set_1>": {
            "<Property_Key1>": ["<Prop_Val_11>", "<Prop_Val_12>", ...],
            "<Property_Key2>": ["<Prop_Val_21>", "<Prop_Val_22>", ...],
        },
        ...
        "<Compound_Node_Set_N>": [<Basic_Node_Set_1>, <Compound_Node_Set_M>, ...],
        ...
    }

Basic node sets are declared using a dictionary of node attributes and
attribute values. An attribute value can be either a scalar (number, string,
bool) or an array of scalars. Scalar values in the json must be compatible
with the H5 types in the node files according to the following equivalence:

|  Json  |             H5            |
|--------|---------------------------|
| number | H5T_IEEE_*LE, H5T_STD_*LE |
| string | H5T_C_S1                  |
|  bool  | H5T_STD_I8LE              |
|  null  | **invalid**               |

Each entry specifies a rule. For scalar attributes a node matches the rule if
the value of its attribute matches the value in the entry. For arrays, a node
matches if its value matches any of the values in the array. A node is part of
a node set if it matches all the rules in the node set definition (logical
AND).

Compound node sets are declared as an array of node sets names, where each name
may refer to another compound node set or a basic node set. The final node set
is the union of all the node sets in the array.

Two special attributes are allowed in the key-value pairs of basic node sets.
The first one is "population", this attribute refers to the node populations
to be considered. Node populations and their names are implicitly defined in
the Node Set namespace, and needn’t be declared explicitly.

At time of interpretation of the node set file, gids must also be defined for
each node in the network to be simulated. For that purpose, "gid" is also a
valid node attribute to appear in key-value pairs. The "gid" to population and
node_id mapping is specified according to [description below](#gid_mapping).


##### An Example of a Node Set File

    {
        "bio_layer45": {
            "model_type": "biophysical",
            "location": ["layer4", "layer5"]
        },
        "V1_point_prime": {
            "population": "biophysical",
            "model_type": "point",
            "node_id": [1, 2, 3, 5, 7, 9, ...]
        }
        "layer4": {
            "gids": [1, 2, 3, 4, 5, ...]
        },
    }

### **Output file formats**

Each report name in the "reports" block results in a separate HDF5 file with
the filename <report_name>.h5 written to the output directory (unless the user
provides a different file name).

#### <a name="spike_file"></a>Spike file

Spikes from all cells will be stored in a single HDF5 file that contains (gid, spike time) pairs in separate datasets. These datasets may be unsorted, sorted by gid or sorted by spike time. The gids are not to be confused with node_ids from populations, see below for details about gid to node_id and population mapping.

The layout of a spike file is as follows:

* **/spikes** (group), attributes:
    - **sorting** (dtype: enum) Optional. It can take one of these
    values: `none`, `by_gid`, `by_time`. Both datasets below are sorted using
    as sorting key the dataset specified by the attribute. When sorting by gid,
     spikes of the same gid are expected to be also sorted by timestamp as
     secondary key. When sorting by timestamp, spikes with the same timestamp
     can be in any order. If missing, no sorting can be assumed.
* **/spikes/timestamps** (dytpe: double, shape: N spikes), attributes:
    - **units** (dytpe: str)
* **/spikes/gids** (dytpe: uint64, shape: N spikes), attributes:

#### Frame oriented, cell element recordings

Used when recording simulation data from elements from one or more cells.
The reported elements are usually the electrical compartments, but other
elements such as synapses could also be reported. The only requisite is that
the cell elements can be identified by an element identifier composed by an
integer and an optional float value.

* **/data** (dtype:float, shape: N_time x N_values). Writers are
  encouraged to use chunking for efficient read access. Attributes:
    - **units** (dtype: str)
* **/mapping/gids** (dtype: uint64, shape: N_cells). Attributes:
    - **sorted** (dtype: bool) Optional. Indicates whether the GID list is
      sorted or not. The list is considered unsorted if not present.
* **/mapping/index_pointer** (dtype: uint64, shape: N_cells)
* **/mapping/element_id** (dtype: uint32, shape: N_values). All
  values referring to the same element must appear together.
* **/mapping/element_pos** (dtype: float, shape: N_values). Optional
* **/mapping/time** (dtype: double, shape: 3),
  the values of the data set are start time, stop time and time step. The
  interval is open on the right (i.e. no data frame for t=stop). Attributes:
    - **units** (dtype: str)

For a particular gid[ix], the data for all the recorded elements is
determined by `data[index_pointer[ix], index_pointer[ix+1]]`.

For compartment reports, the values in `element_id[index_pointer[ix],
index_pointer[ix+1]]` and `element_pos[index_pointer[ix], index_pointer[ix+1]]`
are used to specify the compartment’s section id and the relative position,
respectively, for each gid[ix]’s data column. Note that for single compartment
reports `element_id` and `element_pos` are just arrays of 1s. If the
`element_pos` dataset is not present, for every recorded section all its
compartments will be reported and they will appear in the dataset in
morphological order.

#### Extracellular report

Used when reporting variables that are not associated with the individual cells.

**Extracellular_potential**

* **data** (dtype: float, shape: N_rec_electrodes x N_time), attributes:
     - *units*: str
* **channel_id** (dtype: int, shape: N_rec_electrodes)
* **time** (dtype: double, shape: 3),
  the values of the data set are start time, stop time and time step. The
  interval is open on the right (i.e. no data frame for t=stop). Attributes:
     - *units*: str

The data for a particular electrode channel_id[i] found in data[i,:]

### <a name="gid_mapping"></a> Mapping between gids and cells in the network

In the model description, the cells are uniquely defined by their population name and node_id, whereas in the simulation output they are uniquely defined by the gids. To relate the two, we need to have a mapping: (population,node_id) <-> gid

The mapping could be created by the simulator or prior to simulation (implementation specific) and stored as an HDF5 file having 3 datasets:

**GlobalReferencing**

* **gid** (dtype: uint64, shape: N_gid)
* **population** (dtype: uint32, shape: N_gid)
* **node_id** (dtype: uint32, shape: N_gid)
* **population_names**(dtype: str, shape: N_population)

One can search these datasets to find gid corresponding to a particular (population, node_id) pair or vice versa. The population dataset contains indices in the population_names dataset.

The location of the mapping file is specified in the simulation_config.json as follows:

    {
        "gid_mapping_file": ”<path_to_h5>”
    }

For implementations that generate the mapping at runtime, this location should be used to write the file.

## <a name="appendix">Appendix

### Background material

See CodeJam talks on this topic:

[http://neuralensemble.org/media/slides/Sergey_Gratiy_bionet_representation.pdf](http://neuralensemble.org/media/slides/Sergey_Gratiy_bionet_representation.pdf)

[http://neuralensemble.org/media/slides/bluepy.pdf](http://neuralensemble.org/media/slides/bluepy.pdf)

### Valid Values for "model_processing"

model_processing is a string attribute of nodes allowing the specification of alternative

processing approaches in the model construction behaviour of biophysical neurons. The following values are currently defined (more will be defined in the future, as required).  It is currently not valid to specify this attribute for model_type != "biophysical”.

For model_processing=*"fullaxon",* the biophysical neuron will construct and simulate the full axon. This is the default behaviour if model_processing is undefined for a given node.

For model_processing="axon_bbpv5", the axon is removed, and is replaced by two cylindrical sections of 30 μm each, representing the axon initial segment (AIS).

The diameter of the first section is determined by the diameter at midpoint of the first section of the original axon. The diameter of the second section is the diameter at midpoint of the first original axon section who’s midpoint crosses 60 μm. If the latter section doesn’t exist in the original morphology, the second section gets the same diameter as the first section.

For model_processing="axon_bbpv6”, a new axon initial segment (AIS) consisting of 2 sections of 30 micron each is created. Each of these sections has 5 segments (nseg=5 in NEURON). Record all the segment diameters and lengths (at midpoint) for the entire original axon. Make sure the number of segments of each section in the original morphology is set in such a way that every 6 micron (i.e. 60 micron divided by 2 times 5 segments), a new segment is added. Delete the original axon and replace it with the AIS. Loop over both the segments of the AIS and the diameters of the original axon morphology. Assign diameters according to the original morphology. After the 2 AIS sections, add one myelinated section (section called 'myelin', not 'axon') with a length of 1000 micron, and use the diameter of the last segment in the original axon.

For model_processing="axon_bbpv6nomylin”, same as ”axon_bbpv6”, but no "myelin” section is added after the 2 AIS sections.

For model_processing="aibs_perisomatic”, the axon is removed, and is replaced by two cylindrical sections of 30 μm each connected to soma(0.5), representing the axon initial segment (AIS). The diameter of the sections is set to 1 μm.

For model_processing="...”, ...

### Model Template Structure

For the case that the model_template follows the *hoc* schema, the following is the expected structure of the hoc template.

Allen folks to fill in

For the case that the model_template follows the *bmtk* schema, the following is the expected structure of the hoc template.

Allen folks to fill in

