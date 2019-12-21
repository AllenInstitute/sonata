from bmtk.analyzer.cell_vars import plot_report

## Plot the Calcium and Membrane Potential traces of a select subset of nodes
node_ids = [0, 4, 8]  # Nodes to plot, choose nodes 0 - 8
plot_report(config_file='config.json', node_ids=node_ids)
