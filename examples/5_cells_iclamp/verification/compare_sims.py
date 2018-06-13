import h5py
import numpy as np
import matplotlib.pyplot as plt


original_results = '../output/cell_vars.h5'

def plot_figs(nrn_results=None):
    orig_h5 = h5py.File(original_results, 'r')
    new_h5 = h5py.File(nrn_results, 'r')
    gids = np.array(new_h5['/mapping/gids'])
    indx_ptrs = np.array(new_h5['/mapping/index_pointer'])

    for plot_num, (gid, indx) in enumerate(zip(gids, indx_ptrs)):
        new_voltage = np.array(new_h5['/v/data']) if len(new_h5['/v/data'].shape) == 1 else np.array(new_h5['/v/data'][:, indx])
        orig_voltage = np.array(orig_h5['/v/data'][:, gid])

        plt.subplot(1, 1, 1)
        times = np.linspace(0.0, 4000.0, len(orig_voltage))
        plt.plot(times, new_voltage[1:], label='NEURON')
        plt.plot(times, orig_voltage, label='AIBS')
        plt.legend()
        plt.title('gid = {}'.format(gid))

    plt.show()


#plot_figs('cellvar_gid0_472363762_Scnn1a.h5')
#plot_figs('cellvar_gid1_473863510_Rorb.h5')
#plot_figs('cellvar_gid2_473863035_Nr5a1.h5')
#plot_figs('cellvar_gid3_472912177_PV1.h5')
plot_figs('cellvar_gid4_473862421_PV2.h5')
