"""
A script for plotting cell variable (eg voltage, calcium) traces from a SONATA hdf5 file.

To plot a single ouput:
 $ python plot_potential.py path/to/cell_var.h5

If you want to perform a side-by-side comparison of multiple output files:
 $ python plot_potential.py cell_var_0.h5 cell_var_1.h5 ... cell_var_n.h5
cell_var_0.h5 is used as the base-line for plotting number of gid/subplots and time-traces.

"""

import os
import matplotlib.pyplot as plt
from optparse import OptionParser
from bmtk.utils.cell_vars import CellVarsFile


def plot_vars(file_names, cell_var='v', gid_list=[], t_min=None, t_max=None):
    """Plots variable traces for a SONATA h5 file. If multiple spike files are specified will do a side-by-side
    comparsion for each gid.

    :param file_names: list of cell_var file names
    :param cell_var: cell variable to plot trace
    :param gid_list: used to set what gid/subplots to show (if empty list just plot all possible gids)
    """
    # convert to list if single spike file passed in
    file_names = [file_names] if not isinstance(file_names, (tuple, list)) else file_names
    assert(len(file_names) > 0)

    # Use bmtk to parse the cell-var files
    cell_var_files = []
    for fn in file_names:
        try:
            cell_var_files.append(CellVarsFile(fn, h5_root="/report/internal"))
        except KeyError as e:
            print('Exception: %s'%e)
            cell_var_files.append(CellVarsFile(fn))

    # get first spike file and properties
    cvf_base = cell_var_files[0]
    xlim = [t_min or cvf_base.time_trace[0], t_max or cvf_base.time_trace[-1]]  # Use the same x-axis across all subplots
    gid_list = cvf_base.gids if not gid_list else gid_list  # if gid_list is None just get all gids in first file
    n_cells = len(cvf_base.gids)

    fig, ax = plt.subplots(n_cells, 1, figsize=(10, 10))
    for subplot, gid in enumerate(gid_list):
        for i, cvf in enumerate(cell_var_files):
            # plot all traces
            ax[subplot].plot(cvf.time_trace, cvf.data(gid, cell_var), label=file_names[i])
            time_steps = cvf.time_trace
            data = cvf.data(gid, cell_var)
            fn = 'output/gid_%s.dat'%gid
            f = open(fn,'w')
            print('Writing %i points to %s'%(len(time_steps), fn))
            for ti in range(len(time_steps)):
                f.write('%s\t%s\n'%(time_steps[ti]/1000,data[ti]/1000))
            f.close()

        ax[subplot].yaxis.set_label_position("right")
        ax[subplot].set_ylabel('gid {}'.format(gid), fontsize='xx-small')
        ax[subplot].set_xlim(xlim)
        if subplot + 1 < n_cells:
            # remove x-axis labels on all but the last plot
            ax[subplot].set_xticklabels([])
        else:
            # Use the last plot to get the legend
            handles, labels = ax[subplot].get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper right')
            
    for cvf in cell_var_files:
        # Note: depends on: https://github.com/AllenInstitute/bmtk/pull/73
        cvf.close()

    plt.show()


if __name__ == '__main__':
    parser = OptionParser(usage="Usage: python %prog [options] <cell_vars>.h5 [<cell_vars2>.h5 ...]")
    parser.add_option('--variable', type=str, dest='cell_var', default='V_m', help='Cell variable to compare (v, cai, etc)')
    parser.add_option('--gids', type='string', dest='gids', default=[],
                      action='callback',
                      callback=lambda option, opt, value, parser: setattr(parser.values, option.dest, [int(v) for v in value.split(',')]),
                      help='comma seperated list of gids to plot')
    parser.add_option('--tmin', type=float, dest='t_min', default=None)
    parser.add_option('--tmax', type=float, dest='t_max', default=None)
    options, args = parser.parse_args()

    if len(args) == 0:
        # If no file is specified see if there is a output/membrane_potential.h5 file to plot membrane voltage
        if not os.path.exists('output/membrane_potential.h5'):
            raise Exception('Please specifiy hdf5 file to read in arguments. Exiting!')
        else:
            plot_vars('output/membrane_potential.h5', cell_var=options.cell_var, t_min=options.t_min, t_max=options.t_max)
    else:
        plot_vars(file_names=args, cell_var=options.cell_var, gid_list=options.gids, t_min=options.t_min, t_max=options.t_max)
    if len(args) == 1:
        plt.savefig(args[0].replace(".h5", ".png"))
    else:
        plt.savefig("comparison_{}.png".format(options.cell_var))
