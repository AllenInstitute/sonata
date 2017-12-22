import h5py
import numpy
from itertools import groupby

def _compute_list_mapping(from_list, to_list):

    if (len(to_list) == 1):
        index = numpy.searchsorted(from_list, to_list[0:1])
        if from_list[index[0]] != to_list[0]:
            raise ValueError("Invalid GID: %d" % to_list[0])
        return index

    """Given two numpy arrays of sortable items, finds the array of indices
    such as from_list[indices] == to_list"""
    sorting_indices1 = numpy.argsort(from_list)
    sorting_indices2 = numpy.argsort(to_list)
    positions = numpy.searchsorted(from_list[sorting_indices1],
                                   to_list[sorting_indices2])
    # numpy.argsort(sorting_indices2) gives the indices to access positions
    # in the original order of gids. Using this resorted indices to access
    # sorting_indices1 gives the indices of gids in report.gids.
    indices = sorting_indices1[positions[numpy.argsort(sorting_indices2)]]

    matches = from_list[indices] == to_list
    if not all(matches):
        raise ValueError("Invalid GIDs: " +
                         str(to_list[numpy.logical_not(matches)]))

    return indices

def _compute_block_range(frame_range, frames_per_block):
    def frame_block(frame):
        return frame // frames_per_block
    return range(frame_block(frame_range[0]),
                 frame_block(frame_range[1] - 1) + 1)

class _BaseView(object):
    def __init__(self, report, gids, full_frame):

        self._report = report
        self._full_frame = full_frame

        indices = _compute_list_mapping(report.gids, gids)

        class ReportOrderInfo: pass
        self._report_order = ReportOrderInfo()
        ro = self._report_order

        # During report to memory data transfer we want to proceed in the
        # order in which cells are listed in the report. The following arrays
        # are used for this purpose
        sorting_indices = numpy.argsort(indices)
        in_report_indices = indices[sorting_indices]
        ro.in_report_indices = in_report_indices

        num_values = report._num_values
        ro.num_values = num_values[in_report_indices]
        ro.out_offsets = numpy.zeros(len(gids) + 1, dtype="u4")
        ro.out_offsets[1:] = numpy.cumsum(ro.num_values)
        frame_size = ro.out_offsets[-1]

        # Creating the mapping
        # reordering ro.out_offsets and ro.num_values so they are in the order
        # of the gid list passed at report construction.
        class Mapping: pass
        self.mapping = Mapping()
        self.mapping.num_values = num_values[indices]
        # The offsets are ro.out_offsets in view order instead of report
        # order
        report_order_to_view_order = numpy.argsort(sorting_indices)
        self.mapping.offsets = ro.out_offsets[report_order_to_view_order]

        in_mapping = report._mapping_data

        if full_frame:
            self.mapping.data = in_mapping
        else:
            in_offsets = report._accum_values[in_report_indices]
            out_mapping = numpy.zeros((frame_size), dtype="u4")
            for in_offset, out_offset, values in zip(
                    in_offsets, ro.out_offsets, ro.num_values):
                out_mapping[out_offset:out_offset + values] = \
                    in_mapping[in_offset:in_offset + values]
            self.mapping.data = out_mapping

class _SimpleView(_BaseView):
    def __init__(self, report, gids, full_frame):

        super(_SimpleView, self).__init__(report, gids, full_frame)

        self._data = report._file["data"]

        ro = self._report_order
        ro.in_offsets = report._accum_values[ro.in_report_indices]

    def load(self, frame_range):

        frame_count = frame_range[1] - frame_range[0]

        if self._full_frame:
            # We expect this copy to be as efficient as possible
            return numpy.array(self._data[frame_range[0]:frame_range[1]][:])

        ro = self._report_order
        output = numpy.zeros((frame_count, ro.out_offsets[-1]), dtype="f4")

        # Even if we code load a whole trace for each cell (and the code
        # would be simpler), we will load in blocks of frames aligned with
        # with the chunk size.
        data = self._data
        frames_per_block = data.chunks[0]

        block_range = _compute_block_range(frame_range, frames_per_block)

        # Exception for the single-cell case
        if ro.num_values.shape[0] == 1:
            return numpy.array(
                data[frame_range[0]:frame_range[1],
                     ro.in_offsets[0]:ro.in_offsets[0] + ro.num_values[0]])

        for block in block_range:

            start = max(frame_range[0], block * frames_per_block)
            end = min(frame_range[1], (block + 1) * frames_per_block)
            count = end - start
            out_index = start - frame_range[0]

            if self._full_frame:
                output[out_index, out_index + count][:] = \
                    self._data[start:end][:]
            else:
                for in_off, out_off, n in zip(
                    ro.in_offsets, ro.out_offsets, ro.num_values):
                   output[out_index:out_index + count, out_off:out_off + n] = \
                        data[start:end, in_off:in_off + n]

        return output


    def load_frame(self, frame_number):

        data = self._data

        if self._full_frame:
            out = numpy.array(data[frame_number][:])
            # Reshaping to be 2D.
            return numpy.reshape(out, (1, out.shape[0]))

        ro = self._report_order
        output = numpy.zeros((1, ro.out_offsets[-1]), dtype="f4")

        for in_offset, out_offset, values in zip(
                ro.in_offsets, ro.out_offsets, ro.num_values):
            output[0][out_offset:out_offset + values] = \
                data[frame_number][in_offset:in_offset + values]

        return output

