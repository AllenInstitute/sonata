import os
import numpy as np

from bmtk.builder import NetworkBuilder
from bmtk.builder.bionet import SWCReader
from bmtk.utils.io.spike_trains import PoissonSpikesGenerator

use_nml = True  # True to build network with NEUROML files, false to build network with Cell-Types json files

cell_models = [
    {
        'model_name': 'Scnn1a', 'ei': 'e', 'morphology': 'Scnn1a_473845048_m',
        'model_template': 'nml:nml/Cell_472363762.cell.nml' if use_nml else 'ctdb:Biophys1.hoc',
        'dynamics_params': 'NONE' if use_nml else 'json/472363762_fit.json'
    },
    {
        'model_name': 'Rorb', 'ei': 'e', 'morphology': 'Rorb_325404214_m',
        'model_template': 'nml:nml/Cell_473863510.cell.nml' if use_nml else 'ctdb:Biophys1.hoc',
        'dynamics_params': 'NONE' if use_nml else 'json/473863510_fit.json'
    },
    {
        'model_name': 'Nr5a1', 'ei': 'e', 'morphology': 'Nr5a1_471087815_m',
        'model_template': 'nml:nml/Cell_473863035.cell.nml' if use_nml else 'ctdb:Biophys1.hoc',
        'dynamics_params': 'NONE' if use_nml else 'json/473863035_fit.json'
    }
]

cortex = NetworkBuilder("cortex")
for i, model_props in enumerate(cell_models):
    cortex.add_nodes(N=3,
                     x=[i*30.0 + j for j in range(3)],  y=[0.0]*3, z=[0.0]*3,  # space cells every 10nm along x axs
                     model_type='biophysical',
                     model_processing='aibs_perisomatic',
                     **model_props)

cortex.build()
cortex.save_nodes(output_dir='network')

morphologies = {p['model_name']: SWCReader(os.path.join('../shared_components/morphologies', '{}.swc'.format(p['morphology'])))
                for p in cell_models}


def build_edges(src, trg, sections=['basal', 'apical'], dist_range=[50.0, 150.0]):
    # Get morphology and soma center for the target cell
    swc_reader = morphologies[trg['model_name']]
    target_coords = [trg['x'], trg['y'], trg['z']]

    sec_ids, sec_xs = swc_reader.choose_sections(sections, dist_range)  # randomly choose sec_ids
    coords = swc_reader.get_coord(sec_ids, sec_xs, soma_center=target_coords)  # get coords of sec_ids
    dist = swc_reader.get_dist(sec_ids)
    swctype = swc_reader.get_type(sec_ids)
    return sec_ids, sec_xs, coords[0][0], coords[0][1], coords[0][2], dist[0], swctype[0]

# Feedfoward excitatory virtual cells
exc_net = NetworkBuilder('excvirt')
exc_net.add_nodes(N=10, model_type='virtual', ei='e')
cm = exc_net.add_edges(target=cortex.nodes(), source=exc_net.nodes(ei='e'),
                       connection_rule=lambda *_: np.random.randint(4, 12),
                       dynamics_params='AMPA_ExcToExc.json',
                       model_template='Exp2Syn',
                       delay=2.0)
cm.add_properties('syn_weight', rule=3.4e-4, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])
exc_net.build()
exc_net.save(output_dir='network')

if not os.path.exists('inputs/exc_spike_trains.h5'):
    # Build spike-trains for excitatory virtual cells
    if not os.path.exists('inputs'):
        os.mkdir('inputs')
    psg = PoissonSpikesGenerator(range(10), 10.0, tstop=3000.0)
    psg.to_hdf5('inputs/exc_spike_trains.h5')


# Inhibitory connections, build this as a separate network so we can test simulation with only excitatory input and
# with mixed excitatory/inhibitory input.
inh_net = NetworkBuilder('inhvirt')
inh_net.add_nodes(N=10, model_type='virtual', ei='i')
cm = inh_net.add_edges(target=cortex.nodes(), source=inh_net.nodes(ei='i'),
                       connection_rule=np.random.randint(0, 8),
                       dynamics_params='GABA_InhToExc.json',
                       model_template='Exp2Syn',
                       delay=2.0)
cm.add_properties('syn_weight', rule=2.6e-4, dtypes=np.float)
cm.add_properties(['sec_id', 'sec_x', 'pos_x', 'pos_y', 'pos_z', 'dist', 'type'],
                  rule=build_edges,
                  dtypes=[np.int32, np.float, np.float, np.float, np.float, np.float, np.uint8])
inh_net.build()
inh_net.save(output_dir='network')

if not os.path.exists('inputs/inh_spike_trains.h5'):
    # Build spike-trains for inhibitory virtual cells
    if not os.path.exists('inputs'):
        os.mkdir('inputs')
    psg = PoissonSpikesGenerator(range(10), 10.0, tstop=3000.0)
    psg.to_hdf5('inputs/inh_spike_trains.h5')
