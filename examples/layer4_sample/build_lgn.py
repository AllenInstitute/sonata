import os
import csv
import math
import numpy as np
from random import *
from build_helpers import *

from bmtk.builder.networks import NetworkBuilder
from bmtk.builder.bionet import SWCReader


positions_table, offset_table = read_dat_file('lgn_positions.csv') # file containing cell positions
cell_models = {
    'tON_001': {
        'N': len(positions_table['tON_001']), 'ei': 'e', 'location': 'LGN',
        'model_type': 'virtual', 'pop_name': 'tON', 'pop_id': 'tON_001'
    },
    'tOFF_001': {
        'N': len(positions_table['tOFF_001']),'ei': 'e', 'location': 'LGN',
        'model_type': 'virtual', 'pop_name': 'tOFF', 'pop_id': 'tOFF_001'
    },
    'tONOFF_001': {
        'N': len(positions_table['tONOFF_001']), 'ei': 'e', 'location': 'LGN',
        'model_type': 'virtual', 'pop_name': 'tONOFF', 'pop_id': 'tONOFF_001'
    }
}

lgn_net = NetworkBuilder('lgn')
xcoords = []
ycoords = []
for model_name, model_params in cell_models.items():
    positions = positions_table[model_name]
    xcoords += [p[0] for p in positions]
    ycoords += [p[1] for p in positions]
    tuning_angles = [calc_tuning_angle(o) for o in offset_table[model_name]]

    lgn_net.add_nodes(model_params['N'],
                      # position=positions,
                      x=[p[0] for p in positions],
                      y=[p[1] for p in positions],
                      tuning_angle=tuning_angles,
                      ei=model_params['ei'],
                      location=model_params['location'],
                      model_type=model_params['model_type'],
                      pop_name=model_params['pop_name'],
                      pop_id=model_params['pop_id'])

lgn_net.build()
lgn_net.save_nodes(output_dir='network')


v1_net = NetworkBuilder('l4')
v1_net.import_nodes('network/l4_nodes.h5', 'network/l4_node_types.csv')

morphologies = {n['model_name']: SWCReader(os.path.join('../shared_components/morphologies', n['morphology']))
                                 for n in v1_net.nodes() if 'morphology' in n and n['morphology']}
def build_edges(src, trg, sections=['basal', 'apical'], dist_range=[50.0, 150.0]):
    """Function used to randomly assign a synaptic location based on the section (soma, basal, apical) and an
    arc-length dist_range from the soma. This function should be passed into the network and called during the build
    process.

    :param src: source cell (dict)
    :param trg: target cell (dict)
    :param sections: list of target cell sections to synapse onto
    :param dist_range: range (distance from soma center) to place
    :return:
    """
    # Get morphology and soma center for the target cell
    swc_reader = morphologies[trg['model_name']]
    target_coords = [trg['x'], trg['y'], trg['z']]

    sec_ids, sec_xs = swc_reader.choose_sections(sections, dist_range)  # randomly choose sec_ids
    coords = swc_reader.get_coord(sec_ids, sec_xs, soma_center=target_coords)  # get coords of sec_ids
    dist = swc_reader.get_dist(sec_ids)
    swctype = swc_reader.get_type(sec_ids)
    return sec_ids, sec_xs, coords[0][0], coords[0][1], coords[0][2], dist[0], swctype[0]


lgn_mean = (np.mean(xcoords), np.mean(ycoords))
lgn_dim = (140.0, 70.0)

# Determine the mean center of the CC cells
xcoords = [n['x'] for n in v1_net.nodes()]
ycoords = [n['y'] for n in v1_net.nodes()]
zcoords = [n['z'] for n in v1_net.nodes()]
l4_mean = (np.mean(xcoords), np.mean(ycoords), np.mean(zcoords))
l4_dim = (max(xcoords) - min(xcoords), max(ycoords) - min(ycoords), max(zcoords) - min(zcoords))


cparams = {'lgn_mean': lgn_mean, 'lgn_dim': lgn_dim, 'l4_mean': l4_mean, 'l4_dim': l4_dim, 'N_syn': 30}
cm = v1_net.add_edges(source=lgn_net.nodes(), target={'model_name': 'Rorb'},
                      iterator='all_to_one',
                      connection_rule=select_source_cells,
                      connection_params=cparams,
                      delay=2.0,
                      dynamics_params='AMPA_ExcToExc.json',
                      model_template='exp2syn')
cm.add_properties('syn_weight', rule=5e-05, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['basal', 'apical'], 'dist_range': [0.0, 150.0]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

cm = v1_net.add_edges(source=lgn_net.nodes(), target={'model_name': 'Nr5a1'},
                      iterator='all_to_one',
                      connection_rule=select_source_cells,
                      connection_params=cparams,
                      delay=2.0,
                      dynamics_params='AMPA_ExcToExc.json',
                      model_template='exp2syn')
cm.add_properties('syn_weight', rule=5e-05, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['basal', 'apical'], 'dist_range': [0.0, 150.0]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

cm = v1_net.add_edges(source=lgn_net.nodes(), target={'model_name': 'Scnn1a'},
                      iterator='all_to_one',
                      connection_rule=select_source_cells,
                      connection_params=cparams,
                      delay=2.0,
                      dynamics_params='AMPA_ExcToExc.json',
                      model_template='exp2syn')
cm.add_properties('syn_weight', rule=4e-05, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['basal', 'apical'], 'dist_range': [0.0, 150.0]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])


cm = v1_net.add_edges(source=lgn_net.nodes(), target={'model_name': 'PV1'},
                      iterator='all_to_one',
                      connection_rule=select_source_cells,
                      connection_params=cparams,
                      delay=2.0,
                      dynamics_params='AMPA_ExcToInh.json',
                      model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.0001, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['somatic', 'basal'], 'dist_range': [0.0, 1.0e+20]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

cm = v1_net.add_edges(source=lgn_net.nodes(), target={'model_name': 'PV2'},
                      iterator='all_to_one',
                      connection_rule=select_source_cells,
                      connection_params=cparams,
                      delay=2.0,
                      dynamics_params='AMPA_ExcToInh.json',
                      model_template='exp2syn')
cm.add_properties('syn_weight', rule=9e-05, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['somatic', 'basal'], 'dist_range': [0.0, 1.0e+20]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

cm = v1_net.add_edges(source=lgn_net.nodes(), target={'model_name': 'LIF_exc'},
                      iterator='all_to_one',
                      connection_rule=select_source_cells,
                      connection_params=cparams,
                      delay=2.0,
                      dynamics_params='instanteneousExc.json')
cm.add_properties('syn_weight', rule=0.0045, dtypes=np.float)

cm = v1_net.add_edges(source=lgn_net.nodes(), target={'model_name': 'LIF_inh'},
                      iterator='all_to_one',
                      connection_rule=select_source_cells,connection_params=cparams,
                      delay=2.0,
                      dynamics_params='instanteneousExc.json')
cm.add_properties('syn_weight', rule=0.002, dtypes=np.float)

v1_net.build()
v1_net.save_edges(output_dir='network')
