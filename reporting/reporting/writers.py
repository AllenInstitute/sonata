from __future__ import print_function

import argparse
import brain
import h5py
import math
import numpy
import sys

def compute_frames_per_block(cells_to_frames_ratio, report, block_values,
                             gids=None):

    # The number of frames per block is fixed using the median number of
    # compartments per cell, the expected block size and the cells to frames
    # ratio. Chunks are later guaranteed to not exceed the size of a block.
    if gids is None:
        gids = report.gids

    view = report.create_view(gids)
    mapping = view.mapping
    counts = numpy.zeros((len(gids)), dtype="u4")
    for i in range(len(gids)):
        counts[i] = mapping.num_compartments(i)
    total_compartments = numpy.sum(counts)
    median_num_compartments = numpy.median(counts, overwrite_input=True)

    even = math.sqrt(block_values / median_num_compartments)
    frames = int(math.floor(even / cells_to_frames_ratio))
    # Exceptionally, if the number of frames choosen doesn't fill properly
    # a block for the total number of compartments, we increase the number
    # of frames to the maximum possible
    if (frames * total_compartments - 1) < block_values:
        frames = int(math.floor(block_values / total_compartments))

    return max(1, frames)


def write_common_mapping(gids, mapping, output):

    cell_count = len(gids)
    counts_per_cell = mapping.num_compartments

    out_mapping = output.create_group("mapping")

    out_mapping.create_dataset("gids", data=gids, dtype="u4")

    # Number of values per cell
    num_values = numpy.zeros((cell_count), dtype="u4")
    for i in range(cell_count):
        num_values[i] = counts_per_cell(i)
    out_mapping.create_dataset("num_values", data=num_values, dtype="u4")

    # Per cell mapping data
    index = mapping.index
    mapping_data = index.view(dtype="u4").reshape((index.shape[0], 2))[:, 1]
    out_mapping.create_dataset("data", data=mapping_data, dtype="u4")

    return out_mapping

def write_h5_chunked(report, output, options, gids=None):

    if gids is None:
        gids = report.gids
    view = report.create_view(gids)

    write_common_mapping(gids, view.mapping, output)

    frame_count = output.attrs["frame_count"]
    start_time = output.attrs["start_time"]
    time_step = output.attrs["time_step"]
    total_values = view.mapping.frame_size

    block_values = options.block_size / 4 # sizeof(float)
    frames_per_block = compute_frames_per_block(options.cells_to_frames, report,
                                                block_values, gids)

    h5_chunk_shape = (frames_per_block, block_values / frames_per_block)

    out_data = output.create_dataset("data", (frame_count, total_values),
                                     chunks=h5_chunk_shape, dtype="f4")

    print("  0%", end="")
    sys.stdout.flush()

    for i in range(0, frame_count, frames_per_block):

        time_window = (start_time + (i + 0.5) * time_step,
                       start_time + (i + frames_per_block - 0.49) * time_step)

        frames = view.load(*time_window)[1]
        out_data[i:min(i + frames_per_block, out_data.shape[0]), :] = frames
        print("\b\b\b\b%3d%%" %
              min(100, int((i + frames_per_block) / frame_count * 100)),
              end="")
        sys.stdout.flush()
    print()

