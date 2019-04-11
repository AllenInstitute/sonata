#!/bin/env python

# Sonata Simulator Test Suite
# 1-cell circuit, integrate and fire cell, current clamp input

# Authors: Padraig Gleeson @ UCL

from bmtk.builder import NetworkBuilder

net = NetworkBuilder("one_cell_iclamp")

pos_x, pos_y = [0,0]

template = 'nest:iaf_psc_alpha'

net.add_nodes(N=1, pop_name='LIF_exc', location='VisL4', ei='e',
              model_type='point_process',  # use point_process to indicate we are using point model cells
              model_template=template,
              x=pos_x, y=pos_y,
              dynamics_params='473863035_point.json')
              

net.build()
net.save(output_dir='../input/network')

print 'Built: %s'%net.name
