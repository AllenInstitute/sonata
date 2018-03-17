import pytest
import numbers
import numpy as np

from sonata.io import File


@pytest.fixture
def net():
    return File(data_files=['examples/v1_nodes.h5', 'examples/lgn_nodes.h5', 'examples/v1_v1_edges.h5'],
                data_type_files=['examples/lgn_node_types.csv', 'examples/v1_node_types.csv',
                                 'examples/v1_v1_edge_types.csv'])


def test_node_types(net):
    node_types = net.nodes.node_types_table
    assert(node_types is not None)
    assert(len(node_types.node_type_ids) == 10)
    assert(len(node_types.columns) == 10)
    assert('ei' in node_types.columns)
    assert(node_types.to_dataframe().shape == (10, 10))
    assert(np.isreal(node_types.column('rotation_angle_zaxis').dtype))

    # check lgn node
    assert(1 in node_types)
    node_type1 = node_types[1]
    assert(node_type1['ei'] == 'e')
    assert(node_type1['model_template'] is None)
    assert(node_type1['node_type_id'] == 1)
    assert(node_type1['location'] == 'LGN')

    # check that row is being cached.
    mem_id = id(node_type1)
    del node_type1
    assert (mem_id == id(node_types[1]))

    # check v1 node
    assert(395830185 in node_types)
    node_type2 = node_types[395830185]
    assert(node_type2['location'] == 'VisL4')


def test_edge_types(net):
    edge_types = net.edges.edge_types_table
    assert(edge_types is not None)
    assert(len(edge_types.edge_type_ids) == 11)
    assert(len(edge_types.columns) == 5)
    assert('template' in edge_types.columns)
    assert('delay' in edge_types.columns)
    assert(edge_types.to_dataframe().shape == (11, 5))
    assert(np.isreal(edge_types.column('delay').dtype))

    assert(1 in edge_types)
    edge_type1 = edge_types[1]
    assert(edge_type1['dynamics_params'] == 'instanteneousInh.json')
    assert(edge_type1['delay'] == 2.0)

    # check that row is being cached.
    mem_id = id(edge_type1)
    del edge_type1
    assert (mem_id == id(edge_types[1]))


if __name__ == '__main__':
    test_node_types(net())
    test_edge_types(net())
