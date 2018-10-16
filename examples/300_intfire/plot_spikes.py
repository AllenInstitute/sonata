from bmtk.analyzer.visualization.spikes import plot_spikes

plot_spikes('network/v1_nodes.h5', 'network/v1_node_types.csv', 'output/spikes.h5', group_key='pop_name')