def write_explicit_blocks(report, output, options, gids=None):

    if gids is None:
        gids = report.gids
    metadata = report.metadata
    view = report.create_view(gids)

    block_values = options.block_size / 4 # sizeof(float)
    frames_per_block = compute_frames_per_block(options.cells_to_frames, report,
                                                block_values, gids)

    # Mapping
    mapping = view.mapping

    counts_per_cell = mapping.num_compartments
    offsets = mapping.offsets
    cell_count = len(gids)
    frame_count = output.attrs["frame_count"]

    out_mapping = write_common_mapping(gids, mapping, output)

    out_mapping.attrs["frames_per_block"] = frames_per_block

    # Finding cell ranges for each chunk
    values_in_chunk = 0
    first_cell = 0
    chunks = []
    for i in range(len(gids)):
        nvalues = counts_per_cell(i)
        if nvalues * frames_per_block > block_values:
            print("Block size too small for the next chunk.")
            print("Increase the block size or the cells_to_frames ratio.")
            exit(-1)

        if (values_in_chunk + nvalues) * frames_per_block > block_values:
            chunks.append((first_cell, values_in_chunk))
            values_in_chunk = nvalues
            first_cell = i
        else:
            values_in_chunk += nvalues

    if values_in_chunk * frames_per_block > block_values:
        print("Block size too small for the next chunk.")
        print("Increase the block size or the cells_to_frames ratio.")
        exit(-1)
    chunks.append((first_cell, values_in_chunk))

    utilizations = numpy.zeros((len(chunks)), dtype="f4")

    chunk_ids = numpy.zeros((cell_count), dtype="u4")
    chunk_sizes = numpy.zeros((len(chunks)), dtype="u4")
    accum_cells = numpy.zeros((len(chunks)), dtype="u4")
    for i in range(len(chunks) - 1):
        first = chunks[i][0]
        last = chunks[i+1][0]
        accum_cells[i] = (last - first)
        chunk_ids[first:last] = [i] * (last - first)
        chunk_sizes[i] = chunks[i][1]
    accum_cells[-1] = (cell_count - chunks[-1][0])
    chunk_ids[chunks[-1][0]:] = [len(chunks) - 1] * (cell_count - chunks[-1][0])
    chunk_sizes[len(chunks) - 1] = chunks[-1][1]
    average_cells_per_chunk = accum_cells.mean()
    accum_cells = numpy.cumsum(accum_cells)

    # Per cell chunk id
    out_mapping.create_dataset("chunks", data=chunk_ids, dtype="u4")

    # Computing the total number of chunks necessary for the report and creating
    # the dataset.
    total_blocks = len(chunks) * int((frame_count + frames_per_block - 1) /
                                     frames_per_block)
    full_blocks = frame_count // frames_per_block
    spare_frames = frame_count - full_blocks * frames_per_block

    out_data = output.create_dataset("data", (total_blocks, block_values),
                                     dtype="f4")

    start_time = metadata["start_time"]
    time_step = metadata["time_step"]

    for chunk_index, chunk_size in enumerate(chunk_sizes):

        mean_chunk_utilization = (chunk_size * frames_per_block) / block_values
        utilization = mean_chunk_utilization * full_blocks
        if spare_frames != 0:
            utilization += (chunk_size * spare_frames ) / block_values
            utilization /= full_blocks + 1
        else:
            utilization /= full_blocks
        utilizations[chunk_index] = utilization
    print("Block size: %0.2f KB" % (options.block_size / 1024.0), end="")
    print(", total blocks: %d" % total_blocks)
    print("Frames/block", frames_per_block, "\b, mean cells/chunk %.1f" %
          average_cells_per_chunk)
    print("Utilization: %f" % numpy.mean(utilizations))

    if options.read_full_frames:
        view = report.create_view()

        # Computing the offset of each cell within the frame, this code assumes
        # that GIDs are in order inside a frame, which in principle is
        # guaranteed by the binary report.
        num_values = numpy.zeros((cell_count + 1), dtype="u4")
        for i in range(cell_count):
            num_values[i + 1] = counts_per_cell(i)
        in_offsets = numpy.cumsum(num_values)

        cell_index = 0

    for i in range(0, frame_count, frames_per_block):

        time_window = (start_time + (i + 0.5) * time_step,
                       start_time + (i + frames_per_block - 0.49) * time_step)

        print("Frames %d to %d:   0%%" %
              (i, min(frame_count, i + frames_per_block - 1)), end="")
        sys.stdout.flush()

        if options.read_full_frames:
            frames = view.load(*time_window)[1]

        for chunk_index, chunk_size in enumerate(chunk_sizes):

            if not options.read_full_frames:
                view = report.create_view(gids[chunk_ids == chunk_index])
                frames = view.load(*time_window)[1]

            if options.read_full_frames:
                start = in_offsets[cell_index]
                # Getting the index of the first cell of the next chunk
                cell_index = int(accum_cells[chunk_index])
                end = in_offsets[cell_index - 1] + \
                      mapping.num_compartments(cell_index - 1)

            block = numpy.zeros((block_values))
            for j, frame in enumerate(frames):
                if options.read_full_frames:
                    block[j * chunk_size:(j+1) * chunk_size] = frame[start:end]
                else:
                    block[j * chunk_size:(j+1) * chunk_size] = frame

            block_number = (i // frames_per_block) * len(chunks) + chunk_index
            out_data[block_number] = block

            print("\b\b\b\b%3d%%" % int((chunk_index + 1) /
                                        len(chunk_sizes) * 100),
                  end="")
            sys.stdout.flush()
        print()
        cell_index = 0

class ParseSize(argparse.Action):
    def __init__(self, *args, **kwargs):
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option):

        value = values[0]
        multiplier = 1
        for s, x in [("M", 2), ("K", 1), ("B", 0)]:
            if value[-1] == s:
                multiplier = 1024 ** x
                value = value[:-1]
        try:
            value = int(value) * multiplier
        except:
            raise argparse.ArgumentError(self, "Error parsing size")

        setattr(namespace, self.dest, value)

