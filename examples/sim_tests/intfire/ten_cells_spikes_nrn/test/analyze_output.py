import sys
from bmtk.analyzer.visualization.spikes import plot_spikes


sys.path.append("../../../shared_components/scripts")

from analyze_output_utils import plot_data

if __name__ == '__main__':
    
    #plot_data('output/membrane_potential.h5', 'mV', 'Membrane Potential', show_already=True)
    plot_spikes('../input/network/pre_nodes.h5', '../input/network/pre_node_types.csv', 'output/spikes.h5')
    plot_spikes('../input/network/post_nodes.h5', '../input/network/post_node_types.csv', 'output/spikes.h5')