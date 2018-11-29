import pytest
import tempfile

from sonata.io import File

def test_load_files():
    # load nodes file
    net = File(data_files='examples/v1_nodes.h5', data_type_files='examples/v1_node_types.csv')
    assert(net.nodes is not None)
    assert(net.has_nodes)
    assert(net.edges is None)
    assert(not net.has_edges)

    # load edges file
    net = File(data_files='examples/v1_v1_edges.h5', data_type_files='examples/v1_v1_edge_types.csv')
    assert(net.nodes is None)
    assert(not net.has_nodes)
    assert(net.edges is not None)
    assert(net.has_edges)

    # load nodes and edges
    net = File(data_files=['examples/v1_nodes.h5', 'examples/v1_v1_edges.h5'],
               data_type_files=['examples/v1_node_types.csv', 'examples/v1_v1_edge_types.csv'])
    assert(net.nodes is not None)
    assert(net.has_nodes)
    assert(net.edges is not None)
    assert(net.has_edges)


def test_version():
    net = File(data_files=['examples/v1_nodes.h5', 'examples/v1_v1_edges.h5'],
               data_type_files=['examples/v1_node_types.csv', 'examples/v1_v1_edge_types.csv'])
    assert(net.version == '0.1')


def test_bad_magic():
    import h5py
    tmp_file, tmp_file_name = tempfile.mkstemp(suffix='.hdf5')
    # no magic
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.create_group('nodes')

    with pytest.raises(Exception):
        File(data_files=tmp_file_name, data_type_files='examples/v1_node_types.csv')

    # bad magic
    with h5py.File(tmp_file_name, 'r+') as h5:
        h5.attrs['magic'] = 0x0A7B

    with pytest.raises(Exception):
        File(data_files=tmp_file_name, data_type_files='examples/v1_node_types.csv')


def test_no_files():
    with pytest.raises(Exception):
        File(data_files=[], data_type_files=[])


def test_no_node_types():
    with pytest.raises(Exception):
        File(data_files='examples/v1_nodes.h5', data_type_files=[])


def test_mixed_files():
    with pytest.raises(Exception):
        File(data_files='examples/v1_nodes.h5', data_type_files='examples/v1_v1_edge_types.csv')
