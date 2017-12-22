import h5py
import numpy as np
import math

example = h5py.File("example.h5", "w")

# Attributes
example.attrs["version"] = "0.0"
example.attrs["sim_id"] = "to_be_decided"
example.attrs.create("start_time", 0.0, dtype="f")
example.attrs.create("time_step", 0.5, dtype="f")
example.attrs["data_unit"] = "mV"
example.attrs["time_unit"] = "ms"
# tend can be computed as start + dt * num_frames

# Mapping
mapping = example.create_group("mapping")

# Per cell info arrays: gid, #values, offset (total #values of previous
# cells)
#
# NOTE 1: Another options would be to have a array of structures, but then it's
# more difficult to change the datasize of any type
#
# NOTE 2: Either offset or #values is redundant as offsets are the prefix sum
# of #values.

gids = np.array([1, 2]) # Array of cell gids.
num_values = np.zeros((0)) # Array of #values per cell.
offsets = np.zeros((0)) # Array of cell offsets inside the frame buffer.

mapping_data = np.zeros((0))
# 1D array of cell item ids. This array maps positions in a simulation frame
# to cells and items inside these cells. The array is divided in #cells
# subarrayas, i.e the information for each cell is in a compact range.
# For the ith cell, it's subarray has #values_i values, being each value
# the id of the cell element to which the corresponding position in the frame
# maps.
#
# In multicompartment simulations each cell has several compartments
# per morphological section, thus an item ID is a section ID. In our case,
# sections are contiguous, this means that all compartments of a section appear
# as a single block of section IDs in the cell array."""

# Example values
#
# cell 0: 0 1 1 2 2 2 (section 0, 1 compartment,
#                      section 1, 2 compartment,
#                      section 2, 3 compartment,
#                       total compartments 6)
cell_0_items_ids = [0, 1, 1, 2, 2, 2]
mapping_data = np.append(mapping, cell_0_items_ids)
offsets = np.append(offsets, [0])
num_values = np.append(num_values, len(cell_0_items_ids))

# cell 1: 0 1 3 3 5 5 5 5 (section 0, 1 compartment,
#                          section 1, 1 compartment,
#                          section 3, 2 compartment,
#                          section 5, 4 compartment,
#                          total compartments 8)
cell_1_items_ids = [0, 1, 3, 3, 5, 5, 5, 5]
mapping_data = np.append(mapping_data, cell_1_items_ids)
offsets = np.append(offsets, [num_values[-1]])
num_values = np.append(num_values, len(cell_1_items_ids))

mapping.create_dataset("gids", data=gids, dtype="u4")
mapping.create_dataset("offsets", data=offsets, dtype="u4")
mapping.create_dataset("num_values", data=num_values, dtype="u4")
mapping.create_dataset("data", data=mapping_data, dtype="u4")

# Frames: 2D array, #frames x Sum #values_i
frames = np.array([
    # Frame 0
    [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, # cell 0
     1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7], # cell 1
    # Frame 1
    [0.0, -0.1, -0.2, -0.3, -0.4, -0.5, # cell 0
     -1.0, -1.1, -1.2, -1.3, -1.4, -1.5, -1.6, -1.7]])
example.create_dataset("data", data=frames, dtype="f")

#comp_per_cell = 240
#block_size = 1024 ** 2
#bandwidth = 1024 ** 3 # bytes/s
#
#def single_cell_trace_efficacy(cells_per_chunk, frames_per_chuck):
#    bytes_per_chunk = comp_per_cell * 4 * cells_per_chunk * frames_per_chunk
#    # This is computed assuming that two consecutive chunks never contain
#    # data for the same cells
#    blocks_per_chunk = math.ceil(bytes_per_chunk / block_size)
#    KB_read = blocks_per_chunk * bytes_per_chunk
#    KB_needed = comp_per_cell * 4 * frames_per_chunk
#    return KB_needed / KB_read
#
#def single_frame_efficacy(cells_per_chunk, frames_per_chuck):
#    bytes_per_chunk = comp_per_cell * 4 * cells_per_chunk * frames_per_chunk
#    # This is computed assuming that two consecutive chunks never contain
#    # data for the same frames
#    blocks_per_chunk = math.ceil(bytes_per_chunk / block_size)
#    KB_read = blocks_per_chunk * bytes_per_chunk
#    KB_needed = comp_per_cell * 4 * cells_per_chunk
#    return KB_needed / KB_read
#
#even = int(math.floor(math.sqrt(block_size / (comp_per_cell * 4))))
#even = even - even % 2
#
#for cell_frame_ratio in [0.125, 0.25, 0.5, 1, 2, 4, 8]:
#
#    cells_per_chunk = even * cell_frame_ratio
#    frames_per_chunk = int(math.floor(even / cell_frame_ratio))
#
#    print("Cells/ck %d, frames/ck %d" % (cells_per_chunk, frames_per_chunk))
#    efficacy = single_cell_trace_efficacy(cells_per_chunk, frames_per_chunk)
#    print("\tSingle cell: %.2f MB/s" % (bandwidth * efficacy / (1024 ** 2)))
#    efficacy = single_frame_efficacy(cells_per_chunk, frames_per_chunk)
#    print("\tSingle frame: %.2f MB/s" % (bandwidth * efficacy / (1024 ** 2)))








