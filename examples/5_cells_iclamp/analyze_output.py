import h5py
import numpy as np
import matplotlib.pyplot as plt


def plot_vm():
    cellvar_h5 = h5py.File('output/cell_vars.h5', 'r')
    vm_data = np.array(cellvar_h5['/v/data'])
    plt.plot(vm_data[:, [1]])
    plt.show()

if __name__ == '__main__':
    plot_vm()