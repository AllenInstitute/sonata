
import h5py
import numpy as np
import matplotlib.pyplot as plt


def plot_data(reports_file, y_axis, title, show_already=True):
    print('Plotting data on %s (%s) from file: %s'%(title, y_axis, reports_file))
    cellvar_h5 = h5py.File(reports_file, 'r')
    gids = np.array(cellvar_h5['/mapping/gids'])
    soma_locs = np.array(cellvar_h5['/mapping/index_pointer'])  # location of soma
    t_start = cellvar_h5['/mapping/time'][0]
    t_stop = cellvar_h5['/mapping/time'][1]
    dt = cellvar_h5['/mapping/time'][2]
    time_steps = np.linspace(t_start, t_stop, 1+(t_stop-t_start)/float(dt))

    n_plots = len(gids)
    data_table = np.array(cellvar_h5['/data'])
    f, axarr = plt.subplots(n_plots, 1)
    f.suptitle(title)
    for i, (gid, soma_index) in enumerate(zip(gids, soma_locs)):
        data = data_table[:, [soma_index]]
        ax = axarr if n_plots==1 else axarr[i]
        ax.plot(time_steps, data, label='gid {}'.format(gid))
        
        fn = 'output/gid_%s.dat'%gid
        f = open(fn,'w')
        print('Writing %i points to %s'%(len(time_steps), fn))
        for ti in range(len(time_steps)):
            f.write('%s\t%s\n'%(time_steps[ti]/1000,data[ti][0]/1000))
        f.close()
        ax.legend()
        ax.set_ylabel(y_axis)
        if i < n_plots - 1:
            ax.set_xticklabels([])
            ax.set_xlabel('ms')
    
    if show_already:
        plt.show()

