import sys

sys.path.append("../../../shared_components/scripts")

from analyze_output_utils import plot_data

if __name__ == '__main__':
    
    plot_data('output/membrane_potential.h5', 'mV', 'Membrane Potential')