from bmtk.analyzer.visualization.spikes import plot_spikes
import sys

title = None
if len(sys.argv)>1:
    title = 'Simulator: %s'%sys.argv[1]

# Note: depends on https://github.com/AllenInstitute/bmtk/pull/73
plot_spikes('network/internal_nodes.h5', 
            'network/internal_node_types.csv', 
            'output/spikes.h5', 
            group_key='model_name', 
            legend=False,
            title=title)
