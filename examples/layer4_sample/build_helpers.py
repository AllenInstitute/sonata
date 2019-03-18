import math
import random
import csv
import numpy as np

""""Functions used by build_l4.py"""


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
    dw = distance_weight(np.array([source['x'], source['y']]) - np.array([target['x'], target['y']]), d_weight_min,
                         d_weight_max, d_max)

    # drop the connection if the weight is too low
    if dw <= 0:
        return None

    # filter out nodes by treating the weight as a probability of connection
    if random.random() > dw:
        return None

    # Add the number of synapses for every connection.
    # It is probably very useful to take this out into a separate function.
    tmp_nsyn = random.randint(nsyn_min, nsyn_max)
    return tmp_nsyn


def generate_random_positions(N, center, height, radius_outer, radius_inner):
    """

    :param N: umber of positions to generate
    :param center: center of the cylinder (numpy array)
    :param height: cylinder height
    :param radius_outer: outer radius, within which all positions are generated
    :param radius_inner: inner radius, within which no positions are generated
    :return: A generated list of poisitons with in the given bounds
    """
    # Generate N random x and y values using polar coordinates;
    #   for phi, use uniform distribution;
    #   for r, the probability density is p(r)dr = r dr, so use inverse transform sampling:
    #   integral_R0_R p(r) dr = R^2/2 - R0^2/2; draw x = R^2/2 - R0^2/2 from a uniform distribution with values of x
    #   between 0 and R1^2/2 - R0^2/2.
    phi = 2.0 * math.pi * np.random.random([N])
    r = np.sqrt((radius_outer**2 - radius_inner**2) * np.random.random([N]) + radius_inner**2)
    x = center[0] + r * np.cos(phi)
    z = center[2] + r * np.sin(phi)

    # Generate N random z values.
    y = center[1] + height * (np.random.random([N]) - 0.5)
    return np.column_stack((x, y, z))


def cylinder_from_density(N, density, height, center=None):
    """
    Build a cylinder for given point density, center and height.
    N: number of points
    density: density of points
    height: height of the cylinder
    center: desired center of the cylinder
    """
    if center is None:
        center = np.array([0.0, 0.0, 0.0])

    height = float(height)
    radius = math.sqrt((N / density) / (height * math.pi) )
    return center, height, radius


def gaussianLL(src, trg, weight, weight_sigma=50.0):
    src_tuning = src['tuning_angle']
    tar_tuning = trg['tuning_angle']
    delta_tuning = abs(abs(abs(180.0 - abs(float(tar_tuning) - float(src_tuning)) % 360.0) - 90.0) - 90.0)
    return weight * math.exp(-(delta_tuning / weight_sigma) ** 2)


"""Functions used by build_lgn.py"""
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

        if tuning_angle is None:
            ellipse_center_x = ellipse_center_x0
            ellipse_center_y = ellipse_center_y0
            ellipse_a = ellipse_a0
            ellipse_b = ellipse_b0
        else:
            if src_type == 'tON_001':
                ellipse_center_x = ellipse_center_x0 + ellipses_centers_halfdistance * ellipse_sin_mphi
                ellipse_center_y = ellipse_center_y0 + ellipses_centers_halfdistance * ellipse_cos_mphi
                ellipse_a = ellipse_a0
                ellipse_b = ellipse_b0
            elif src_type == 'tOFF_001':
                ellipse_center_x = ellipse_center_x0 - ellipses_centers_halfdistance * ellipse_sin_mphi
                ellipse_center_y = ellipse_center_y0 - ellipses_centers_halfdistance * ellipse_cos_mphi
                ellipse_a = ellipse_a0
                ellipse_b = ellipse_b0
            else:
                # Make this a simple circle.
                ellipse_center_x = ellipse_center_x0
                ellipse_center_y = ellipse_center_y0
                # Make the region from which source cells are selected a bit smaller for the transient_ON_OFF cells,
                # since each source cell in this case produces both ON and OFF responses.
                ellipse_b = ellipses_centers_halfdistance/2.0 #0.01 #ellipses_centers_halfdistance + 1.0*ellipse_b0 #0.01 #0.5 * ellipse_b0 # 0.8 * ellipse_b0
                ellipse_a = ellipse_b0 #0.01 #ellipse_b0

        # Find those source cells of the appropriate type that have their visual space coordinates within the ellipse.
        for src_id, src_dict in cell_type_dict[src_type]:
            x, y = (src_dict['x'], src_dict['y'])
            x = x - ellipse_center_x
            y = y - ellipse_center_y

            x_new = x
            y_new = y
            if tuning_angle is not None:
                x_new = x * ellipse_cos_mphi - y * ellipse_sin_mphi
                y_new = x * ellipse_sin_mphi + y * ellipse_cos_mphi

            if ((x_new/ellipse_a)**2 + (y_new/ellipse_b) ** 2) <= 1.0:
                if (tuning_angle is not None) and (src_type == 'tONOFF_001'):
                    src_tuning_angle = float(src_dict['tuning_angle'])
                    delta_tuning = abs(abs(abs(180.0-abs(tuning_angle_value-src_tuning_angle)%360.0)-90.0)-90.0)
                    if delta_tuning < 15.0:
                        src_cells_selected[src_type].append(src_id)
                else:
                    src_cells_selected[src_type].append(src_id)

        while len(src_cells_selected[src_type]) > top_N_src_cells_subfield:
            src_cells_selected[src_type].remove(random.choice(src_cells_selected[src_type]))


    select_cell_ids = [id for _, selected in src_cells_selected.items() for id in selected]
    nsyns_ret = [N_syn if id in select_cell_ids else None for id in source_ids]
    return nsyns_ret