class _BlockBasedView(_BaseView):
    def __init__(self, report, gids, full_frame):

        super(_BlockBasedView, self).__init__(report, gids, full_frame)

        ro = self._report_order

        data_offsets = numpy.array(report._data_offsets)
        ro.in_offsets = data_offsets[ro.in_report_indices]

        chunk_ids = numpy.array(report._chunk_ids)[ro.in_report_indices]
        # chunk ids are supposed to be sorted in the report
        ro.chunks = numpy.unique(chunk_ids)
        ro.chunk_sizes = numpy.array(report._chunk_sizes)[ro.chunks]
        # chunk_index_range[i], chunk_index_range[i+1] is the range of
        # cell indices for the chunk i
        ro.chunk_index_range = numpy.zeros((ro.chunks.shape[0] + 1), dtype="u4")
        ro.chunk_index_range[1:] = numpy.cumsum(
            [len(list(g)) for k, g in groupby(chunk_ids)])

    def load(self, frame_range):

        chunks_per_frame = len(self._report._chunk_sizes)
        frames_per_block = self._report._frames_per_block

        def frame_block(frame):
            return frame // frames_per_block

        # Reading blocks
        block_ids = []
        for i in _compute_block_range(frame_range, frames_per_block):
            for j in self._report_order.chunks:
                block_ids.append(i * chunks_per_frame + j)

        blocks = self._report._cache.load_blocks(block_ids)

        return self._blocks_to_output(blocks, block_ids, frame_range)

    def load_frame(self, frame):

        chunks_per_frame = len(self._report._chunk_sizes)
        frames_per_block = self._report._frames_per_block

        frame_block = frame // frames_per_block

        # Reading blocks
        block_ids = []
        for i in self._report_order.chunks:
            block_ids.append(frame_block * chunks_per_frame + i)
        blocks = self._report._cache.load_blocks(block_ids)

        return self._blocks_to_output(blocks, block_ids, (frame, frame + 1))

    def _blocks_to_output(self, blocks, block_ids, frame_range):
        """Copies the pieces of data corresponding to this view from a list of
        blocks to an output numpy array containing the final result of a load
        operation.
        frame_range is the interval of frames to copy and it's open on the
        right.
        """

        # Allocating the output numpy array
        frame_size = self._report_order.out_offsets[-1]
        output = numpy.zeros((frame_range[1] - frame_range[0], frame_size),
                             dtype="f4")
        total_elements = output.shape[0] * output.shape[1]

        chunks_per_frame = len(self._report._chunk_sizes)
        frames_per_block = self._report._frames_per_block

        # Transfering the data from the blocks to the output array.
        local_chunk_id = 0
        for block_id, block in zip(block_ids, blocks):

            # The first block may not need to be processed completely depending
            # on the first requested frame
            first_frame = max(
                frame_range[0],
                (block_id // chunks_per_frame) * frames_per_block)
            # The same goes for the last block
            last_frame = min((first_frame // frames_per_block + 1) *
                             frames_per_block, frame_range[1])
            frame_count = last_frame - first_frame

            chunk_id = block_id % chunks_per_frame
            # Finding the index of this chunk in the chunk_index_range array
            ro = self._report_order
            if chunk_id < ro.chunks[local_chunk_id]:
                local_chunk_id = 0
            while ro.chunks[local_chunk_id] != chunk_id:
                local_chunk_id += 1

            chunk_size = ro.chunk_sizes[local_chunk_id]
            cell_index_range = (ro.chunk_index_range[local_chunk_id],
                                ro.chunk_index_range[local_chunk_id + 1])

            if self._full_frame:

                out_offset = (ro.out_offsets[cell_index_range[0]] +
                              (first_frame - frame_range[0]) * frame_size)
                in_offset = (first_frame % frames_per_block) * chunk_size

                # Flatten and apply the initial offset for this chunk to output
                out_view = output.reshape((total_elements))[out_offset:]
                if frame_count == 1:
                    out_view[0:chunk_size] = \
                        block[in_offset:in_offset+chunk_size]
                else:
                    # Reshaping the out_view with the strides for this chunk
                    shape = (frame_count, chunk_size)
                    out_view = numpy.lib.stride_tricks.as_strided(
                        out_view, shape=shape, strides=(frame_size * 4, 4))

                    # Shaping the block to be 2D and remove the padding and the
                    # heading frames that may be discarded
                    in_view = numpy.lib.stride_tricks.as_strided(
                        block[in_offset:], shape=shape,
                        strides=(chunk_size * 4, 4))

                    out_view[:] = in_view
            else:

                # Copying cell by cell using a strided view for the frames.
                # This is better than copying frame by frame because:
                # - cell strides are not regular
                # - speeds up single cell traces (for full frames we have the
                #   optimization above)
                for cell_index in range(*cell_index_range):

                    cell_size = ro.num_values[cell_index]

                    out_offset = ro.out_offsets[cell_index] + \
                                 frame_size * (first_frame - frame_range[0])
                    in_offset = ((first_frame % frames_per_block) * chunk_size +
                                 ro.in_offsets[cell_index])

                    # Flatten the out array and apply the initial offset for
                    # this chunk
                    out_view = output.reshape(
                        (total_elements))[int(out_offset):]

                    if frame_count == 1:
                        out_view[0:cell_size] = \
                            block[in_offset:in_offset+cell_size]
                    else:
                        # Reshaping the out_view with the strides for this cell
                        shape = (frame_count, cell_size)
                        out_view = numpy.lib.stride_tricks.as_strided(
                            out_view, shape=shape, strides=(frame_size * 4, 4))
                        # Shaping the block to be 2D and select the portions for
                        # this cells
                        in_view = numpy.lib.stride_tricks.as_strided(
                            block[in_offset:], shape=shape,
                            strides=(chunk_size * 4, 4))

                        out_view[:] = in_view

        return output

class View:
    def __init__(self, report, gids):

        self._report = report

        if gids is None:
            self.gids = self._report.gids
            full_frame = True
        else:
            if type(gids) != list and type(gids) != numpy.ndarray:
                raise ValueError("Invalid gid specification")

            self.gids = numpy.array(gids, dtype="u4")
            full_frame = False

        if report._block_based:
            self._impl = _BlockBasedView(report, self.gids, full_frame)
        else:
            self._impl = _SimpleView(report, self.gids, full_frame)
        self.mapping = self._impl.mapping

    def load(self, start, end = None):

        metadata = self._report.metadata
        start_time = metadata["start_time"]
        time_step = metadata["time_step"]

        if end is None:

            frame = self._get_frame_number(start)
            timestamp = start_time + time_step * frame
            data = self._impl.load_frame(frame)
            return (numpy.array([timestamp]), data)

        start = max(start_time, start)
        end_time = metadata["end_time"]
        end = numpy.nextafter(min(end_time, end), -float("inf"))


        first_frame = self._get_frame_number(start)
        frame_count = self._get_frame_number(end) - first_frame + 1
        frame_range = (first_frame, first_frame + frame_count)

        data = self._impl.load(frame_range)

        # Creating the array of timestamps
        start_time = first_frame * time_step + start_time
        stamps = numpy.arange(
            # The subtraction of half a time_step avoids rounding errors
            start_time, start_time + (frame_count - 0.5) * time_step, time_step)

        return (stamps, data)

    def load_all(self):

        metadata = self._report.metadata
        frame_count = metadata["frame_count"]

        frames = self._impl.load((0, frame_count))

        # Creating the array of timestamps
        start_time = metadata["start_time"]
        time_step = metadata["time_step"]
        stamps = numpy.arange(start_time, start_time + frame_count * time_step,
                              time_step)

        return (stamps, frames)

    def _get_frame_number(self, timestamp):

        metadata = self._report.metadata

        start_time = metadata["start_time"]
        end_time = metadata["end_time"]
        time_step = metadata["time_step"]

        timestamp = max(min(timestamp,
                            numpy.nextafter(end_time, -float("inf"))),
                        start_time) - start_time
        return int(timestamp / time_step)

class Report:

    class Cache:
        def __init__(self, data, cache_size=5471):
            self._data = data

            self._cache_size = cache_size
            self._block_cache = [(-1, None)] * cache_size

        def load_blocks(self, ids):

            blocks = []
            for i in ids:
                index = i % self._cache_size
                entry = self._block_cache[index]
                if entry[0] == i:
                    block = entry[1]
                else:
                    block = self._data[i,:]
                    self._block_cache[index] = (i, block)
                blocks.append(block)

            return blocks

    def __init__(self, name):
        self._file = h5py.File(name, "r")
        attrs = self._file.attrs
        mapping = self._file["mapping"]
        self._mapping = mapping

        self.gids = numpy.array(mapping["gids"])
        self.metadata = {"cell_count": len(self.gids)}
        self.metadata["data_unit"] = attrs["data_unit"]
        self.metadata["time_unit"] = attrs["time_unit"]
        time_step = attrs["time_step"]
        self.metadata["time_step"] = time_step
        frame_count = attrs["frame_count"]
        self.metadata["frame_count"] = frame_count
        start_time = attrs["start_time"]
        self.metadata["start_time"] = start_time
        self.metadata["end_time"] = start_time + frame_count * time_step

        self._block_based = "frames_per_block" in mapping.attrs

        self.__mapping_data = None
        self.__num_values = None
        self.__accum_values = None

        if self._block_based:
            self._parse_block_based_mapping(mapping)
            self._cache = self.Cache(self._file["data"])

    @property
    def _mapping_data(self):
        if self.__mapping_data is None:
            self.__mapping_data = numpy.array(self._mapping["data"])
        return self.__mapping_data

    @property
    def _num_values(self):
        if self.__num_values is None:
            self.__num_values = numpy.array(self._mapping["num_values"])
        return self.__num_values

    @property
    def _accum_values(self):
        if self.__accum_values is None:
            num_values = self._num_values
            accum_values = numpy.zeros(num_values.shape, dtype="u4")
            accum_values[1:] = numpy.cumsum(num_values[:-1], dtype="u4")
            accum_values[0] = 0
            self.__accum_values = accum_values
        return self.__accum_values

    def _parse_block_based_mapping(self, mapping):

        self._frames_per_block = mapping.attrs["frames_per_block"]
        self._chunk_ids = mapping["chunks"]
        self._mapping_offsets = numpy.cumsum(self._num_values)

        # Computing the size of each chunk and the data offset of each cell
        cells_per_chunk = numpy.bincount(self._chunk_ids)
        cum_cells = numpy.zeros((cells_per_chunk.shape[0] + 1), dtype="u4")
        cum_cells[1:] = numpy.cumsum(cells_per_chunk, dtype="u4")
        # cum_values gives the offsets as if all cells belonged to the same
        # chunk
        cum_values = numpy.zeros((self._num_values.shape[0] + 1), dtype="u4")
        cum_values[1:] = numpy.cumsum(self._num_values, dtype="u8")
        # Using the prefix sum of per chunk cell counts we can obtain the chunk
        # sizes
        self._chunk_sizes = (cum_values[cum_cells[1:]] -
                             cum_values[cum_cells[:-1]])
        # Each offset needs is then subtracted the accumulated sum of the chunk
        # sizes of all chunks previous to the chunk the cells belongs to.
        cum_chunk_sizes = numpy.zeros((self._chunk_sizes.shape[0]), dtype="u4")
        cum_chunk_sizes[1:] = numpy.cumsum(self._chunk_sizes[:-1], dtype="u4")
        self._data_offsets = cum_values[:-1] - cum_chunk_sizes[self._chunk_ids]
        self.metadata["value_count"] = self._mapping_offsets[-1]

    def create_view(self, gids=None):
        return View(self, gids)
