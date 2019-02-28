import os
import numpy as np
import random
import math

from bmtk.builder.networks import NetworkBuilder
from bmtk.builder.bionet import SWCReader

# Percentage of 45,000 network to build, default to 1 percent (~ 450 cells)
PERCENTAGE_CELLS = 0.01
WEIGHT_ADJ = np.sqrt(1.0/PERCENTAGE_CELLS)

cell_models = [
    {
        'model_name': 'Scnn1a',
        'N': int(PERCENTAGE_CELLS*3700),
        'ei': 'e',
        'model_type': 'biophysical',
        'morphology': 'Scnn1a_473845048_m',
        'electrophysiology': '472363762_fit.json',
        'rotation_angle_zaxis': -3.646878266,
        'model_template': 'nml:Cell_472363762.cell.nml'
    },
    {
        'model_name': 'Rorb',
        'N': int(PERCENTAGE_CELLS*3300),
        'ei': 'e',
        'model_type': 'biophysical',
        'morphology': 'Rorb_325404214_m',
        'electrophysiology': '473863510_fit.json',
        'rotation_angle_zaxis': -4.159763785,
        'model_template': 'nml:Cell_473863510.cell.nml'
    },
    {
        'model_name': 'Nr5a1',
        'N': int(PERCENTAGE_CELLS*1500),
        'ei': 'e',
        'model_type': 'biophysical',
        'morphology': 'Nr5a1_471087815_m',
        'electrophysiology': '473863035_fit.json',
        'rotation_angle_zaxis': -2.639275277,
        'model_template': 'nml:Cell_473863035.cell.nml'
    },
    {
        'model_name': 'PV1',
        'N': int(PERCENTAGE_CELLS**800),
        'ei': 'i',
        'model_type': 'biophysical',
        'morphology': 'Pvalb_470522102_m',
        'electrophysiology': '472912177_fit.json',
        'rotation_angle_zaxis': -2.539551891,
        'model_template': 'nml:Cell_472912177.cell.nml'
    },
    {
        'model_name': 'PV2',
        'N': int(PERCENTAGE_CELLS*700),
        'ei': 'i',
        'model_type': 'biophysical',
        'morphology': 'Pvalb_469628681_m.swc',
        'electrophysiology': '473862421_fit.json',
        'rotation_angle_zaxis': -3.684439949,
        'model_template': 'nml:Cell_473862421.cell.nml'
    },
    {
        'model_name': 'LIF_exc',
        'N': int(PERCENTAGE_CELLS*29750),
        'ei': 'e',
        'model_type': 'point_process',
        'model_template': 'nrn:IntFire1',
        'dynamics_params': 'IntFire1_exc_1.json'
    },
    {
        'model_name': 'LIF_inh',
        'N': int(PERCENTAGE_CELLS*5250),
        'ei': 'i',
        'model_type': 'point_process',
        'model_template': 'nrn:IntFire1',
        'dynamics_params': 'IntFire1_inh_1.json'
    }
]


def lerp(v0, v1, t):
    return v0 * (1.0 - t) + v1 * t


def distance_weight(delta_p, w_min, w_max, r_max):
    r = np.linalg.norm(delta_p)
    if r >= r_max:
        return 0.0
    else:
        return lerp(w_max, w_min, r / r_max)


def orientation_tuning_weight(tuning1, tuning2, w_min, w_max):

    # 0-180 is the same as 180-360, so just modulo by 180
    delta_tuning = math.fmod(abs(tuning1 - tuning2), 180.0)

    # 90-180 needs to be flipped, then normalize to 0-1
    delta_tuning = delta_tuning if delta_tuning < 90.0 else 180.0 - delta_tuning

    # t = delta_tuning / 90.0
    return lerp(w_max, w_min, delta_tuning / 90.0)


