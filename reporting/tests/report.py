import os
import numpy
import setup

from reporting import Report

import unittest

class Common:

    def setUp(self):
        self.report = Report(self.path)

    def test_report_metadata(self):
        assert(self.report.metadata["cell_count"] == 10)
        assert(self.report.metadata["start_time"] == 0)
        assert(self.report.metadata["end_time"] == 1)
        assert(self.report.metadata["time_step"] == 0.1)
        assert(self.report.metadata["frame_count"] == 10)
        assert(self.report.metadata["time_unit"] == "ms")
        assert(self.report.metadata["data_unit"] == "mV")

    def test_report_gids(self):
        gids = [324, 868, 30872, 75457, 82463, 84347, 106208, 118620,
                127768, 215203]
        assert(set(self.report.gids) == set(gids))

    def test_create_view(self):
        view = self.report.create_view()
        view = self.report.create_view([324])
        view = self.report.create_view(numpy.array([868, 324], dtype="u4"))

        with self.assertRaises(ValueError):
            self.report.create_view([1111])
        with self.assertRaises(ValueError):
            self.report.create_view([868, 1111])

    def test_view_gids(self):
        view = self.report.create_view()
        assert(all(view.gids == self.report.gids))

        view = self.report.create_view([75457])
        assert(all(view.gids == [75457]))

        view = self.report.create_view([75457, 30872])
        assert(all(view.gids == [75457, 30872]))

    def test_single_neuron_mapping(self):

        view = self.report.create_view([75457])
        mapping = view.mapping
        assert(mapping.offsets[0] == 0)
        assert(mapping.num_values[0] == 832)
        data = mapping.data
        assert(data[0] == 0)
        assert((data == numpy.sort(data)).all())

    def test_multi_neuron_mapping(self):

        view = self.report.create_view([75457, 82463, 324])
        mapping = view.mapping
        assert((mapping.offsets == [37, 869, 0]).all())
        assert((mapping.num_values == [832, 261, 37]).all())
        assert((mapping.data[mapping.offsets] == 0).all())
        data = mapping.data
        assert(numpy.sum(mapping.num_values) == data.shape[0])
        for offset, size in zip(mapping.offsets, mapping.num_values):
            assert((data[offset:offset+size] ==
                    numpy.sort(data[offset:offset+size])).all())

        view = self.report.create_view([82463, 324, 75457])
        mapping = view.mapping
        assert((mapping.offsets == [869, 0, 37]).all())
        assert((mapping.num_values == [261, 37, 832]).all())
        assert((mapping.data[mapping.offsets] == 0).all())
        data = mapping.data
        assert(numpy.sum(mapping.num_values) == data.shape[0])
        for offset, size in zip(mapping.offsets, mapping.num_values):
            assert((data[offset:offset+size] ==
                    numpy.sort(data[offset:offset+size])).all())

    def test_single_neuron_trace_data(self):

        view = self.report.create_view([75457])
        mapping = view.mapping
        t, f = view.load_all()
        assert(all(t == numpy.arange(0, 1, 0.1)))
        assert(f.shape == (10, 832))
        assert(f.shape[1] == mapping.num_values[0])
        assert(numpy.isclose(f[0][0], -70.80388641))
        assert(numpy.isclose(f[2][0], -70.8115))

    def test_single_neuron_partial_trace(self):

        view = self.report.create_view([75457])
        mapping = view.mapping
        t, f = view.load(0.2, 0.5)
        assert(t.shape[0] == f.shape[0])
        assert(all(t == numpy.arange(0.2, 0.5, 0.1)))
        assert(f.shape == (3, 832))
        assert(f.shape[1] == mapping.num_values[0])

    def test_single_full_frame_read(self):

        view = self.report.create_view()
        mapping = view.mapping
        t, f = view.load(0.2)
        assert(t.shape[0] == f.shape[0])
        assert(all(t == [0.2]))
        assert(f.shape[1] == numpy.sum(mapping.num_values))
        index = view.gids.searchsorted(75457)
        assert(numpy.isclose(f[0][mapping.offsets[index]], -70.8115))

    def test_full_frame_range(self):

        view = self.report.create_view()
        mapping = view.mapping
        t, f = view.load(0.1, 0.3)
        assert(t.shape[0] == f.shape[0])
        assert(all(t == [0.1, 0.2]))
        assert(f.shape[1] == numpy.sum(mapping.num_values))
        index = view.gids.searchsorted(75457)
        assert(numpy.isclose(f[1][mapping.offsets[index]], -70.8115))

    def test_single_partial_frame(self):

        view = self.report.create_view([75457, 82463, 324])
        mapping = view.mapping
        t, f = view.load(0.2)
        assert(t.shape[0] == f.shape[0])
        assert(all(t == [0.2]))
        assert(f.shape[1] == numpy.sum(mapping.num_values))
        # Checking first value of cell 75457
        assert(numpy.isclose(f[0][mapping.offsets[0]], -70.8115))

        view = self.report.create_view([82463, 324, 75457])
        mapping = view.mapping
        t, f = view.load(0.2)
        assert(t.shape[0] == f.shape[0])
        assert(all(t == [0.2]))
        assert(f.shape[1] == numpy.sum(mapping.num_values))
        # Checking first value of cell 75457
        assert(numpy.isclose(f[0][mapping.offsets[2]], -70.8115))

    def test_single_partial_frame_range(self):

        view = self.report.create_view([75457, 82463, 324])
        mapping = view.mapping
        t, f = view.load_all()
        t, f = view.load(0.1, 0.3)
        assert(t.shape[0] == f.shape[0])
        assert(all(t == [0.1, 0.2]))
        assert(f.shape[1] == numpy.sum(mapping.num_values))
        # Checking first value of cell 75457
        assert(numpy.isclose(f[1][mapping.offsets[0]], -70.8115))

        view = self.report.create_view([82463, 324, 75457])
        mapping = view.mapping
        t, f = view.load_all()
        t, f = view.load(0.1, 0.3)
        assert(t.shape[0] == f.shape[0])
        assert(all(t == [0.1, 0.2]))
        assert(f.shape[1] == numpy.sum(mapping.num_values))
        # Checking first value of cell 75457
        assert(numpy.isclose(f[1][mapping.offsets[2]], -70.8115))

class TestBlockBased(Common, unittest.TestCase):

    path = os.path.join(setup.prefix, "tests/data/by_blocks.h5")

class TestChunkedDataset(Common, unittest.TestCase):

    path = os.path.join(setup.prefix, "tests/data/chunked.h5")

if __name__ == '__main__':
    unittest.main()

