import os
import sys
import h5py
import numpy as np
import glob


def add_magic(files):
    # files = glob.glob('*.h5')  #['v1_nodes.h5', 'v1_v1_edges.h5', 'lgn_nodes.h']
    for h5_file in files:
        print('Updating {}.'.format(h5_file))
        with h5py.File(h5_file, 'r+') as h5:
            h5['/'].attrs['magic'] = np.uint32(0x0A7A)
            h5['/'].attrs['version'] = [np.uint32(0), np.uint32(1)]


if __name__ == '__main__':
    if len(sys.argv) == 1:
        add_magic(glob.glob('*.h5'))
    else:
        for pth in sys.argv[1:]:
            abs_pth = os.path.abspath(pth)
            if os.path.isdir(abs_pth):
                lastwd = os.getcwd()
                os.chdir(abs_pth)
                add_magic(glob.glob("*.h5"))
                os.chdir(lastwd)
            if os.path.isfile(abs_pth):
                add_magic(pth)
