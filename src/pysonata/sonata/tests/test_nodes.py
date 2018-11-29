import pytest
import numpy as np
from collections import Counter

from sonata.io import File


@pytest.fixture
def net():
    return File(data_files=['examples/v1_nodes.h5', 'examples/lgn_nodes.h5', 'examples/v1_v1_edges.h5'],
                data_type_files=['examples/lgn_node_types.csv', 'examples/v1_node_types.csv',
                                 'examples/v1_v1_edge_types.csv'],
                gid_table='examples/gid_table.h5')


def test_population_lookup(net):
    """Test searching by index, node_id and gid"""
    nodes = net.nodes
    v1_nodes = nodes['v1']
    assert(len(v1_nodes.node_ids) == 449)
    n1 = v1_nodes.get_row(0)
    assert(n1.node_id == 0)
    assert(n1.gid == 0)
    assert(n1['location'] == 'VisL4')
    assert(n1['tuning_angle'] == 0.0)

    n2 = v1_nodes.get_node_id(432)
    assert(n2.node_id == 432)
    assert(n2.gid == 432)
    assert(n2['location'] == 'VisL4')
    assert('tuning_angle' not in n2)

    n3 = v1_nodes.get_gid(84)
    assert(n3.node_id == 84)
    assert(n3.gid == 84)
    assert(n3['location'] == 'VisL4')
    assert('tuning_angle' in n3)

    lgn_nodes = nodes['lgn']
    n1 = lgn_nodes.get_row(1000)
    n2 = lgn_nodes.get_node_id(1000)
    n3 = lgn_nodes.get_gid(1000)
    assert(n2.node_id == n1.node_id == n3.node_id == 1000)
    assert(n1['positions'][0] == n2['positions'][0] == n3['positions'][0])
    assert(n1['positions'][1] == n2['positions'][1] == n3['positions'][1])


def test_population_itr(net):
    nodes = net.nodes
    node_count = 0
    for i, node in enumerate(nodes['v1']):
        assert(node.gid == i)
        assert(node.node_id == i)
        assert(node['location'] == 'VisL4')
        assert(node['positions'].shape == (3,))
        node_count += 1
    assert(node_count == 449)

    for i, node in enumerate(nodes['lgn']):
        assert(node.gid == i + 449)
        assert(node.node_id == i)
        assert(node['location'] == 'LGN')
        assert(node['positions'].shape == (2,))
        node_count += 1
    assert(node_count == 9449)


def test_node_set(net):
    # Test with normal list
    v1_nodes = net.nodes['v1']
    selected_rows = [1, 2, 3, 395, 396, 397]
    node_set = v1_nodes.get_rows(selected_rows)
    assert(len(node_set) == 6)
    assert(all(node_set.node_ids == [1, 2, 3, 395, 396, 397]))
    assert(all(node_set.gids == [1, 2, 3, 395, 396, 397]))
    assert(all(node_set.node_type_ids == [395830185, 395830185, 395830185, 100000101, 100000101, 100000102]))
    for i, node in enumerate(node_set):
        assert(node.node_id == selected_rows[i])
        assert(node['location'] == 'VisL4')


def test_group(net):
    v1_nodes = net.nodes['v1']
    grp_biophysical = v1_nodes.get_group(0)
    assert(grp_biophysical.group_id == 0)
    assert(not grp_biophysical.has_dynamics_params)
    node_ids = grp_biophysical.node_ids
    assert(len(node_ids) == 382 and node_ids[0] == 0 and node_ids[-1] == 396)
    gids = grp_biophysical.gids
    assert(len(gids) == 382 and gids[0] == 0 and gids[-1] == 396)
    assert (len(grp_biophysical.columns) == 3)
    assert('rotation_angle_zaxis' not in grp_biophysical.columns)
    assert('tuning_angle' in grp_biophysical.columns)
    assert (len(grp_biophysical.all_columns) == 13)
    assert('rotation_angle_zaxis' in grp_biophysical.all_columns)
    node_type_ids = Counter(grp_biophysical.node_type_ids)
    assert(sum(node_type_ids.values()) == 382)
    assert(all([node_type_ids[_id] > 0 for _id in [100000101, 395830185, 314804042, 318808427]]))

    grp_2 = v1_nodes.get_group(1)
    assert(grp_2.group_id == 1)
    assert(len(grp_2) == 67)
    node_ids = grp_2.node_ids
    assert(len(node_ids) == 67 and node_ids[0] == 85)
    assert('tuning_angle' not in grp_2.columns)
    assert('tuning_angle' not in grp_2.all_columns)
    assert('positions' in grp_2.columns)


def test_group_iter(net):
    v1_nodes = net.nodes['v1']
    grp_0 = v1_nodes.get_group(0)
    node_count = 0
    for node in grp_0:
        node_count += 1
        assert('tuning_angle' in node)
    assert(node_count == 382)

    grp_0 = v1_nodes.get_group(1)
    node_count = 0
    for node in grp_0:
        node_count += 1
        assert('tuning_angle' not in node)
    assert(node_count == 67)


def test_group_df(net):
    v1_nodes = net.nodes['v1']
    grp_0 = v1_nodes.get_group(0)
    df = grp_0.to_dataframe()
    assert(df.shape == (382, 18))

    grp_1 = v1_nodes.get_group(1)
    df = grp_1.to_dataframe()
    assert(df.shape == (67, 17))


def test_group_properties(net):
    v1_nodes = net.nodes['v1']
    grp_0 = v1_nodes.get_group(0)
    assert(grp_0.get_values('positions').shape == (382, 3))

    loc_vals = grp_0.get_values('model_template')
    assert(len(loc_vals) == 382)
    assert(loc_vals[0] == 'ctdb:Biophys1.hoc')
    assert(loc_vals[-1] == 'nrn:IntFire1')


def test_group_search(net):
    v1_nodes = net.nodes['v1']
    grp_0 = v1_nodes.get_group(0)
    for node in grp_0.filter(model_template='ctdb:Biophys1.hoc'):
        assert(node['model_template'] == 'ctdb:Biophys1.hoc')

    for node in grp_0.filter(model_template='ctdb:Biophys1.hoc', pop_name='Nr5a1'):
        assert(node.node_type_id == 318808427)

    assert(sum(1 for _ in grp_0.filter(model_template='nrn:IntFire1', pop_name='Nr5a1')) == 0)

    for i, node in enumerate(grp_0.filter(tuning_angle=0.0)):
        assert(node['tuning_angle'] == 0.0)
    assert((i+1) == 4)


if __name__ == '__main__':
    test_population_lookup(net())
    test_population_itr(net())
    test_node_set(net())
    test_group(net())
    test_group_iter(net())
    test_group_df(net())
    test_group_properties(net())
    test_group_search(net())
