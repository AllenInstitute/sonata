
import h5py
import numpy as np
import matplotlib.pyplot as plt


def plot_data(reports_file, y_axis, title, show_already=True, max_num_traces=None):
    print('Plotting data on %s (%s) from file: %s'%(title, y_axis, reports_file))
    cellvar_h5 = h5py.File(reports_file, 'r')
    
    
    try:
        top_level = cellvar_h5['/mapping']
        pop_prefixes = {'GLOBAL':'/'}
    except:
        pop_prefixes = {}
        for pop in cellvar_h5['/report'].keys():
            pop_prefixes = {pop:'/report/%s/'%pop}
        
    for pop in pop_prefixes:
        
        gids = np.array(cellvar_h5['%smapping/gids'%pop_prefixes[pop]])

        soma_locs = np.array(cellvar_h5['%smapping/index_pointer'%pop_prefixes[pop]])  # location of soma
        t_start = cellvar_h5['%smapping/time'%pop_prefixes[pop]][0]
        t_stop = cellvar_h5['%smapping/time'%pop_prefixes[pop]][1]
        dt = cellvar_h5['%smapping/time'%pop_prefixes[pop]][2]
        time_steps = np.linspace(t_start, t_stop, 1+(t_stop-t_start)/float(dt))
        print('Time steps %s -> %s, dt: %s (%s points)'%(t_start,t_stop,dt, len(time_steps)))

        n_plots = len(gids)
        if max_num_traces:
            n_plots = min(max_num_traces, n_plots)
        data_table = np.array(cellvar_h5['%sdata'%pop_prefixes[pop]])
        f, axarr = plt.subplots(n_plots, 1)
        f.suptitle(title)
        for i, (gid, soma_index) in enumerate(zip(gids, soma_locs)):
            if i<n_plots:
                data = data_table[:, [soma_index]]
                ax = axarr if n_plots==1 else axarr[i]

                print('For gid %i (%s) there are %i time steps and %i data points'%(gid, pop, len(time_steps), len(data)))
                label='%s: gid %i'%(pop,gid)
                if len(time_steps) == len(data):
                    ax.plot(time_steps, data, label=label)

                    fn = 'output/gid_%s.dat'%gid
                    f = open(fn,'w')
                    print('Writing %i points to %s'%(len(time_steps), fn))
                    for ti in range(len(time_steps)):
                        f.write('%s\t%s\n'%(time_steps[ti]/1000,data[ti][0]/1000))
                    f.close()
                else:
                    ax.plot(data, label=label)



                ax.legend()
                ax.set_ylabel(y_axis)
                if i < n_plots - 1:
                    ax.set_xticklabels([])
                    ax.set_xlabel('ms')
    
    if show_already:
        plt.show()