def distance_tuning_connection_handler(source, target, d_weight_min, d_weight_max, d_max, t_weight_min,
                                       t_weight_max, nsyn_min, nsyn_max):
    # Avoid self-connections.n_nodes
    sid = source.node_id
    tid = target.node_id
    if sid == tid:
        if sid % 100 == 0:
            print "processing connections for node",  sid
        return None

    # first create weights by euclidean distance between cells
    # DO NOT use PERIODIC boundary conditions in x and y!
    dw = distance_weight(np.array([source['x'], source['y']]) - np.array([target['x'], target['y']]), d_weight_min,
                         d_weight_max, d_max)

    # drop the connection if the weight is too low
    if dw <= 0:
        return None

    # next create weights by orientation tuning [ aligned, misaligned ] --> [ 1, 0 ]
    # Check that the orientation tuning property exists for both cells; otherwise,
    # ignore the orientation tuning.
    if source['tuning_angle'] > 0 and target['tuning_angle'] > 0:
        tw = dw * orientation_tuning_weight(source['tuning_angle'],
                                            target['tuning_angle'],
                                            t_weight_min, t_weight_max)
    else:
        tw = dw

    # drop the connection if the weight is too low
    if tw <= 0:
        return None

    # filter out nodes by treating the weight as a probability of connection
    if random.random() > tw:
        return None

    # Add the number of synapses for every connection.
    # It is probably very useful to take this out into a separate function.

    tmp_nsyn = random.randint(nsyn_min, nsyn_max)
    return tmp_nsyn


def distance_connection_handler(source, target, d_weight_min, d_weight_max, d_max, nsyn_min, nsyn_max):
    # Avoid self-connections.
    sid = source.node_id
    tid = target.node_id

    if sid == tid:
        if sid % 100 == 0:
            print "processing connections for node", sid
        return None

    # first create weights by euclidean distance between cells
    # DO NOT use PERIODIC boundary conditions in x and y!
    dw = distance_weight(np.array([source['x'], source['y']]) - np.array([target['x'], target['y']]),
                               d_weight_min, d_weight_max, d_max)

    # drop the connection if the weight is too low
    if dw <= 0:
        return None

    # filter out nodes by treating the weight as a probability of connection
    if random.random() > dw:
        return None

    # Add the number of synapses for every connection.
    # It is probably very useful to take this out into a separate function.

    tmp_nsyn = random.randint(nsyn_min, nsyn_max)
    # print('{} ({}) --> {} ({})'.format(sid, source['name'], tid, target['name']))
    return tmp_nsyn


net = NetworkBuilder('l4')
for model_params in cell_models:
    N = model_params['N']
    positions = np.random.rand(N, 3)*[100.0, -300.0, 100.0]
    rotation_angle_yaxis = np.random.uniform(0.0, 2*np.pi, (N,))
    tuning_angle = np.linspace(0, 360.0, N, endpoint=False) if model_params['ei'] == 'e' else [-1.0]*N
    net.add_nodes(x=positions[:, 0],
                  y=positions[:, 1],
                  z=positions[:, 2],
                  rotation_angle_yaxis=rotation_angle_yaxis,
                  tuning_angle=tuning_angle,
                  **model_params)

# net.build()
# net.save_nodes('tmp_nodes.h5', 'tmp_node_types.csv')

morphologies = {p['model_name']: SWCReader(os.path.join('../shared_components/morphologies', p['morphology']))
                for p in cell_models if 'morphology' in p}
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


def gaussianLL(src, trg, weight, weight_sigma=50.0):
    src_tuning = src['tuning_angle']
    tar_tuning = trg['tuning_angle']
    delta_tuning = abs(abs(abs(180.0 - abs(float(tar_tuning) - float(src_tuning)) % 360.0) - 90.0) - 90.0)
    return weight * math.exp(-(delta_tuning / weight_sigma) ** 2)


cparameters = {'d_weight_min': 0.0, 'd_weight_max': 1.0, 'd_max': 160.0, 'nsyn_min': 3, 'nsyn_max': 7}

