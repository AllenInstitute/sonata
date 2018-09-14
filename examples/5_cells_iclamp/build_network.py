import numpy as np
from neuron import h
from bmtk.builder import NetworkBuilder

cell_models = [
    {
        'model_name': 'Scnn1a', 'x': [0.0], 'y': [0.0], 'z': [0.0], 'ei': 'e', 'morphology': 'Scnn1a_473845048_m',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '472363762_fit.json',
    },
    {
        'model_name': 'Rorb', 'x': [200.0], 'y': [0.0], 'z': [0.0], 'ei': 'e', 'morphology': 'Rorb_325404214_m',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '473863510_fit.json',
    },
    {
        'model_name': 'Nr5a1', 'x': [-200.0], 'y': [0.0], 'z': [0.0], 'ei': 'e', 'morphology': 'Nr5a1_471087815_m',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '473863035_fit.json',
    },
    {
        'model_name': 'PV1', 'x': [0.0], 'y': [200.0], 'z': [0.0], 'ei': 'i', 'morphology': 'Pvalb_470522102_m',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '472912177_fit.json',
    },
    {
        'model_name': 'PV2', 'x': [0.0], 'y': [-200.0], 'z': [0.0], 'ei': 'i', 'morphology': 'Pvalb_469628681_m',
        'model_template': 'ctdb:Biophys1.hoc',
        'dynamics_params': '473862421_fit.json',
    }
]

bio_cells = NetworkBuilder("biophysical")
for model_props in cell_models:
    bio_cells.add_nodes(model_type='biophysical', model_processing='aibs_perisomatic', **model_props)

bio_cells.build()
bio_cells.save_nodes(output_dir='network')

