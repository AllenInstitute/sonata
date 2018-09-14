import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt


def plot_data(reports_file, y_axis, title):
    cellvar_h5 = h5py.File(reports_file, 'r')
    gids = np.array(cellvar_h5['/mapping/gids'])
    soma_locs = np.array(cellvar_h5['/mapping/index_pointer'])  # location of soma
    t_start = cellvar_h5['/mapping/time'][0]
    t_stop = cellvar_h5['/mapping/time'][1]
    dt = cellvar_h5['/mapping/time'][2]
    time_steps = np.linspace(t_start, t_stop, (t_stop-t_start)/float(dt))

    n_plots = len(gids)
    data_table = np.array(cellvar_h5['/data'])
    f, axarr = plt.subplots(n_plots, 1)
    f.suptitle(title)
    for i, (gid, soma_index) in enumerate(zip(gids, soma_locs)):
        axarr[i].plot(time_steps, data_table[:, [soma_index]], label='gid {}'.format(gid))
        axarr[i].legend()
        axarr[i].set_ylabel(y_axis)
        if i < n_plots - 1:
            axarr[i].set_xticklabels([])
            axarr[i].set_xlabel('ms')
    plt.show()


if __name__ == '__main__':
    membrane_var = 'voltage' if __file__ == sys.argv[-1] else sys.argv[-1].lower()
    if membrane_var in ['cai', 'calcium', 'calcium_concentration', 'calcium_concentration.h5']:
        plot_data('output/calcium_concentration.h5', 'mM', 'Ca++ Concentration')

    elif membrane_var in ['v', 'voltage', 'membrane_potential', 'membrane_potential.h5']:
        plot_data('output/membrane_potential.h5', 'mV', 'Membrane Potential')

    else:
        raise RuntimeError('Unknown report variable {} (valid options: cai, v)'.format(membrane_var))
