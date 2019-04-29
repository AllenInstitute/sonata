import os
import numpy as np

from bmtk.builder import NetworkBuilder
from bmtk.builder.bionet import SWCReader
from bmtk.utils.io.spike_trains import PoissonSpikesGenerator
from bmtk.builder.aux.node_params import positions_columinar, xiter_random

build_recurrent_edges = True

print('Building internal network')
# List of non-virtual cell models
cell_models = [
    {
        'model_name': 'Scnn1a', 'ei': 'e',
        'model_template': 'nest:iaf_psc_alpha',
        'dynamics_params': '472363762_point.json'
    },
    {
        'model_name': 'Rorb', 'ei': 'e',
        'model_template': 'nest:iaf_psc_alpha',
        'dynamics_params': '473863510_point.json'
    },
    {
        'model_name': 'Nr5a1', 'ei': 'e',
        'model_template': 'nest:iaf_psc_alpha',
        'dynamics_params': '473863035_point.json'
    },
    {
        'model_name': 'PV1', 'ei': 'i',
        'model_template': 'nest:iaf_psc_alpha',
        'dynamics_params': '472912177_point.json'
    },
    {
        'model_name': 'PV2', 'ei': 'i',
        'model_template': 'nest:iaf_psc_alpha',
        'dynamics_params': '473862421_point.json'
    }
]

'''
morphologies = {p['model_name']: SWCReader(os.path.join('../shared_components/morphologies',
                                                        '{}.swc'.format(p['morphology'])))
                for p in cell_models}
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
'''

# Build a network of 300 biophysical cells to simulate
internal = NetworkBuilder("internal")
for i, model_props in enumerate(cell_models):
    n_cells = 80 if model_props['ei'] == 'e' else 30  # 80% excitatory, 20% inhib

    # Randomly get positions uniformly distributed in a column
    positions = positions_columinar(N=n_cells, center=[0, 10.0, 0], max_radius=50.0, height=200.0)

    internal.add_nodes(N=n_cells,
                       x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
                       rotation_angle_yaxis=xiter_random(N=n_cells, min_x=0.0, max_x=2 * np.pi),  # randomly rotate y axis
                       model_type='point_process',
                       **model_props)



if build_recurrent_edges:
    def n_connections(src, trg, prob=0.5, min_syns=2, max_syns=7):
        return 0 if np.random.uniform() > prob else np.random.randint(min_syns, max_syns)

    # exc --> exc connections
    cm = internal.add_edges(source={'ei': 'e'}, target={'ei': 'e'},
                            connection_rule=lambda s, t: np.random.binomial(1, 0.2),
                            dynamics_params='ExcToExc.json',
                            model_template='static_synapse',
                            # syn_weight=2.5,
                            delay=2.0)
    cm.add_properties('syn_weight', rule=2.5, dtypes=np.float)

    # exc --> inh connections
    cm = internal.add_edges(source={'ei': 'e'}, target={'ei': 'i'},
                            connection_rule=lambda s, t: np.random.binomial(1, 0.5),
                            dynamics_params='ExcToInh.json',
                            model_template='static_synapse',
                            # syn_weight=7.0,
                            delay=2.0)
    cm.add_properties('syn_weight', rule=7.0, dtypes=np.float)

    # inh --> exc connections
    cm = internal.add_edges(source={'ei': 'i'}, target={'ei': 'e'},
                            connection_rule=lambda s, t: np.random.binomial(1, 0.5),
                            #connection_rule=lambda *_: np.random.randint(0, 4),
                            dynamics_params='InhToExc.json',
                            model_template='static_synapse',
                            # syn_weight=-7.5,
                            delay=2.0)
    cm.add_properties('syn_weight', rule=-7.5, dtypes=np.float)

    # inh --> inh connections
    cm = internal.add_edges(source={'ei': 'i'}, target={'ei': 'i'},
                            connection_rule=lambda s, t: np.random.binomial(1, 0.5),
                            dynamics_params='InhToInh.json',
                            model_template='static_synapse',
                            # syn_weight=-3.0,
                            delay=2.0)
    cm.add_properties('syn_weight', rule=-3.0, dtypes=np.float)


internal.build()

print('Saving internal')
internal.save(output_dir='network')


print('Building external connections')
external = NetworkBuilder("external")
external.add_nodes(N=100, model_type='virtual', ei='e')
cm = external.add_edges(target=internal.nodes(ei='e'), source=external.nodes(),
                        connection_rule=lambda *_: np.random.binomial(1, .7),
                        dynamics_params='ExcToExc.json',
                        model_template='static_synapse')
cm.add_properties('syn_weight', rule=50.0, dtypes=np.float)


cm = external.add_edges(target=internal.nodes(ei='i'), source=external.nodes(),
                        connection_rule=lambda *_: np.random.binomial(1, .7),
                        dynamics_params='ExcToInh.json',
                        model_template='static_synapse')
cm.add_properties('syn_weight', rule=65.0, dtypes=np.float)


external.build()

print('Saving external')
external.save(output_dir='network')