def main():


    args_parser = argparse.ArgumentParser(
        usage="bbp2h5 report [-o filename] [options]",
        description="Binary to new h5 report converter")

    args_parser.add_argument(
        "report", type=str, help=".bbp binary report")
    args_parser.add_argument(
        "--out", "-o", type=str, metavar="filename", help="output file name",
        default="out.h5")
    args_parser.add_argument(
        "--block-size", "-b", action=ParseSize, metavar="size[B,K,M]", nargs=1,
        help="block size in bytes, KiB or MiB",  default=1024 ** 2)
    args_parser.add_argument(
        "--cells-to-frames", "-r", type=float, metavar="ratio",
        help="average fraction of cells per block compared to frames",
        default=0.25)
    args_parser.add_argument(
        "--read-full-frames", help="read full frames during conversion",
        action="store_true", default=False)
    args_parser.add_argument(
        "--use-chunking", help="Use hdf5 chunking instead of explicit one",
        action="store_true", default=False)
    args_parser.add_argument(
        "--frame-range", help="Frame range to be converted (default=all)",
        default=None, type=int, nargs=2)
    args_parser.add_argument(
        "--fraction", help="Random fraction of the cells to be selected",
        default=1, type=float)

    try:
        options = args_parser.parse_args(sys.argv[1:])
    except Exception as exc:
        print(exc)
        return -1

    report = brain.CompartmentReport(options.report)
    metadata = report.metadata

    output = h5py.File(options.out, "w")

    output.attrs["version"] = "0.0"
    start_time = metadata["start_time"]
    time_step = metadata["time_step"]
    frame_count = metadata["frame_count"]
    output.attrs["time_step"] = time_step
    output.attrs["data_unit"] = metadata["data_unit"]
    output.attrs["time_unit"] = metadata["time_unit"]

    if options.frame_range is not None:
        assert(options.frame_range[0] >= 0)
        assert(options.frame_range[1] > options.frame_range[0])
        start_time = start_time + options.frame_range[0] * time_step
        frame_count = options.frame_range[1] - options.frame_range[0]

    output.attrs["start_time"] = start_time
    output.attrs["frame_count"] = frame_count

    gids = None
    if options.fraction != 1:
        gids = numpy.array(report.gids)
        numpy.random.seed(5)
        numpy.random.shuffle(gids)
        gids = gids[0:int(len(gids) * options.fraction)]
        gids.sort() # gids need to be sorted
        print("Picking %d cells from %d" % (len(gids), len(report.gids)))
        options.read_full_frames = False

    if options.use_chunking:
        write_h5_chunked(report, output, options, gids)
    else:
        write_explicit_blocks(report, output, options, gids)

    output.close()
    return 0
