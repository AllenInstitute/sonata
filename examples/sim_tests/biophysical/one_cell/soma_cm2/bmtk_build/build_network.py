#!/bin/env python

# Sonata Simulator Test Suite
# 1-cell circuit, single soma, only cm, 1 step current

# Authors: Werner Van Geit @ BBP

import bmtk.builder

cell_models = [
    {'model_name': 'soma_cm', 'x': [0.0],
     'y': [0.0],
     'z': [0.0],
     'morphology': 'soma1',
     'model_template': 'nml:soma_cm2.nml'}]

bio_cells = bmtk.builder.NetworkBuilder("biophysical")
for model_props in cell_models:
    bio_cells.add_nodes(
        model_type='biophysical',
        **model_props)

bio_cells.build()
bio_cells.save_nodes(output_dir='../input/network')
