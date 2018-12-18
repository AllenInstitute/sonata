import sys
from bmtk.analyzer.visualization.spikes import plot_spikes


sys.path.append("../sim_tests/shared_components/scripts")

from analyze_output_utils import plot_data

if __name__ == '__main__':
    
    plot_data('output/membrane_potential.h5', 'mV', 'Membrane Potential', show_already=True, max_num_traces=12)
    plot_spikes('network/internal_nodes.h5', 'network/internal_node_types.csv', 'output/spikes.h5', group_key='model_name')