import os
import numpy as np

from bmtk.builder.networks import NetworkBuilder


net = NetworkBuilder("ten_cells_spikes")


net.add_nodes(N=30, pop_name='VirtualCells', ei='e', location='TW', model_type='virtual')

net.add_nodes(N=24, pop_name='Exc', location='VisL4', ei='e',
              model_type='point_process',  # use point_process to indicate were are using point model cells
              model_template='nrn:IntFire1',  # Tell the simulator to use the NEURON built-in IntFire1 type cell
              dynamics_params='IntFire1_exc_1.json')
'''
net.add_nodes(N=6, pop_name='LIF_inh', location='VisL4', ei='i',
              model_type='point_process',
              model_template='nrn:IntFire1',
              dynamics_params='IntFire1_inh_1.json')'''
              

def recurrent_connections(src_cells, trg_cell, n_syns):
    if np.random.random() > .5:
        synapses = [n_syns]*len(src_cells)
    else:
        synapses = [None]*len(src_cells)
    return synapses

def recurrent_connections_low(src_cells, trg_cell, n_syns):
    
    synapses = [n_syns*(np.random.random() > .1) for i in range(len(src_cells))]
 
    return synapses

def recurrent_connections_low2(src_cells, trg_cell, n_syns):

    synapses = [n_syns*(np.random.random() > .1) for i in range(len(src_cells))]
    
    return synapses

'''              
net.add_edges(source=net.nodes(pop_name='VirtualCells'), target=net.nodes(pop_name='Exc'),
             iterator='all_to_one',
             connection_rule=recurrent_connections_low,
             connection_params={'n_syns': 1},
             syn_weight=0.5,
             weight_function='wmax',
             delay=0.0,
             dynamics_params='instanteneousExc.json')'''
             

'''
net.add_edges(source={'ei': 'i'}, target={'ei': 'i', 'model_type': 'point_process'},
              iterator='all_to_one',
              connection_rule=recurrent_connections,
              connection_params={'n_syns': 10},
              syn_weight=0.01,
              weight_function='wmax',
              delay=0.0,
              dynamics_params='instanteneousInh.json')



net.add_edges(source={'ei': 'i'}, target={'ei': 'e', 'model_type': 'point_process'},
              iterator='all_to_one',
              connection_rule=recurrent_connections,
              connection_params={'n_syns': 10},
              syn_weight=0.15,
              weight_function='wmax',
              delay=0.0,
              dynamics_params='instanteneousInh.json')


net.add_edges(source={'ei': 'e'}, target={'pop_name': 'LIF_inh'},
              iterator='all_to_one',
              connection_rule=recurrent_connections,
              connection_params={'n_syns': 10},
              syn_weight=0.3,
              weight_function='wmax',
              delay=0.0,
              dynamics_params='instanteneousExc.json')


net.add_edges(source={'ei': 'e'}, target={'pop_name': 'LIF_exc'},
              iterator='all_to_one',
              connection_rule=recurrent_connections_low2,
              connection_params={'n_syns': 1},
              syn_weight=0.002,
              weight_function='wmax',
              delay=2.0,
              dynamics_params='instanteneousExc.json')
'''

net.build()



def generate_positions(N, x0=0.0, x1=300.0, y0=0.0, y1=100.0):
    X = np.random.uniform(x0, x1, N)
    Y = np.random.uniform(y0, y1, N)
    return X, Y


'''
tw = NetworkBuilder("tw")
tw.add_nodes(N=30, pop_name='TW', ei='e', location='TW', model_type='virtual')

tw.add_edges(source=tw.nodes(), target=net.nodes(pop_name='LIF_exc'),
             iterator='all_to_one',
             connection_rule=recurrent_connections_low,
             connection_params={'n_syns': 1},
             syn_weight=0.5,
             weight_function='wmax',
             delay=0.0,
             dynamics_params='instanteneousExc.json')


tw.add_edges(source=tw.nodes(), target=net.nodes(pop_name='LIF_inh'),
             connection_rule=1,
             syn_weight=0.2,
             weight_function='wmax',
             delay=0.0,
             dynamics_params='instanteneousExc.json')

tw.build()
tw.save(output_dir='../input/network')'''

net.save(output_dir='../input/network')


print 'done'