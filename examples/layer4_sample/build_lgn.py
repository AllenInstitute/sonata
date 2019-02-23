import os
import csv
import math
import numpy as np
from random import *

from bmtk.builder.networks import NetworkBuilder
from bmtk.builder.bionet import SWCReader

def read_dat_file(filename, type_mapping={'transient_ON': 'tON_001', 'transient_OFF': 'tOFF_001', 'transient_ON_OFF': 'tONOFF_001'}):
    positions_table = {val: [] for val in type_mapping.values()}
    offset_table = {val: [] for val in type_mapping.values()}
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ')
        for row in csvreader:
            model_type = type_mapping.get(row[0], None)
            if model_type:
                positions_table[model_type].append([float(row[1]), float(row[2])])
                offset_table[model_type].append([float(row[3]), float(row[4])])

    return positions_table, offset_table


def calc_tuning_angle(offset_vect):
    offset_sum = sum(offset_vect)
    if offset_sum == 0:
        return -1.0
    else:
        tmp_vec = offset_vect / np.sqrt(offset_vect[0]**2 + offset_vect[1]**2)
        return (360.0 + 180.0 * np.arctan2(tmp_vec[1], tmp_vec[0]) / np.pi) % 360.0


def select_source_cells(sources, target, lgn_mean, lgn_dim, l4_mean, l4_dim, N_syn):

    target_id = target.node_id
    source_ids = [s.node_id for s in sources]

    if target_id%1000 == 0:
        print "connection LGN cells to L4 cell #", target_id

    subfields_centers_distance_min = 10.0  # 10.0
    subfields_centers_distance_max = 11.0  # 10.0
    subfields_centers_distance_L = subfields_centers_distance_max - subfields_centers_distance_min

    subfields_ON_OFF_width_min = 6.0  # 8.0 #10.0 #8.0 #8.0 #14.0 #15.0
    subfields_ON_OFF_width_max = 8.0  # 10.0 #12.0 #10.0 #15.0 #20.0 #15.0
    subfields_ON_OFF_width_L = subfields_ON_OFF_width_max - subfields_ON_OFF_width_min

    subfields_width_aspect_ratio_min = 2.8  # 1.9 #1.4 #0.9 #1.0
    subfields_width_aspect_ratio_max = 3.0  # 2.0 #1.5 #1.1 #1.0
    subfields_width_aspect_ratio_L = subfields_width_aspect_ratio_max - subfields_width_aspect_ratio_min

    vis_x = lgn_mean[0] + ((target['x'] - l4_mean[0]) / l4_dim[0]) * lgn_dim[0]
    vis_y = lgn_mean[1] + ((target['y'] - l4_mean[2]) / l4_dim[2]) * lgn_dim[1]

    ellipse_center_x0 = vis_x #tar_cells[tar_gid]['vis_x']
    ellipse_center_y0 = vis_y #tar_cells[tar_gid]['vis_y']

    try:
        tuning_angle = float(target['tuning_angle'])
        tuning_angle = None if math.isnan(tuning_angle) or tuning_angle < 0 else tuning_angle
    except Exception:
        tuning_angle = None
    #tuning_angle = None if math.isnan(target['tuning_angle']) else target['tuning_angle']
    if tuning_angle is None:
        ellipse_b0 = (subfields_ON_OFF_width_min + random() * subfields_ON_OFF_width_L) / 2.0  # Divide by 2 to convert from width to radius.
        ellipse_b0 = 2.5 * ellipse_b0  # 1.5 * ellipse_b0
        ellipse_a0 = ellipse_b0  # ellipse_b0
        top_N_src_cells_subfield = 15  # 20
        ellipses_centers_halfdistance = 0.0
    else:
        tuning_angle_value = float(tuning_angle)
        ellipses_centers_halfdistance = (subfields_centers_distance_min + random() * subfields_centers_distance_L) / 2.0
        ellipse_b0 = (subfields_ON_OFF_width_min + random() * subfields_ON_OFF_width_L) / 2.0  # Divide by 2 to convert from width to radius.
        ellipse_a0 = ellipse_b0 * (subfields_width_aspect_ratio_min + random() * subfields_width_aspect_ratio_L)
        ellipse_phi = tuning_angle_value + 180.0 + 90.0  # Angle, in degrees, describing the rotation of the canonical ellipse away from the x-axis.
        ellipse_cos_mphi = math.cos(-math.radians(ellipse_phi))
        ellipse_sin_mphi = math.sin(-math.radians(ellipse_phi))
        top_N_src_cells_subfield = 8  # 10 #9

    # to match previous algorithm reorganize source cells by type
    cell_type_dict = {
        'tON_001': [(src_id, src_dict) for src_id, src_dict in zip(source_ids, sources) if src_dict['pop_id'] == 'tON_001'],
        'tOFF_001': [(src_id, src_dict) for src_id, src_dict in zip(source_ids, sources) if src_dict['pop_id'] == 'tOFF_001'],
        'tONOFF_001': [(src_id, src_dict) for src_id, src_dict in zip(source_ids, sources) if src_dict['pop_id'] == 'tONOFF_001']
    }


    src_cells_selected = {}
    for src_type in cell_type_dict.keys():
        src_cells_selected[src_type] = []

        if (tuning_angle is None):
            ellipse_center_x = ellipse_center_x0
            ellipse_center_y = ellipse_center_y0
            ellipse_a = ellipse_a0
            ellipse_b = ellipse_b0
        else:
            if (src_type == 'tON_001'):
                ellipse_center_x = ellipse_center_x0 + ellipses_centers_halfdistance * ellipse_sin_mphi
                ellipse_center_y = ellipse_center_y0 + ellipses_centers_halfdistance * ellipse_cos_mphi
                ellipse_a = ellipse_a0
                ellipse_b = ellipse_b0
            elif (src_type == 'tOFF_001'):
                ellipse_center_x = ellipse_center_x0 - ellipses_centers_halfdistance * ellipse_sin_mphi
                ellipse_center_y = ellipse_center_y0 - ellipses_centers_halfdistance * ellipse_cos_mphi
                ellipse_a = ellipse_a0
                ellipse_b = ellipse_b0
            else:
                # Make this a simple circle.
                ellipse_center_x = ellipse_center_x0
                ellipse_center_y = ellipse_center_y0
                # Make the region from which source cells are selected a bit smaller for the transient_ON_OFF cells, since each
                # source cell in this case produces both ON and OFF responses.
                ellipse_b = ellipses_centers_halfdistance/2.0 #0.01 #ellipses_centers_halfdistance + 1.0*ellipse_b0 #0.01 #0.5 * ellipse_b0 # 0.8 * ellipse_b0
                ellipse_a = ellipse_b0 #0.01 #ellipse_b0

        # Find those source cells of the appropriate type that have their visual space coordinates within the ellipse.
        for src_id, src_dict in cell_type_dict[src_type]:
            x, y = (src_dict['position'][0], src_dict['position'][1])

            x = x - ellipse_center_x
            y = y - ellipse_center_y

            x_new = x
            y_new = y
            if tuning_angle is not None:
                x_new = x * ellipse_cos_mphi - y * ellipse_sin_mphi
                y_new = x * ellipse_sin_mphi + y * ellipse_cos_mphi

            if (((x_new / ellipse_a) ** 2 + (y_new / ellipse_b) ** 2) <= 1.0):
                if ((tuning_angle is not None) and (src_type == 'tONOFF_001')):
                    src_tuning_angle = float(src_dict['tuning_angle'])
                    delta_tuning = abs(abs(abs(180.0 - abs(tuning_angle_value - src_tuning_angle) % 360.0) - 90.0) - 90.0)
                    if (delta_tuning < 15.0):
                        src_cells_selected[src_type].append(src_id)
                else:
                    src_cells_selected[src_type].append(src_id)

        while len(src_cells_selected[src_type]) > top_N_src_cells_subfield:
            src_cells_selected[src_type].remove(choice(src_cells_selected[src_type]))

    select_cell_ids = [id for _, selected in src_cells_selected.items() for id in selected]
    nsyns_ret = [N_syn if id in select_cell_ids else None for id in source_ids]
    return nsyns_ret

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
                      position=positions,
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
print "> LGN mean center:"

# Determine the mean center of the CC cells
xcoords = [n['x'] for n in v1_net.nodes()]
ycoords = [n['y'] for n in v1_net.nodes()]
zcoords = [n['z'] for n in v1_net.nodes()]
l4_mean = (np.mean(xcoords), np.mean(ycoords), np.mean(zcoords))
l4_dim = (max(xcoords) - min(xcoords), max(ycoords) - min(ycoords), max(zcoords) - min(zcoords))
print "> L4 mean center:", str(l4_mean)

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
