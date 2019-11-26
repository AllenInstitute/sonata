#!/bin/env python

import sys


def run(config_file, simulator):
    
    if simulator=='NEURON':
        from bmtk.simulator import bionet
        conf = bionet.Config.from_json(config_file, validate=True)
        conf.build_env()
        net = bionet.BioNetwork.from_config(conf)
        sim = bionet.BioSimulator.from_config(conf, network=net)
        
    
    elif simulator=='NEST':
        from bmtk.simulator import pointnet
        conf = pointnet.Config.from_json(config_file)
        conf.build_env()
        net = pointnet.PointNetwork.from_config(conf)
        sim = pointnet.PointSimulator.from_config(conf, net)
        
    sim.run()


if __name__ == '__main__':
    if __file__ != sys.argv[-1]:
        
        simulator = 'NEURON'
        if len(sys.argv)==3:
            simulator = sys.argv[-2]
            
        run(sys.argv[-1], simulator)
    else:
        run('config.json')
