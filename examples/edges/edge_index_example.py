#!/usr/bin/env python

import numpy
import random
import h5py


out = h5py.File("edge_index_example.h5", "w")

population = out.create_group("edges/example")

connections = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 0), (2, 4), (3, 1), (3, 4),
               (4, 0), (4, 1), (4, 3)]
random.shuffle(connections)
synapses_per_connection = \
    numpy.array([random.randint(1, 5) for i in range(len(connections))])
edge_count = numpy.sum(synapses_per_connection)

source = numpy.zeros((edge_count), dtype="u8")
target = numpy.zeros((edge_count), dtype="u8")

pre_ranges = [[] for i in range(5)]
post_ranges = [[] for i in range(5)]

i = 0
for (s, t), count in zip(connections, synapses_per_connection):
    source[i:i+count] = s
    target[i:i+count] = t
    pre_ranges[s].append((i, i + count))
    post_ranges[t].append((i, i + count))
    i += count

population.create_dataset("source_node_id", data=source)
population.create_dataset("target_node_id", data=target)
population.create_dataset("edge_group_id", data=numpy.zeros((edge_count)))
population.create_dataset("edge_group_index", data=range(0, edge_count))

edge_group = population.create_group("0") # Left empty on purpose

indices = population.create_group("indices")

def create_index(ranges, group):
    node_id_to_range = numpy.zeros((5, 2), dtype="u8")
    range_to_edge_id = numpy.zeros((len(connections), 2), dtype="u8")
    j = 0
    for i, node_ranges in enumerate(ranges):
        if len(node_ranges) == 0:
            node_id_to_range[i] = [-1, -1]
        else:
            node_id_to_range[i] = [j, j + len(node_ranges)]
            for s, e in node_ranges:
                range_to_edge_id[j] = [s, e]
                j += 1
    group.create_dataset("node_id_to_range", data=node_id_to_range)
    group.create_dataset("range_to_edge_id", data=range_to_edge_id)

source_to_target = indices.create_group("source_to_target")
create_index(pre_ranges, source_to_target)

target_to_source = indices.create_group("target_to_source")
create_index(post_ranges, target_to_source)