# inh --> bio inh
cm = net.add_edges(source={'ei': 'i'}, target={'ei': 'i', 'model_type': 'biophysical'},
                   connection_rule=distance_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='GABA_InhToInh.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.0002, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['somatic', 'basal'], 'dist_range': [0.0, 1e+20]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

# inh --> point inh
cm = net.add_edges(source={'ei': 'i'}, target={'ei': 'i', 'model_type': 'point_process'},
                   connection_rule=distance_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='instanteneousInh.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.00225, dtypes=np.float)

# inh --> bio exc
cparameters = {'d_weight_min': 0.0, 'd_weight_max': 1.0, 'd_max': 160.0, 'nsyn_min': 3, 'nsyn_max': 7}
cm = net.add_edges(source={'ei': 'i'}, target={'ei': 'e', 'model_type': 'biophysical'},
                   connection_rule=distance_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='GABA_InhToExc.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.00018*WEIGHT_ADJ, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['somatic', 'basal', 'apical'], 'dist_range': [0.0, 50.0]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

# inh --> point exc
cm = net.add_edges(source={'ei': 'i'}, target={'ei': 'e', 'model_type': 'intfire'},
                   connection_rule=distance_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='instanteneousInh.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.009*WEIGHT_ADJ, dtypes=np.float)

# exc --> PV1
cparameters = {'d_weight_min': 0.0, 'd_weight_max': 0.26, 'd_max': 300.0, 'nsyn_min': 3, 'nsyn_max': 7}
cm = net.add_edges(source={'ei': 'e'}, target={'model_name': 'PV1'},
                   connection_rule=distance_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='AMPA_ExcToInh.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.00035*WEIGHT_ADJ, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['somatic', 'basal'], 'dist_range': [0.0, 1e+20]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

# exc --> PV2
cm = net.add_edges(source={'ei': 'e'}, target={'model_name': 'PV2'},
                   connection_rule=distance_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='AMPA_ExcToInh.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.00027*WEIGHT_ADJ, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['somatic', 'basal'], 'dist_range': [0.0, 1e+20]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

# exc --> LIF_inh
cm = net.add_edges(source={'ei': 'e'}, target={'model_name': 'LIF_inh'},
                   connection_rule=distance_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='instanteneousExc.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.0043*WEIGHT_ADJ, dtypes=np.float)


cparameters = {'d_weight_min': 0.0, 'd_weight_max': 0.34, 'd_max': 300.0, 't_weight_min': 0.5,
               't_weight_max': 1.0, 'nsyn_min': 3, 'nsyn_max': 7}

# exc --> Scnn1a
cm = net.add_edges(source={'ei': 'e'}, target={'model_name': 'Scnn1a'},
                   connection_rule=10, #distance_tuning_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='AMPA_ExcToExc.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=gaussianLL, rule_params={'weight': 6.4e-05*WEIGHT_ADJ}, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['basal', 'apical'], 'dist_range': [30.0, 150.0]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

# exc --> Rorb
cm = net.add_edges(source={'ei': 'e'}, target={'model_name': 'Rorb'},
                   connection_rule=distance_tuning_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='AMPA_ExcToExc.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=gaussianLL, rule_params={'weight': 5.5e-05*WEIGHT_ADJ}, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['basal', 'apical'], 'dist_range': [30.0, 150.0]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

# exc --> Nr5a1
cm = net.add_edges(source={'ei': 'e'}, target={'model_name': 'Nr5a1'},
                   connection_rule=distance_tuning_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='AMPA_ExcToExc.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=gaussianLL, rule_params={'weight': 7.2e-05*WEIGHT_ADJ}, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  rule_params={'sections': ['basal', 'apical'], 'dist_range': [30.0, 150.0]},
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])

# exc --> LIF_exc
cm = net.add_edges(source={'ei': 'e'}, target={'model_name': 'LIF_exc'},
                   connection_rule=distance_tuning_connection_handler,
                   connection_params=cparameters,
                   delay=2.0,
                   dynamics_params='instanteneousExc.json',
                   model_template='exp2syn')
cm.add_properties('syn_weight', rule=0.0019*WEIGHT_ADJ, dtypes=np.float)

net.build()
net.save(output_dir='network')
