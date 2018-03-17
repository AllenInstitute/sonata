import pytest

from sonata.io import File, Edge


@pytest.fixture
def net():
    return File(data_files=['examples/v1_nodes.h5', 'examples/lgn_nodes.h5', 'examples/v1_v1_edges.h5'],
                data_type_files=['examples/lgn_node_types.csv', 'examples/v1_node_types.csv',
                                 'examples/v1_v1_edge_types.csv'],
                gid_table='examples/gid_table.h5')


def test_edge_population(net):
    edges = net.edges['v1_to_v1']
    assert(len(edges) == 48286)
    assert(edges.source_population == 'v1')
    assert(edges.target_population == 'v1')


def test_population_itr_all(net):
    edges = net.edges['v1_to_v1']
    for i, edge in enumerate(edges):
        assert(edge.source_population == 'v1')
    assert((i+1) == 48286)


def test_population_itr_selected(net):
    edges = net.edges['v1_to_v1']
    for i, edge in enumerate(edges.get_target(100)):
        assert(edge.target_node_id == 100)
        assert(edge['delay'] == 2.0)
    assert((i+1) == 107)

    for i, edge in enumerate(edges.get_source(349)):
        assert(edge.source_node_id == 349)
    assert((i+1) == 81)

    for i, edge in enumerate(edges.get_targets([1, 10, 100])):
        assert(edge.target_node_id in [1, 10, 100])
    assert((i+1) == 346)

    for i, edge in enumerate(edges.get_sources(range(250,300))):
        assert(250 <= edge.source_node_id < 300)
    assert((i+1) == 4184)


def test_population_search(net):
    edges = net.edges['v1_to_v1']

    # Search on a group property
    for i, edge in enumerate(edges.filter(nsyns=7)):
        assert(edge['nsyns'] == 7)
    assert((i+1) == 9729)

    # search on an edge_type property
    for i, edge in enumerate(edges.filter(template='Exp2Syn')):
        assert(edge['edge_type_id'] in [0, 2, 4, 5, 7, 8, 9, 10])
        assert(edge['template'] == 'Exp2Syn')
    assert((i+1) == 11852)

    # mixed search
    for i, edge in enumerate(edges.filter(edge_type_id=7, nsyns=4)):
        assert(edge['nsyns'] == 4)
        assert(edge['edge_type_id'] == 7)
    assert((i+1) == 551)


def test_group(net):
    edges = net.edges['v1_to_v1']
    grp0 = edges.get_group(0)
    assert(len(grp0) == len(edges))
    assert(grp0.group_id == 0)
    assert(grp0.columns == ['nsyns'])
    assert(len(grp0.all_columns) == 6)
    assert(len(grp0.get_values('nsyns')) == 48286)


def test_group_itr(net):
    edges = net.edges['v1_to_v1']
    grp0 = edges.get_group(0)
    for i, edge in enumerate(grp0):
        assert(isinstance(edge, Edge))
    assert((i+1) == 48286)


if __name__ == '__main__':
    test_edge_population(net())
    test_population_itr_all(net())
    test_population_itr_selected(net())
    test_population_search(net())
    test_group(net())
    test_group_itr(net())
