import numpy as np
from neuron import h
from bmtk.builder import NetworkBuilder

cell_models = [
    {
        'model_name': 'Scnn1a', 'positions': [(0.0, 0.0, 0.0)], 'ei': 'e', 'morphology_file': 'Scnn1a_473845048_m.swc',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '472363762_fit.json',
    },
    {
        'model_name': 'Rorb', 'positions': [(200.0, 0.0, 0.0)], 'ei': 'e', 'morphology_file': 'Rorb_325404214_m.swc',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '473863510_fit.json',
    },
    {
        'model_name': 'Nr5a1', 'positions': [(-200.0, 0.0, 0.0)], 'ei': 'e', 'morphology_file': 'Nr5a1_471087815_m.swc',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '473863035_fit.json',
    },
    {
        'model_name': 'PV1', 'positions': [(0.0, 200.0, 0.0)], 'ei': 'i', 'morphology_file': 'Pvalb_470522102_m.swc',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '472912177_fit.json',
    },
    {
        'model_name': 'PV2', 'positions': [(0.0, -200.0, 0.0)], 'ei': 'i', 'morphology_file': 'Pvalb_469628681_m.swc',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '473862421_fit.json',
    }
]

bio_cells = NetworkBuilder("biophysical")
for model_props in cell_models:
    bio_cells.add_nodes(model_type='biophysical', model_processing='aibs_perisomatic', **model_props)

'''
bio_cells.add_nodes(pop_name='Scnn1a',
                    positions=[(0.0, 0.0, 0.0)],
                    ei='e',
                    model_type='biophysical',
                    #model_template='nml/nml:Cell_472363762.cell.nml',
                    model_template='ctdb:Biophys1.hoc',
                    dynamics_params='json/472363762_fit.json',
                    model_processing='aibs_perisomatic',
                    morphology_file='Scnn1a_473845048_m.swc')
'''

bio_cells.build()
bio_cells.save_nodes(output_dir='network')

