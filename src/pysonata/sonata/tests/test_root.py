import os
import pytest
import h5py
import numpy as np

from sonata.io import File


@pytest.fixture
def thalamocortical():
    return File(data_files=['examples/v1_nodes.h5', 'examples/lgn_nodes.h5', 'examples/v1_v1_edges.h5'],
                data_type_files=['examples/lgn_node_types.csv', 'examples/v1_node_types.csv',
                                 'examples/v1_v1_edge_types.csv'])


def test_save_gids(thalamocortical):
    if os.path.exists('tmp/gid_table.h5'):
        os.remove('tmp/gid_table.h5')

    assert(thalamocortical.nodes.has_gids == False)
    thalamocortical.nodes.generate_gids(file_name='tmp/gid_table.h5')
    assert(os.path.exists('tmp/gid_table.h5'))

    gid_h5 = h5py.File('tmp/gid_table.h5', mode='r')
    assert('gid' in gid_h5)
    assert(len(gid_h5['gid']) == 9449)
    assert(np.issubdtype(gid_h5['gid'].dtype, np.uint))

    assert('node_id' in gid_h5)
    assert(len(gid_h5['node_id']) == 9449)
    assert(np.issubdtype(gid_h5['node_id'].dtype, np.uint))

    assert('population' in gid_h5)
    assert(len(gid_h5['population']) == 9449)
    assert(np.issubdtype(gid_h5['population'].dtype, object))
    assert(set(np.unique(gid_h5['population'][...])) == set([0, 1]))
    assert(set(np.unique(gid_h5['population_names'][...])) == set(['v1', 'lgn']))


def test_nodes(thalamocortical):
    nodes = thalamocortical.nodes
    assert(nodes.root_name == 'nodes')
    assert(set(nodes.population_names) == set(['lgn', 'v1']))
    assert('v1' in nodes)
    assert('lgn' in nodes)
    assert(nodes['v1'].name == 'v1')
    assert(nodes['lgn'].name == 'lgn')


def test_edges(thalamocortical):
    edges = thalamocortical.edges
    assert(edges.root_name == 'edges')
    assert(len(edges.population_names) == 1)
    assert(edges['v1_to_v1'].name == 'v1_to_v1')
    assert(len(edges.get_populations(source='v1')) == 1)
    assert(len(edges.get_populations(source='v1', target='lgn')) == 0)
    assert(len(edges.get_populations(source='v1', target='v1')) == 1)


if __name__ == '__main__':
    test_save_gids(thalamocortical())
    test_nodes(thalamocortical())
    test_edges(thalamocortical())