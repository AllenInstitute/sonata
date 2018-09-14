import os
import sys
import neuron
import json
from pprint import pprint
from neuron import h
import matplotlib.pyplot as plt
import numpy as np
import h5py

## Runs the 5 cell iclamp simulation but in NEURON for each individual cell
# $ python pure_nrn.py <gid>

neuron.load_mechanisms('../components/mechanisms')
h.load_file('stdgui.hoc')
h.load_file('import3d.hoc')

cells_table = {
    # gid = [model id, cre line, morph file]
    0: [472363762, 'Scnn1a', 'Scnn1a_473845048_m.swc'],
    1: [473863510, 'Rorb', 'Rorb_325404214_m.swc'],
    2: [473863035, 'Nr5a1', 'Nr5a1_471087815_m.swc'],
    3: [472912177, 'PV1', 'Pvalb_470522102_m.swc'],
    4: [473862421, 'PV2', 'Pvalb_469628681_m.swc']
}


def run_simulation(gid, morphologies_dir='../components/morphologies', plot_results=True):
    swc_file = os.path.join(morphologies_dir, cells_table[gid][2])
    model_file = 'model_gid{}_{}_{}.json'.format(gid, cells_table[gid][0], cells_table[gid][1])
    params_dict = json.load(open(model_file, 'r'))
    # pprint(params_dict)

    # load the cell
    nrn_swc = h.Import3d_SWC_read()
    nrn_swc.input(str(swc_file))
    imprt = h.Import3d_GUI(nrn_swc, 0)
    h("objref this")
    imprt.instantiate(h.this)

    # Cut the axon
    h("soma[0] area(0.5)")
    for sec in h.allsec():
        sec.nseg = 1 + 2 * int(sec.L / 40.0)
        if sec.name()[:4] == "axon":
            h.delete_section(sec=sec)
    h('create axon[2]')
    for sec in h.axon:
        sec.L = 30
        sec.diam = 1
        sec.nseg = 1 + 2 * int(sec.L / 40.0)
    h.axon[0].connect(h.soma[0], 0.5, 0.0)
    h.axon[1].connect(h.axon[0], 1.0, 0.0)
    h.define_shape()

    # set model params
    h("access soma")
    for sec in h.allsec():
        sec_name = sec.name().split('[')[0]

        # special case for passive channels rev. potential
        sec.insert('pas')
        for seg in sec:
            if sec_name not in params_dict['e_pas']:
                continue

            seg.pas.e = params_dict['e_pas'][sec_name]

        # insert mechanisms (if req.) and set density
        for prop in params_dict[sec_name]:
            if 'mechanism' in prop:
                sec.insert(prop['mechanism'])

            setattr(sec, prop['name'], prop['value'])

    # simulation properties
    h.stdinit()
    h.tstop = 4000.0
    h.dt = 0.1
    h.steps_per_ms = 1/h.dt
    h.celsius = 34.0
    h.v_init = -80.0

    # stimuli is an increasing series of 3 step currents
    cclamp1 = h.IClamp(h.soma[0](0.5))
    cclamp1.delay = 500.0
    cclamp1.dur = 500.0
    cclamp1.amp = 0.1500

    cclamp2 = h.IClamp(h.soma[0](0.5))
    cclamp2.delay = 1500.0
    cclamp2.dur = 500.0
    cclamp2.amp = 0.1750

    cclamp3 = h.IClamp(h.soma[0](0.5))
    cclamp3.delay = 2500.0
    cclamp3.dur = 500.0
    cclamp3.amp = 0.2000

    # run simulation
    v_vec = h.Vector()
    v_vec.record(h.soma[0](0.5)._ref_v)
    h.startsw()
    h.run(h.tstop)
    voltages = [v for v in v_vec]

    cell_var_name = 'cellvar_gid{}_{}_{}.h5'.format(gid, cells_table[gid][0], cells_table[gid][1])
    with h5py.File(cell_var_name, 'w') as h5:
        # fake a mapping table just for convience
        h5.create_dataset('/mapping/gids', data=[gid], dtype=np.uint16)
        h5.create_dataset('/mapping/element_pos', data=[0.5], dtype=np.float)
        h5.create_dataset('/mapping/element_id', data=[0], dtype=np.uint16)
        h5.create_dataset('/mapping/index_pointer', data=[0], dtype=np.uint16)

        h5.create_dataset('/v/data', data=voltages, dtype=np.float64)

    if plot_results:
        times = np.linspace(0.0, h.tstop, len(voltages))
        plt.plot(times, voltages)
        plt.show()


if __name__ == '__main__':
    if __file__ != sys.argv[-1]:
        run_simulation(sys.argv[-1])
    else:
        for gid in range(5):
            run_simulation(gid, plot_results=False)
