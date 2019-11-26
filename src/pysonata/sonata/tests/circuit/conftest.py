import os
import pytest
from six import string_types

from sonata.circuit.file import File


def _append_fdir(files):
    fdir = os.path.dirname(os.path.realpath(__file__))
    if isinstance(files, string_types):
        return os.path.join(fdir, files)
    else:
        return [os.path.join(fdir, f) for f in files]


@pytest.fixture
def net():
    return File(data_files=_append_fdir(['examples/v1_nodes.h5', 'examples/lgn_nodes.h5', 'examples/v1_v1_edges.h5']),
                data_type_files=_append_fdir(['examples/lgn_node_types.csv', 'examples/v1_node_types.csv',
                                              'examples/v1_v1_edge_types.csv']))


@pytest.fixture
def thalamocortical():
    return File(data_files=_append_fdir(['examples/v1_nodes.h5', 'examples/lgn_nodes.h5', 'examples/v1_v1_edges.h5']),
                data_type_files=_append_fdir(['examples/lgn_node_types.csv', 'examples/v1_node_types.csv',
                                              'examples/v1_v1_edge_types.csv']))


def load_circuit_files(data_files, data_type_files):
    return File(data_files=_append_fdir(data_files), data_type_files=_append_fdir(data_type_files))