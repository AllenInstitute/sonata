import os
import numpy as np

from bmtk.builder.networks import NetworkBuilder


# Step 1: Create a v1 mock network of 14 cells (nodes) with across 7 different cell "types"
net = NetworkBuilder("v1")

net.add_nodes(N=240, pop_name='LIF_exc', location='VisL4', ei='e',
              model_type='point_process',  # use point_process to indicate were are using point model cells
              model_template='nrn:IntFire1',  # Tell the simulator to use the NEURON built-in IntFire1 type cell
              dynamics_params='IntFire1_exc_1.json')

net.add_nodes(N=60, pop_name='LIF_inh', location='VisL4', ei='i',
              model_type='point_process',
              model_template='nrn:IntFire1',
              dynamics_params='IntFire1_inh_1.json')

def recurrent_connections(src_cells, trg_cell, n_syns):
    if np.random.random() > 0.3:
        synapses = [n_syns]*len(src_cells)
    else:
        synapses = [None]*len(src_cells)
    return synapses


net.add_edges(source={'ei': 'i'}, target={'ei': 'i', 'model_type': 'point_process'},
              iterator='all_to_one',
              connection_rule=recurrent_connections,
              connection_params={'n_syns': 10},
              syn_weight=0.01,
              weight_function='wmax',
              delay=2.0,
              dynamics_params='instanteneousInh.json')



net.add_edges(source={'ei': 'i'}, target={'ei': 'e', 'model_type': 'point_process'},
              iterator='all_to_one',
              connection_rule=recurrent_connections,
              connection_params={'n_syns': 10},
              syn_weight=0.15,
              weight_function='wmax',
              delay=2.0,
              dynamics_params='instanteneousInh.json')


net.add_edges(source={'ei': 'e'}, target={'pop_name': 'LIF_inh'},
              iterator='all_to_one',
              connection_rule=recurrent_connections,
              connection_params={'n_syns': 10},
              syn_weight=0.3,
              weight_function='wmax',
              delay=2.0,
              dynamics_params='instanteneousExc.json')


net.add_edges(source={'ei': 'e'}, target={'pop_name': 'LIF_exc'},
              iterator='all_to_one',
              connection_rule=recurrent_connections,
              connection_params={'n_syns': 10},
              syn_weight=0.002,
              weight_function='wmax',
              delay=2.0,
              dynamics_params='instanteneousExc.json')


net.build()
net.save(output_dir='network')


def generate_positions(N, x0=0.0, x1=300.0, y0=0.0, y1=100.0):
    X = np.random.uniform(x0, x1, N)
    Y = np.random.uniform(y0, y1, N)
    return X, Y


def select_source_cells(src_cells, trg_cell, n_syns):
    if np.random.random() > 0.1:
        synapses = [n_syns if src['pop_name'] == 'tON' or src['pop_name'] == 'tOFF' else 0 for src in src_cells]
    else:
        synapses = [n_syns if src['pop_name'] == 'tONOFF' else 0 for src in src_cells]

    return synapses


lgn = NetworkBuilder("lgn")
pos_x, pos_y = generate_positions(30)
lgn.add_nodes(N=30, pop_name='tON', ei='e', location='LGN',
              x=pos_x, y=pos_y,
              model_type='virtual')

pos_x, pos_y = generate_positions(30)
lgn.add_nodes(N=30, pop_name='tOFF', ei='e', location='LGN',
              x=pos_x, y=pos_y,
              model_type='virtual')

pos_x, pos_y = generate_positions(30)
lgn.add_nodes(N=30, pop_name='tONOFF', ei='e', location='LGN',
              x=pos_x, y=pos_y,
              model_type='virtual')




lgn.add_edges(source=lgn.nodes(), target=net.nodes(pop_name='LIF_exc'),
              iterator='all_to_one',
              connection_rule=select_source_cells,
              connection_params={'n_syns': 10},
              syn_weight=0.0045,
              weight_function='wmax',
              delay=2.0,
              dynamics_params='instanteneousExc.json')

lgn.add_edges(source=lgn.nodes(), target=net.nodes(pop_name='LIF_inh'),
              iterator='all_to_one',
              connection_rule=select_source_cells,
              connection_params={'n_syns': 10},
              syn_weight=0.0015,
              weight_function='wmax',
              delay=2.0,
              dynamics_params='instanteneousExc.json')

lgn.build()
lgn.save(output_dir='network')


tw = NetworkBuilder("tw")
tw.add_nodes(N=30, pop_name='TW', ei='e', location='TW', model_type='virtual')

tw.add_edges(source=tw.nodes(), target=net.nodes(pop_name='LIF_exc'),
             connection_rule=5,
             syn_weight=0.01,
             weight_function='wmax',
             delay=2.0,
             dynamics_params='instanteneousExc.json')

tw.add_edges(source=tw.nodes(), target=net.nodes(pop_name='LIF_inh'),
             connection_rule=5,
             syn_weight=0.02,
             weight_function='wmax',
             delay=2.0,
             dynamics_params='instanteneousExc.json')

tw.build()
tw.save(output_dir='network')
print 'done'